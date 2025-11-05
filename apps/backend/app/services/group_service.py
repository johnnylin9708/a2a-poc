"""Group service - business logic for group management"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime
import uuid
from app.models import Group, GroupCreate, GroupResponse


class GroupService:
    """Group management service"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.groups
    
    async def list_groups(self, skip: int = 0, limit: int = 100) -> List[GroupResponse]:
        """List all groups"""
        cursor = self.collection.find().skip(skip).limit(limit)
        groups = await cursor.to_list(length=limit)
        return [self._to_response(group) for group in groups]
    
    async def get_group(self, group_id: str) -> Optional[GroupResponse]:
        """Get group by ID"""
        group = await self.collection.find_one({"group_id": group_id})
        if not group:
            return None
        return self._to_response(group)
    
    async def create_group(
        self,
        group_data: GroupCreate,
        admin_address: str
    ) -> GroupResponse:
        """Create a new group"""
        group_id = f"grp_{uuid.uuid4().hex[:12]}"
        
        group_dict = {
            "group_id": group_id,
            "name": group_data.name,
            "description": group_data.description,
            "admin_address": admin_address,
            "member_agents": group_data.initial_agents,
            "collaboration_rules": {
                "task_timeout": 3600,
                "max_retries": 3,
                "require_validation": False,
                "auto_feedback": True
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        await self.collection.insert_one(group_dict)
        return self._to_response(group_dict)
    
    def _to_response(self, group_dict: dict) -> GroupResponse:
        """Convert database document to API response"""
        return GroupResponse(
            group_id=group_dict["group_id"],
            name=group_dict["name"],
            description=group_dict["description"],
            admin_address=group_dict["admin_address"],
            member_count=len(group_dict["member_agents"]),
            created_at=group_dict["created_at"],
        )

