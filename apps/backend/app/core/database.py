"""Database connection and utilities"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from typing import Optional


class Database:
    """MongoDB database connection manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db_instance = Database()


async def connect_to_mongo():
    """Connect to MongoDB"""
    db_instance.client = AsyncIOMotorClient(settings.MONGODB_URI)
    db_instance.db = db_instance.client[settings.MONGODB_DB_NAME]
    
    # Create indexes
    await create_indexes()


async def close_mongo_connection():
    """Close MongoDB connection"""
    if db_instance.client:
        db_instance.client.close()


async def create_indexes():
    """Create database indexes"""
    if db_instance.db is None:
        return
    
    # Agents collection indexes
    await db_instance.db.agents.create_index("token_id", unique=True)
    await db_instance.db.agents.create_index("endpoint", unique=True)
    await db_instance.db.agents.create_index("owner_address")
    await db_instance.db.agents.create_index([("capabilities", 1)])
    
    # Groups collection indexes
    await db_instance.db.groups.create_index("group_id", unique=True)
    await db_instance.db.groups.create_index("admin_address")
    
    # Tasks collection indexes
    await db_instance.db.tasks.create_index("task_id", unique=True)
    await db_instance.db.tasks.create_index("agent_id")
    await db_instance.db.tasks.create_index("status")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if db_instance.db is None:
        raise RuntimeError("Database not connected")
    return db_instance.db

