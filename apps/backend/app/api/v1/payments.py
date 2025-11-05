"""
x402 Payment API endpoints
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
import logging

from app.schemas.payment import (
    PaymentCreateRequest,
    PaymentResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse
)
from app.services.payment_service import payment_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_record(request: PaymentCreateRequest):
    """
    Record a payment for agent services (x402 protocol)

    This endpoint records payment proofs that can later be used
    to verify payments and allow feedback submission
    """
    try:
        payment = await payment_service.create_payment_record(
            agent_id=request.agent_id,
            payment_proof=request.payment_proof.model_dump(),
            service_description=request.service_description,
            task_id=request.task_id
        )

        return payment

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create payment record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment record: {str(e)}"
        )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str):
    """Get payment record by ID"""
    try:
        payment = await payment_service.get_payment(payment_id)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment {payment_id} not found"
            )

        return payment

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment: {str(e)}"
        )


@router.get("/", response_model=dict)
async def list_payments(
    agent_id: Optional[int] = Query(None, description="Filter by agent ID"),
    task_id: Optional[str] = Query(None, description="Filter by task ID"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List payment records with optional filters"""
    try:
        result = await payment_service.list_payments(
            agent_id=agent_id,
            task_id=task_id,
            is_verified=is_verified,
            limit=limit,
            offset=offset
        )

        return result

    except Exception as e:
        logger.error(f"Failed to list payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list payments: {str(e)}"
        )


@router.post("/verify", response_model=PaymentVerifyResponse)
async def verify_payment(request: PaymentVerifyRequest):
    """
    Verify a payment on-chain

    This endpoint checks the blockchain to verify that the payment
    transaction is valid and confirmed
    """
    try:
        result = await payment_service.verify_payment(request.payment_id)

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to verify payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify payment: {str(e)}"
        )


@router.get("/agent/{agent_id}/stats", response_model=dict)
async def get_agent_payment_stats(agent_id: int):
    """
    Get payment statistics for a specific agent

    Returns total number of payments and total amount received
    """
    try:
        stats = await payment_service.get_agent_payment_stats(agent_id)

        return stats

    except Exception as e:
        logger.error(f"Failed to get agent payment stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent payment stats: {str(e)}"
        )

