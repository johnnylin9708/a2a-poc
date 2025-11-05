"""
Configuration management using Pydantic Settings
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Server Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_RELOAD: bool = Field(default=True, description="Auto reload in development")
    ENVIRONMENT: str = Field(default="development", description="Environment")
    
    # MongoDB
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URL"
    )
    MONGODB_DB_NAME: str = Field(
        default="a2a_ecosystem",
        description="MongoDB database name"
    )
    
    # Blockchain
    WEB3_PROVIDER_URI: str = Field(
        default="http://localhost:8545",
        description="Web3 provider URI"
    )
    CHAIN_ID: int = Field(default=31337, description="Blockchain chain ID")
    
    # Contract Addresses
    IDENTITY_REGISTRY_ADDRESS: str = Field(
        default="",
        description="AgentIdentityRegistry contract address"
    )
    PAYMENT_REGISTRY_ADDRESS: str = Field(
        default="",
        description="PaymentRegistry contract address (x402)"
    )
    REPUTATION_REGISTRY_ADDRESS: str = Field(
        default="",
        description="ReputationRegistry contract address"
    )
    VALIDATION_REGISTRY_ADDRESS: str = Field(
        default="",
        description="ValidationRegistry contract address"
    )
    
    # IPFS
    IPFS_API_URL: str = Field(
        default="http://localhost:5001",
        description="IPFS API URL"
    )
    IPFS_GATEWAY_URL: str = Field(
        default="http://localhost:8080",
        description="IPFS Gateway URL"
    )
    PINATA_API_KEY: str = Field(default="", description="Pinata API key")
    PINATA_SECRET_KEY: str = Field(default="", description="Pinata secret key")
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="CORS allowed origins"
    )
    
    # A2A Protocol
    A2A_PROTOCOL_VERSION: str = Field(default="1.0", description="A2A protocol version")
    A2A_DEFAULT_TIMEOUT: int = Field(
        default=30,
        description="Default timeout for A2A requests"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")


# Create settings instance
settings = Settings()

