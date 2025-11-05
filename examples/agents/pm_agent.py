"""
PM Agent - Project Manager Agent
自动搜索、组建团队、委派任务
"""

from typing import Dict, List, Optional
import asyncio

from .base_agent import BaseAgent
from utils.logger import (
    log_success, log_error, log_info, log_warning, log_section,
    log_agent_search_results, log_task_delegation
)


class PMAgent(BaseAgent):
    """PM Agent - 负责项目管理和团队协调"""
    
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
        启动项目
        
        Args:
            project_requirements: 项目需求
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
            项目执行结果
        """
        project_name = project_requirements.get("name", "Unnamed Project")
        
        log_section(f"启动项目: {project_name}")
        log_info(project_requirements.get("description", ""))
        
        try:
            # Step 1: 自动搜索团队成员
            await self._recruit_team(project_requirements)
            
            # Step 2: 创建 Group
            await self._create_team_group(project_name, project_requirements)
            
            # Step 3: 分配任务
            tasks = await self._delegate_tasks(project_requirements)
            
            # Step 4: 监控任务进度
            results = await self._monitor_tasks(tasks)
            
            # Step 5: 评价团队成员
            await self._evaluate_team(results)
            
            log_success("🎉 项目完成！")
            
            return {
                "project_name": project_name,
                "team_members": self.team_members,
                "tasks": tasks,
                "results": results
            }
            
        except Exception as e:
            log_error(f"项目执行失败: {project_name}", e)
            raise
    
    async def _recruit_team(self, requirements: Dict):
        """Step 1: 自动搜索并招募团队成员"""
        log_section("Step 1: 自动搜索团队成员")
        
        required_caps = requirements.get("required_capabilities", {})
        min_reputation = requirements.get("min_reputation", 4.0)
        
        for role, capabilities in required_caps.items():
            log_info(f"🔍 搜索 {role.upper()} 开发者...")
            log_info(f"   能力要求: {', '.join(capabilities)}")
            log_info(f"   最低声誉: {min_reputation} ⭐")
            print()
            
            # 搜索 Agents
            agents = await self.discover_agents(
                capabilities=capabilities,
                min_reputation=min_reputation,
                sort_by="reputation",
                limit=5
            )
            
            if not agents:
                log_error(f"未找到符合条件的 {role} 开发者")
                continue
            
            # 显示搜索结果
            log_agent_search_results(agents)
            
            # 选择最佳候选者（声誉最高）
            best_agent = agents[0]
            self.team_members.append({
                "role": role,
                "agent": best_agent
            })
            
            log_success(
                f"已选择: {best_agent['name']}",
                f"Token ID: {best_agent['token_id']} | 声誉: {best_agent['reputation_score'] / 100:.1f}⭐"
            )
            print()
    
    async def _create_team_group(self, project_name: str, requirements: Dict):
        """Step 2: 创建 Group"""
        log_section("Step 2: 创建协作 Group")
        
        member_ids = [member["agent"]["token_id"] for member in self.team_members]
        
        log_info(f"👥 Group 名称: {project_name} Team")
        log_info(f"   成员数量: {len(member_ids)}")
        
        for member in self.team_members:
            log_info(f"   - {member['role']}: {member['agent']['name']}")
        
        print()
        
        self.group_id = await self.create_group(
            group_name=f"{project_name} Team",
            description=f"Development team for {project_name}",
            member_agents=member_ids
        )
        
        if self.group_id:
            log_success(f"Group 创建成功", f"Group ID: {self.group_id}")
        print()
    
    async def _delegate_tasks(self, requirements: Dict) -> List[Dict]:
        """Step 3: 委派任务"""
        log_section("Step 3: 委派任务给团队成员")
        
        tasks = []
        project_name = requirements.get("name", "Project")
        deadline = requirements.get("deadline")
        
        for idx, member in enumerate(self.team_members, 1):
            role = member["role"]
            agent = member["agent"]
            
            log_info(f"📋 任务 {idx}/{len(self.team_members)}: {role.upper()} 开发")
            log_info(f"   分配给: {agent['name']} (Token ID: {agent['token_id']})")
            print()
            
            # 根据角色创建任务
            task_data = self._create_task_data(role, project_name, deadline)
            
            # 显示任务详情
            log_task_delegation(task_data)
            print()
            
            # 委派任务
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
                log_success(f"任务委派成功", f"Task ID: {task_id}")
            
            print()
        
        return tasks
    
    def _create_task_data(self, role: str, project_name: str, deadline: Optional[str]) -> Dict:
        """根据角色创建任务数据"""
        
        if role == "frontend":
            return {
                "title": f"{project_name} - Frontend Development",
                "description": f"""
