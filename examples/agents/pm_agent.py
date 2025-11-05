"""
PM Agent - Project Manager Agent
Automatically searches, forms teams, and delegates tasks
"""

from typing import Dict, List, Optional
import asyncio

from .base_agent import BaseAgent
from utils.logger import (
    log_success, log_error, log_info, log_warning, log_section,
    log_agent_search_results, log_task_delegation
)


class PMAgent(BaseAgent):
    """PM Agent - Responsible for project management and team coordination"""
    
    def __init__(
        self,
        name: str = "PM Agent",
        private_key: str = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
        **kwargs
    ):
        super().__init__(
            name=name,
            description="AI Project Manager specialized in team coordination and task delegation",
            capabilities=["project-management", "team-coordination", "task-planning"],
            private_key=private_key,
            **kwargs
        )
        
        self.team_members: List[Dict] = []
        self.active_tasks: List[str] = []
        self.group_id: Optional[str] = None
    
    async def start_project(self, project_requirements: Dict) -> Dict:
        """
        Start project
        
        Args:
            project_requirements: Project requirements
                {
                    "name": "Todo List App",
                    "description": "...",
                    "required_capabilities": {
                        "frontend": ["react", "typescript", "ui-design"],
                        "backend": ["python", "fastapi", "database"]
                    },
                    "deadline": "2025-11-15",
                    "budget": 0.5
                }
        
        Returns:
            Project execution results
        """
        project_name = project_requirements.get("name", "Unnamed Project")
        
        log_section(f"Starting Project: {project_name}")
        log_info(project_requirements.get("description", ""))
        
        try:
            # Step 1: Automatically search for team members
            await self._recruit_team(project_requirements)
            
            # Step 2: Create Group
            await self._create_team_group(project_name, project_requirements)
            
            # Step 3: Delegate tasks
            tasks = await self._delegate_tasks(project_requirements)
            
            # Step 4: Monitor task progress
            results = await self._monitor_tasks(tasks)
            
            # Step 5: Evaluate team members
            await self._evaluate_team(results)
            
            log_success("🎉 Project Completed!")
            
            return {
                "project_name": project_name,
                "team_members": self.team_members,
                "tasks": tasks,
                "results": results
            }
            
        except Exception as e:
            log_error(f"Project execution failed: {project_name}", e)
            raise
    
    async def _recruit_team(self, requirements: Dict):
        """Step 1: Automatically search and recruit team members"""
        log_section("Step 1: Automatically Search for Team Members")
        
        required_caps = requirements.get("required_capabilities", {})
        min_reputation = requirements.get("min_reputation", 4.0)
        
        for role, capabilities in required_caps.items():
            log_info(f"🔍 Searching for {role.upper()} Developer...")
            log_info(f"   Required Capabilities: {', '.join(capabilities)}")
            log_info(f"   Minimum Reputation: {min_reputation} ⭐")
            print()
            
            # Search for Agents
            agents = await self.discover_agents(
                capabilities=capabilities,
                min_reputation=min_reputation,
                sort_by="reputation",
                limit=5
            )
            
            if not agents:
                log_error(f"No qualified {role} developers found")
                continue
            
            # Display search results
            log_agent_search_results(agents)
            
            # Select best candidate (highest reputation)
            best_agent = agents[0]
            self.team_members.append({
                "role": role,
                "agent": best_agent
            })
            
            log_success(
                f"Selected: {best_agent['name']}",
                f"Token ID: {best_agent['token_id']} | Reputation: {best_agent['reputation_score'] / 100:.1f}⭐"
            )
            print()
    
    async def _create_team_group(self, project_name: str, requirements: Dict):
        """Step 2: Create Group"""
        log_section("Step 2: Create Collaboration Group")
        
        member_ids = [member["agent"]["token_id"] for member in self.team_members]
        
        log_info(f"👥 Group Name: {project_name} Team")
        log_info(f"   Team Size: {len(member_ids)}")
        
        for member in self.team_members:
            log_info(f"   - {member['role']}: {member['agent']['name']}")
        
        print()
        
        self.group_id = await self.create_group(
            group_name=f"{project_name} Team",
            description=f"Development team for {project_name}",
            member_agents=member_ids
        )
        
        if self.group_id:
            log_success(f"Group created successfully", f"Group ID: {self.group_id}")
        print()
    
    async def _delegate_tasks(self, requirements: Dict) -> List[Dict]:
        """Step 3: Delegate tasks"""
        log_section("Step 3: Delegate Tasks to Team Members")
        
        tasks = []
        project_name = requirements.get("name", "Project")
        deadline = requirements.get("deadline")
        
        for idx, member in enumerate(self.team_members, 1):
            role = member["role"]
            agent = member["agent"]
            
            log_info(f"📋 Task {idx}/{len(self.team_members)}: {role.upper()} Development")
            log_info(f"   Assigned to: {agent['name']} (Token ID: {agent['token_id']})")
            print()
            
            # Create task based on role
            task_data = self._create_task_data(role, project_name, deadline)
            
            # Display task details
            log_task_delegation(task_data)
            print()
            
            # Delegate task
            task_id = await self.delegate_task(
                agent_id=agent["token_id"],
                task_data=task_data,
                group_id=self.group_id
            )
            
            if task_id:
                tasks.append({
                    "task_id": task_id,
                    "role": role,
                    "agent_id": agent["token_id"],
                    "agent_name": agent["name"],
                    "task_data": task_data
                })
                self.active_tasks.append(task_id)
                log_success(f"Task delegated successfully", f"Task ID: {task_id}")
            
            print()
        
        return tasks
    
    def _create_task_data(self, role: str, project_name: str, deadline: Optional[str]) -> Dict:
        """Create task data based on role"""
        
        if role == "frontend":
            return {
                "title": f"{project_name} - Frontend Development",
                "description": f"""
Develop the frontend interface for {project_name}

Requirements:
- Use React + TypeScript
- Implement full CRUD operations
- Responsive design with mobile support
- Excellent user experience

Deliverables:
- Complete frontend code
- Component documentation
- Deployment guide
""",
                "task_type": "frontend_development",
                "priority": 5,
                "deadline": deadline,
                "metadata": {
                    "tech_stack": ["react", "typescript", "tailwindcss"],
                    "deliverables": ["source_code", "documentation", "deployment_guide"]
                }
            }
        
        elif role == "backend":
            return {
                "title": f"{project_name} - Backend API Development",
                "description": f"""
Develop the backend API for {project_name}

Requirements:
- Use FastAPI + MongoDB
- RESTful API design
- User authentication and authorization
- API documentation (OpenAPI)

Deliverables:
- Complete backend code
- API documentation
- Database design
- Deployment scripts
""",
                "task_type": "backend_development",
                "priority": 5,
                "deadline": deadline,
                "metadata": {
                    "tech_stack": ["fastapi", "mongodb", "pydantic"],
                    "deliverables": ["source_code", "api_docs", "database_schema"]
                }
            }
        
        else:
            return {
                "title": f"{project_name} - {role.title()} Development",
                "description": f"Implement {role} components for {project_name}",
                "task_type": "general",
                "priority": 3,
                "deadline": deadline
            }
    
    async def _monitor_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Step 4: Monitor task progress (simulated)"""
        log_section("Step 4: Monitor Task Progress")
        
        log_info("⏳ Waiting for team to complete tasks...")
        log_info("   (Tasks automatically complete in demo mode)")
        print()
        
        # Simulate task progress
        results = []
        for task in tasks:
            # In production, this would poll task status
            # Now we simulate task completion
            
            await asyncio.sleep(1)  # Simulate work time
            
            # Simulate task completion
            task_result = {
                "task_id": task["task_id"],
                "agent_id": task["agent_id"],
                "agent_name": task["agent_name"],
                "role": task["role"],
                "status": "completed",
                "result": {
                    "deliverables": [
                        f"{task['role']}_source_code.zip",
                        f"{task['role']}_documentation.pdf"
                    ],
                    "quality_score": 95
                }
            }
            
            results.append(task_result)
            
            log_success(
                f"{task['agent_name']} completed task",
                f"Role: {task['role']} | Quality: 95/100"
            )
        
        print()
        log_success("✅ All tasks completed!")
        print()
        
        return results
    
    async def _evaluate_team(self, results: List[Dict]):
        """Step 5: Evaluate team members"""
        log_section("Step 5: Automatically Evaluate Team Members")
        
        for result in results:
            agent_id = result["agent_id"]
            agent_name = result["agent_name"]
            role = result["role"]
            quality_score = result["result"]["quality_score"]
            
            # Calculate rating based on quality score
            rating = min(5.0, quality_score / 20)  # Convert 100-point to 5-star
            
            comment = self._generate_feedback_comment(role, quality_score)
            
            log_info(f"⭐ Evaluating {agent_name} ({role})")
            log_info(f"   Rating: {rating:.1f}/5.0")
            log_info(f"   Comment: {comment}")
            print()
            
            # Submit feedback to blockchain
            try:
                success = await self.submit_feedback(
                    agent_id=agent_id,
                    rating=rating,
                    comment=comment
                )
                if success:
                    log_success("   ✅ Feedback submitted to blockchain")
                else:
                    log_warning("   ⚠️  Feedback submission failed, but continuing demo")
            except Exception as e:
                # In demo mode, on-chain submission failure doesn't stop the flow
                log_warning(f"   ⚠️  On-chain submission failed: {str(e)[:80]}")
                log_info("   ℹ️  Continuing with next steps...")
            
            await asyncio.sleep(0.5)
        
        log_success("✅ Evaluation complete")
    
    def _generate_feedback_comment(self, role: str, quality_score: int) -> str:
        """Generate feedback comment"""
        if quality_score >= 90:
            comments = {
                "frontend": "Excellent frontend implementation, beautiful UI design, high code quality",
                "backend": "Outstanding API design, excellent performance, comprehensive documentation"
            }
        elif quality_score >= 80:
            comments = {
                "frontend": "Good frontend implementation, meets requirements",
                "backend": "Reliable API implementation, complete functionality"
            }
        else:
            comments = {
                "frontend": "Basically meets requirements, room for improvement",
                "backend": "Functionality implemented correctly, suggest performance optimization"
            }
        
        return comments.get(role, "Task completed well")
    
    async def get_project_summary(self) -> Dict:
        """Get project summary"""
        return {
            "team_size": len(self.team_members),
            "active_tasks": len(self.active_tasks),
            "group_id": self.group_id,
            "team_members": [
                {
                    "role": m["role"],
                    "name": m["agent"]["name"],
                    "token_id": m["agent"]["token_id"]
                }
                for m in self.team_members
            ]
        }
