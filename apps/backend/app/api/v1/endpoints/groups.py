"""Group endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models import GroupCreate, GroupResponse
from app.services.group_service import GroupService
from app.core.database import get_database

router = APIRouter()


def get_group_service(db=Depends(get_database)) -> GroupService:
    """Dependency injection for GroupService"""
    return GroupService(db)


@router.get("/", response_model=List[GroupResponse])
async def list_groups(
    skip: int = 0,
    limit: int = 100,
    service: GroupService = Depends(get_group_service)
):
    """List all groups"""
    groups = await service.list_groups(skip=skip, limit=limit)
    return groups


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str,
    service: GroupService = Depends(get_group_service)
):
    """Get group by ID"""
    group = await service.get_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.post("/", response_model=GroupResponse, status_code=201)
async def create_group(
    group_data: GroupCreate,
    admin_address: str,
    service: GroupService = Depends(get_group_service)
):
    """Create a new group"""
    group = await service.create_group(group_data, admin_address)
    return group

