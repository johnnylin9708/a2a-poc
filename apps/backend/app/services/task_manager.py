"""
Task Management Service for tracking agent tasks and workflows
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
import logging

from app.database import get_tasks_collection, get_agents_collection
from app.services.a2a_handler import a2a_handler

logger = logging.getLogger(__name__)


class TaskStatus:
    """Task status constants"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskManagementService:
    """Service for managing tasks and workflows"""

    def __init__(self):
        self._tasks_collection = None
        self._agents_collection = None
        logger.info("✅ Task Management Service initialized")

    @property
    def tasks_collection(self):
        """Lazy loading of tasks collection"""
        if self._tasks_collection is None:
            self._tasks_collection = get_tasks_collection()
        return self._tasks_collection

    @property
    def agents_collection(self):
        """Lazy loading of agents collection"""
        if self._agents_collection is None:
            self._agents_collection = get_agents_collection()
        return self._agents_collection

    async def create_task(
        self,
        agent_id: int,
        task_data: Dict[str, Any],
        group_id: Optional[str] = None,
        priority: int = 1
    ) -> Dict[str, Any]:
        """
        Create a new task

        Args:
            agent_id: Target agent token ID
            task_data: Task details
            group_id: Optional group ID if this is a group task
            priority: Task priority (1-5)

        Returns:
            Created task document
        """
        try:
            # Get agent details
            agent = await self.agents_collection.find_one({"token_id": agent_id})
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")

            task_id = str(uuid.uuid4())
            
            task_doc = {
                "task_id": task_id,
                "agent_id": agent_id,
                "agent_name": agent.get("name", f"Agent #{agent_id}"),
                "group_id": group_id,
                "title": task_data.get("title", "Untitled Task"),
                "description": task_data.get("description", ""),
                "task_type": task_data.get("task_type", "general"),
                "priority": priority,
                "status": TaskStatus.PENDING,
                "task_data": task_data,
                "result": None,
                "error": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "started_at": None,
                "completed_at": None,
                "deadline": task_data.get("deadline"),
                "retry_count": 0,
                "max_retries": task_data.get("max_retries", 3),
                "metadata": task_data.get("metadata", {})
            }

            await self.tasks_collection.insert_one(task_doc)
            
            logger.info(f"✅ Task {task_id} created for agent {agent_id}")
            
            # Remove MongoDB _id
            task_doc.pop("_id", None)
            
            return task_doc

        except Exception as e:
            logger.error(f"❌ Failed to create task: {e}")
            raise

    async def delegate_task(
        self,
        agent_id: int,
        task_data: Dict[str, Any],
        group_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create and delegate task to agent via A2A protocol

        Args:
            agent_id: Target agent token ID
            task_data: Task details
            group_id: Optional group ID

        Returns:
            Task response with delegation status
        """
        try:
            # Create task in database
            task = await self.create_task(agent_id, task_data, group_id)

            # Get agent endpoint
            agent = await self.agents_collection.find_one({"token_id": agent_id})
            
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")

            endpoint = agent.get("endpoint")
            
            if not endpoint:
                raise ValueError(f"Agent {agent_id} has no endpoint configured")

            # Try to delegate via A2A protocol
            try:
                # Check if endpoint is available
                is_available = await a2a_handler.check_endpoint_availability(endpoint)
                
                if not is_available:
                    logger.warning(f"⚠️ Agent {agent_id} endpoint is not available")
                    await self.update_task_status(
                        task["task_id"],
                        TaskStatus.FAILED,
                        error="Agent endpoint is not available"
                    )
                    return task

                # Send task via A2A protocol
                a2a_response = await a2a_handler.send_task(
                    endpoint=endpoint,
                    task={
                        "task_id": task["task_id"],
                        "title": task["title"],
                        "description": task["description"],
                        "task_type": task["task_type"],
                        "priority": task["priority"],
                        "deadline": task["deadline"].isoformat() if task["deadline"] else None,
                        "data": task["task_data"]
                    }
                )

                # Update task status to assigned
                await self.update_task_status(
                    task["task_id"],
                    TaskStatus.ASSIGNED,
                    metadata={"a2a_response": a2a_response}
                )

                logger.info(f"✅ Task {task['task_id']} delegated to agent {agent_id}")

            except Exception as e:
                logger.warning(f"⚠️ Failed to delegate via A2A protocol: {e}")
                # Task is created but not delegated yet
                # Could be retried later

            return task

        except Exception as e:
            logger.error(f"❌ Failed to delegate task: {e}")
            raise

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Update task status

        Args:
            task_id: Task ID
            status: New status
            result: Task result (for completed tasks)
            error: Error message (for failed tasks)
            metadata: Additional metadata

        Returns:
            True if updated successfully
        """
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }

            if result is not None:
                update_data["result"] = result

            if error is not None:
                update_data["error"] = error

            if metadata is not None:
                update_data["metadata"] = metadata

            if status == TaskStatus.IN_PROGRESS and "started_at" not in update_data:
                update_data["started_at"] = datetime.utcnow()

            if status == TaskStatus.COMPLETED:
                update_data["completed_at"] = datetime.utcnow()

            result = await self.tasks_collection.update_one(
                {"task_id": task_id},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"✅ Task {task_id} status updated to {status}")
                
                # Update agent statistics
                await self._update_agent_stats(task_id, status)
                
                return True
            else:
                logger.warning(f"⚠️ Task {task_id} not found or not updated")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to update task status: {e}")
            raise

    async def _update_agent_stats(self, task_id: str, status: str):
        """Update agent statistics based on task status"""
        try:
            task = await self.tasks_collection.find_one({"task_id": task_id})
            
            if not task:
                return

            agent_id = task["agent_id"]

            if status == TaskStatus.COMPLETED:
                await self.agents_collection.update_one(
                    {"token_id": agent_id},
                    {
                        "$inc": {
                            "completed_tasks": 1,
                            "total_tasks": 1
                        }
                    }
                )
            elif status == TaskStatus.FAILED:
                await self.agents_collection.update_one(
                    {"token_id": agent_id},
                    {
                        "$inc": {
                            "failed_tasks": 1,
                            "total_tasks": 1
                        }
                    }
                )

        except Exception as e:
            logger.error(f"❌ Failed to update agent stats: {e}")

    async def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task by ID"""
        try:
            task = await self.tasks_collection.find_one({"task_id": task_id})
            
            if task:
                task.pop("_id", None)
            
            return task

        except Exception as e:
            logger.error(f"❌ Failed to get task: {e}")
            return None

    async def list_tasks(
        self,
        agent_id: Optional[int] = None,
        group_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List tasks with filters

        Args:
            agent_id: Filter by agent ID
            group_id: Filter by group ID
            status: Filter by status
            limit: Max results
            offset: Results offset

        Returns:
            Dict with tasks and pagination info
        """
        try:
            query = {}

            if agent_id is not None:
                query["agent_id"] = agent_id

            if group_id is not None:
                query["group_id"] = group_id

            if status is not None:
                query["status"] = status

            total = await self.tasks_collection.count_documents(query)

            cursor = self.tasks_collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
            tasks = await cursor.to_list(length=limit)

            # Remove MongoDB _id
            for task in tasks:
                task.pop("_id", None)

            return {
                "tasks": tasks,
                "total": total,
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            logger.error(f"❌ Failed to list tasks: {e}")
            raise

    async def retry_task(self, task_id: str) -> Dict[str, Any]:
        """
        Retry a failed task

        Args:
            task_id: Task ID

        Returns:
            Updated task
        """
        try:
            task = await self.get_task(task_id)

            if not task:
                raise ValueError(f"Task {task_id} not found")

            if task["status"] != TaskStatus.FAILED:
                raise ValueError(f"Task {task_id} is not in failed status")

            if task["retry_count"] >= task["max_retries"]:
                raise ValueError(f"Task {task_id} has reached max retries")

            # Increment retry count
            await self.tasks_collection.update_one(
                {"task_id": task_id},
                {
                    "$inc": {"retry_count": 1},
                    "$set": {
                        "status": TaskStatus.PENDING,
                        "error": None,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            # Re-delegate task
            result = await self.delegate_task(
                agent_id=task["agent_id"],
                task_data=task["task_data"],
                group_id=task.get("group_id")
            )

            logger.info(f"✅ Task {task_id} retried")

            return result

        except Exception as e:
            logger.error(f"❌ Failed to retry task: {e}")
            raise

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        try:
            result = await self.update_task_status(
                task_id,
                TaskStatus.CANCELLED
            )

            if result:
                logger.info(f"✅ Task {task_id} cancelled")

            return result

        except Exception as e:
            logger.error(f"❌ Failed to cancel task: {e}")
            raise

    async def get_agent_tasks_summary(self, agent_id: int) -> Dict[str, Any]:
        """Get task summary for an agent"""
        try:
            pipeline = [
                {"$match": {"agent_id": agent_id}},
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1}
                    }
                }
            ]

            cursor = self.tasks_collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)

            summary = {
                "total": 0,
                "pending": 0,
                "assigned": 0,
                "in_progress": 0,
                "completed": 0,
                "failed": 0,
                "cancelled": 0
            }

            for result in results:
                status = result["_id"]
                count = result["count"]
                summary[status] = count
                summary["total"] += count

            return summary

        except Exception as e:
            logger.error(f"❌ Failed to get agent tasks summary: {e}")
            raise


# Create singleton instance
task_manager = TaskManagementService()

