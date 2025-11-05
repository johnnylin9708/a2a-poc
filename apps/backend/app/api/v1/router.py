"""Main API router"""
from fastapi import APIRouter
from app.api.v1.endpoints import agents, groups, tasks
from app.api.v1 import ipfs, reputation, validation

api_router = APIRouter()

api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(ipfs.router, prefix="/ipfs", tags=["ipfs"])
api_router.include_router(reputation.router, prefix="/reputation", tags=["reputation"])
api_router.include_router(validation.router, prefix="/validation", tags=["validation"])

