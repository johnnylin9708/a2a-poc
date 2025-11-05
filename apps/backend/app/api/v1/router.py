"""Main API router"""
from fastapi import APIRouter
from app.api.v1.endpoints import agents, groups, tasks

api_router = APIRouter()

api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

