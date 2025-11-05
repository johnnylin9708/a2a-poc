"""
x402 Payment Protocol schemas
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PaymentProof(BaseModel):
    """Payment proof structure for x402 protocol"""
    transaction_hash: str = Field(..., description="Blockchain transaction hash")
    from_address: str = Field(..., description="Payer address")
    to_address: str = Field(..., description="Payee address")
    amount: str = Field(..., description="Payment amount (in wei or token units)")
    token: str = Field(default="ETH", description="Payment token (ETH, USDC, etc.)")
    timestamp: datetime = Field(..., description="Payment timestamp")
    signature: Optional[str] = Field(None, description="Payment signature")
    chain_id: int = Field(default=31337, description="Blockchain chain ID")


class PaymentCreateRequest(BaseModel):
    """Request to record a payment"""
    agent_id: int = Field(..., description="Agent token ID")
    task_id: Optional[str] = Field(None, description="Related task ID")
    payment_proof: PaymentProof
    service_description: str = Field(..., description="Description of service paid for")


class PaymentResponse(BaseModel):
    """Payment record response"""
    payment_id: str
    agent_id: int
    agent_name: str
    task_id: Optional[str]
    payment_proof: PaymentProof
    service_description: str
    is_verified: bool
    created_at: datetime


class PaymentVerifyRequest(BaseModel):
    """Request to verify a payment"""
    payment_id: str


class PaymentVerifyResponse(BaseModel):
    """Payment verification response"""
    payment_id: str
    is_valid: bool
    transaction_confirmed: bool
    amount_matches: bool
    signature_valid: bool
    message: str