开发 {project_name} 的前端界面

要求:
- 使用 React + TypeScript
- 实现完整的 CRUD 操作
- 响应式设计，支持移动端
- 良好的用户体验

交付物:
- 完整的前端代码
- 组件文档
- 部署说明
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
开发 {project_name} 的后端 API

要求:
- 使用 FastAPI + MongoDB
- RESTful API 设计
- 用户认证和授权
- API 文档 (OpenAPI)

交付物:
- 完整的后端代码
- API 文档
- 数据库设计
- 部署脚本
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
        """Step 4: 监控任务进度 (模拟)"""
        log_section("Step 4: 监控任务进度")
        
        log_info("⏳ 等待团队完成任务...")
        log_info("   (Demo 中模拟任务自动完成)")
        print()
        
        # 模拟任务进度
        results = []
        for task in tasks:
            # 在实际场景中，这里会轮询任务状态
            # 现在我们模拟任务完成
            
            await asyncio.sleep(1)  # 模拟耗时
            
            # 模拟任务完成
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
                f"{task['agent_name']} 完成任务",
                f"角色: {task['role']} | 质量: 95/100"
            )
        
        print()
        log_success("✅ 所有任务已完成！")
        print()
        
        return results
    
    async def _evaluate_team(self, results: List[Dict]):
        """Step 5: 评价团队成员"""
        log_section("Step 5: 自动评价团队成员")
        
        for result in results:
            agent_id = result["agent_id"]
            agent_name = result["agent_name"]
            role = result["role"]
            quality_score = result["result"]["quality_score"]
            
            # 根据质量分数计算评分
            rating = min(5.0, quality_score / 20)  # 100分制转5星
            
            comment = self._generate_feedback_comment(role, quality_score)
            
            log_info(f"⭐ 评价 {agent_name} ({role})")
            log_info(f"   评分: {rating:.1f}/5.0")
            log_info(f"   评语: {comment}")
            print()
            
            # 提交反馈到区块链
            try:
                success = await self.submit_feedback(
                    agent_id=agent_id,
                    rating=rating,
                    comment=comment
                )
                if success:
                    log_success("   ✅ 反馈已提交到区块链")
                else:
                    log_warning("   ⚠️  反馈提交失败，但继续执行")
            except Exception as e:
                # 在演示中，如果链上提交失败，不中断整个流程
                log_warning(f"   ⚠️  链上提交失败: {str(e)[:80]}")
                log_info("   ℹ️  继续执行后续步骤...")
            
            await asyncio.sleep(0.5)
        
        log_success("✅ 评价完成")
    
    def _generate_feedback_comment(self, role: str, quality_score: int) -> str:
        """生成反馈评语"""
        if quality_score >= 90:
            comments = {
                "frontend": "出色的前端实现，UI 设计精美，代码质量高",
                "backend": "优秀的 API 设计，性能出色，文档完善"
            }
        elif quality_score >= 80:
            comments = {
                "frontend": "良好的前端实现，符合要求",
                "backend": "可靠的 API 实现，功能完整"
            }
        else:
            comments = {
                "frontend": "基本符合要求，有改进空间",
                "backend": "功能实现正确，建议优化性能"
            }
        
        return comments.get(role, "任务完成良好")
    
    async def get_project_summary(self) -> Dict:
        """获取项目摘要"""
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

