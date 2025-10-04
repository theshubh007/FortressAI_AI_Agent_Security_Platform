"""
MongoDB Atlas Database Connection
"""
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import logging

logger = logging.getLogger(__name__)

# MongoDB connection string from environment
MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
)

# Database name
DATABASE_NAME = os.getenv("DATABASE_NAME", "banking_db")

# Global client instance
client = None
database = None


async def connect_to_mongo():
    """Connect to MongoDB Atlas."""
    global client, database
    
    try:
        logger.info("Connecting to MongoDB Atlas...")
        
        # Create client with server API version
        client = MongoClient(
            MONGODB_URL,
            server_api=ServerApi('1'),
            maxPoolSize=10,
            minPoolSize=1
        )
        
        # Test connection
        client.admin.command('ping')
        
        # Get database
        database = client[DATABASE_NAME]
        
        logger.info(f"✅ Connected to MongoDB Atlas database: {DATABASE_NAME}")
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection."""
    global client
    
    if client:
        client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """Get database instance."""
    return database


# Collections
def get_accounts_collection():
    """Get accounts collection."""
    return database.accounts


def get_transactions_collection():
    """Get transactions collection."""
    return database.transactions


def get_users_collection():
    """Get users collection."""
    return database.users


def get_customers_collection():
    """Get customers collection."""
    return database.customers


def get_roles_collection():
    """Get roles collection."""
    return database.roles


def get_user_roles_collection():
    """Get user_roles collection."""
    return database.user_roles
