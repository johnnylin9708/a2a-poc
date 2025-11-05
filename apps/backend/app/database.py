"""
MongoDB database connection and utilities
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Global MongoDB client and database
mongo_client: Optional[AsyncIOMotorClient] = None
mongo_db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    """Connect to MongoDB"""
    global mongo_client, mongo_db
    
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongo_db = mongo_client[settings.MONGODB_DB_NAME]
        
        # Test connection
        await mongo_client.admin.command("ping")
        logger.info(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection() -> None:
    """Close MongoDB connection"""
    global mongo_client
    
    if mongo_client is not None:
        mongo_client.close()
        logger.info("✅ Closed MongoDB connection")


async def create_indexes() -> None:
    """Create database indexes"""
    if mongo_db is None:
        return
    
    try:
        # Agents collection indexes
        await mongo_db.agents.create_index("token_id", unique=True)
        await mongo_db.agents.create_index("owner_address")
        await mongo_db.agents.create_index("endpoint", unique=True)
        await mongo_db.agents.create_index("capabilities")
        await mongo_db.agents.create_index("is_active")
        
        # Groups collection indexes
        await mongo_db.groups.create_index("group_id", unique=True)
        await mongo_db.groups.create_index("admin_address")
        await mongo_db.groups.create_index("member_agents")
        
        # Tasks collection indexes
        await mongo_db.tasks.create_index("task_id", unique=True)
        await mongo_db.tasks.create_index("agent_id")
        await mongo_db.tasks.create_index("group_id")
        await mongo_db.tasks.create_index("status")
        await mongo_db.tasks.create_index("created_at")
        
        logger.info("✅ Database indexes created")
        
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")


def get_database() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance"""
    if mongo_db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return mongo_db


# Collection helpers
def get_agents_collection():
    """Get agents collection"""
    return get_database().agents


def get_groups_collection():
    """Get groups collection"""
    return get_database().groups


def get_tasks_collection():
    """Get tasks collection"""
    return get_database().tasks


def get_feedbacks_collection():
    """Get feedbacks collection"""
    return get_database().feedbacks


def get_validations_collection():
    """Get validations collection"""
    return get_database().validations

