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
        
        # Feedbacks collection indexes
        await mongo_db.feedbacks.create_index("agent_id")
        await mongo_db.feedbacks.create_index("reviewer_address")
        await mongo_db.feedbacks.create_index("created_at")
        await mongo_db.feedbacks.create_index([("agent_id", 1), ("created_at", -1)])
        
        # Validations collection indexes
        await mongo_db.validations.create_index("agent_id")
        await mongo_db.validations.create_index("validation_type")
        await mongo_db.validations.create_index("created_at")
        
        # Prompt templates collection indexes
        await mongo_db.prompt_templates.create_index("template_id", unique=True)
        await mongo_db.prompt_templates.create_index("agent_id")
        await mongo_db.prompt_templates.create_index("category")
        await mongo_db.prompt_templates.create_index("is_public")
        await mongo_db.prompt_templates.create_index("tags")
        await mongo_db.prompt_templates.create_index("usage_count")
        
        # Payments collection indexes (x402)
        await mongo_db.payments.create_index("payment_id", unique=True)
        await mongo_db.payments.create_index("agent_id")
        await mongo_db.payments.create_index("task_id")
        await mongo_db.payments.create_index("payment_proof.transaction_hash", unique=True)
        await mongo_db.payments.create_index("is_verified")
        await mongo_db.payments.create_index("created_at")
        
        # API Keys collection indexes (Phase 3)
        await mongo_db.api_keys.create_index("key_hash", unique=True)
        await mongo_db.api_keys.create_index("owner_address")
        await mongo_db.api_keys.create_index("tier")
        await mongo_db.api_keys.create_index("is_active")
        await mongo_db.api_keys.create_index("created_at")
        
        # Errors collection indexes (Phase 3)
        await mongo_db.errors.create_index("error_type")
        await mongo_db.errors.create_index("severity")
        await mongo_db.errors.create_index("timestamp")
        await mongo_db.errors.create_index([("error_type", 1), ("timestamp", -1)])
        await mongo_db.errors.create_index("resolved")
        
        # API Requests collection indexes (Phase 3)
        await mongo_db.api_requests.create_index("timestamp")
        await mongo_db.api_requests.create_index("path")
        await mongo_db.api_requests.create_index("status_code")
        await mongo_db.api_requests.create_index([("timestamp", -1), ("path", 1)])
        
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


def get_prompt_templates_collection():
    """Get prompt templates collection"""
    return get_database().prompt_templates


def get_payments_collection():
    """Get payments collection"""
    return get_database().payments


def get_api_keys_collection():
    """Get API keys collection"""
    return get_database().api_keys


def get_errors_collection():
    """Get errors collection"""
    return get_database().errors


def get_api_requests_collection():
    """Get API requests collection"""
    return get_database().api_requests
