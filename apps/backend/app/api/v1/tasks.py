"""
Task Management API endpoints
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
import logging

from app.services.task_manager import task_manager, TaskStatus

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/delegate", response_model=dict)
async def delegate_task_to_agent(
    agent_id: int,
    task_data: dict
):
    """
    Delegate a task to a specific agent

    The task will be created in the database and sent to the agent
    via A2A protocol if the agent's endpoint is available
    """
    try:
        task = await task_manager.delegate_task(
            agent_id=agent_id,
            task_data=task_data
        )

        return task

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to delegate task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delegate task: {str(e)}"
        )


@router.get("/{task_id}", response_model=dict)
async def get_task(task_id: str):
    """Get task details by ID"""
    try:
        task = await task_manager.get_task(task_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task: {str(e)}"
        )


@router.get("/", response_model=dict)
async def list_tasks(
    agent_id: Optional[int] = Query(None, description="Filter by agent ID"),
    group_id: Optional[str] = Query(None, description="Filter by group ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List tasks with optional filters"""
    try:
        result = await task_manager.list_tasks(
            agent_id=agent_id,
            group_id=group_id,
            status=status,
            limit=limit,
            offset=offset
        )

        return result

    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tasks: {str(e)}"
        )


@router.put("/{task_id}/status", response_model=dict)
async def update_task_status(
    task_id: str,
    status: str,
    result: Optional[dict] = None,
    error: Optional[str] = None
):
    """
    Update task status

    This endpoint can be called by agents to update their task status
    """
    try:
        # Validate status
        valid_statuses = [
            TaskStatus.PENDING,
            TaskStatus.ASSIGNED,
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED
        ]

        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        success = await task_manager.update_task_status(
            task_id=task_id,
            status=status,
            result=result,
            error=error
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )

        return {"message": "Task status updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task status: {str(e)}"
        )


@router.post("/{task_id}/retry", response_model=dict)
async def retry_task(task_id: str):
    """Retry a failed task"""
    try:
        task = await task_manager.retry_task(task_id)

        return {
            "message": "Task retry initiated",
            "task": task
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to retry task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry task: {str(e)}"
        )


@router.post("/{task_id}/cancel", response_model=dict)
async def cancel_task(task_id: str):
    """Cancel a pending or in-progress task"""
    try:
        success = await task_manager.cancel_task(task_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )

        return {"message": "Task cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}"
        )


@router.get("/agent/{agent_id}/summary", response_model=dict)
async def get_agent_tasks_summary(agent_id: int):
    """Get task summary for a specific agent"""
    try:
        summary = await task_manager.get_agent_tasks_summary(agent_id)

        return summary

    except Exception as e:
        logger.error(f"Failed to get agent tasks summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent tasks summary: {str(e)}"
        )

