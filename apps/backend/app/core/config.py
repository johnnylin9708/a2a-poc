"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Agent Ecosystem API"
    VERSION: str = "1.0.0"
    
    # Server Settings
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/a2a_ecosystem"
    MONGODB_DB_NAME: str = "a2a_ecosystem"
    
    # Blockchain
    ETHEREUM_RPC_URL: str = ""
    PRIVATE_KEY: str = ""
    IDENTITY_REGISTRY_ADDRESS: str = ""
    REPUTATION_REGISTRY_ADDRESS: str = ""
    VALIDATION_REGISTRY_ADDRESS: str = ""
    
    # IPFS
    IPFS_API_URL: str = "https://ipfs.infura.io:5001"
    IPFS_GATEWAY_URL: str = "https://ipfs.io/ipfs/"
    PINATA_API_KEY: str = ""
    PINATA_SECRET_KEY: str = ""
    
    # A2A
    A2A_REGISTRY_URL: str = "https://registry.a2a.dev"
    
    # Security
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = "../../.env"
        case_sensitive = True


settings = Settings()

