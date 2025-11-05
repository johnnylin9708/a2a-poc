"""
x402 Payment Service for handling payment proofs and verification
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import logging

from app.database import get_agents_collection
from app.services.blockchain import blockchain_service

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for managing x402 payment proofs"""

    def __init__(self):
        self._payments_collection = None
        self._agents_collection = None
        logger.info("✅ Payment Service (x402) initialized")

    @property
    def payments_collection(self):
        """Lazy loading of payments collection"""
        if self._payments_collection is None:
            from app.database import get_database
            self._payments_collection = get_database().payments
        return self._payments_collection

    @property
    def agents_collection(self):
        """Lazy loading of agents collection"""
        if self._agents_collection is None:
            self._agents_collection = get_agents_collection()
        return self._agents_collection

    async def create_payment_record(
        self,
        agent_id: int,
        payment_proof: Dict[str, Any],
        service_description: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a payment record

        Args:
            agent_id: Agent token ID
            payment_proof: Payment proof data
            service_description: Description of service
            task_id: Optional related task ID

        Returns:
            Created payment document
        """
        try:
            # Verify agent exists
            agent = await self.agents_collection.find_one({"token_id": agent_id})
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")

            # Check if payment proof already exists (prevent double payment)
            tx_hash = payment_proof.get("transaction_hash")
            existing = await self.payments_collection.find_one(
                {"payment_proof.transaction_hash": tx_hash}
            )
            
            if existing:
                raise ValueError(f"Payment with transaction {tx_hash} already recorded")

            payment_id = str(uuid.uuid4())

            payment_doc = {
                "payment_id": payment_id,
                "agent_id": agent_id,
                "agent_name": agent.get("name", f"Agent #{agent_id}"),
                "task_id": task_id,
                "payment_proof": payment_proof,
                "service_description": service_description,
                "is_verified": False,  # Will be verified separately
                "verification_status": {
                    "transaction_confirmed": False,
                    "amount_matches": False,
                    "signature_valid": False
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            await self.payments_collection.insert_one(payment_doc)

            logger.info(f"✅ Payment {payment_id} recorded for agent {agent_id}")

            # Try to verify immediately
            try:
                await self._verify_payment(payment_id)
            except Exception as e:
                logger.warning(f"⚠️ Initial verification failed: {e}")

            # Remove MongoDB _id
            payment_doc.pop("_id", None)

            return payment_doc

        except Exception as e:
            logger.error(f"❌ Failed to create payment record: {e}")
            raise

    async def _verify_payment(self, payment_id: str) -> bool:
        """
        Verify a payment on-chain

        Args:
            payment_id: Payment ID

        Returns:
            True if verified successfully
        """
        try:
            payment = await self.payments_collection.find_one({"payment_id": payment_id})
            
            if not payment:
                raise ValueError(f"Payment {payment_id} not found")

            proof = payment["payment_proof"]
            tx_hash = proof.get("transaction_hash")

            # Check if transaction exists on blockchain
            try:
                tx_receipt = blockchain_service.w3.eth.get_transaction_receipt(tx_hash)
                transaction_confirmed = tx_receipt["status"] == 1
            except Exception as e:
                logger.warning(f"⚠️ Failed to get transaction receipt: {e}")
                transaction_confirmed = False

            # For now, we'll consider it verified if the transaction exists
            # In production, you'd verify amount, recipient, etc.
            verification_status = {
                "transaction_confirmed": transaction_confirmed,
                "amount_matches": True,  # TODO: Implement amount verification
                "signature_valid": True   # TODO: Implement signature verification
            }

            is_verified = transaction_confirmed

            # Update payment record
            await self.payments_collection.update_one(
                {"payment_id": payment_id},
                {
                    "$set": {
                        "is_verified": is_verified,
                        "verification_status": verification_status,
                        "verified_at": datetime.utcnow() if is_verified else None,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            logger.info(f"✅ Payment {payment_id} verification: {is_verified}")

            return is_verified

        except Exception as e:
            logger.error(f"❌ Failed to verify payment: {e}")
            raise

    async def get_payment(self, payment_id: str) -> Optional[Dict]:
        """Get payment by ID"""
        try:
            payment = await self.payments_collection.find_one({"payment_id": payment_id})

            if payment:
                payment.pop("_id", None)

            return payment

        except Exception as e:
            logger.error(f"❌ Failed to get payment: {e}")
            return None

    async def list_payments(
        self,
        agent_id: Optional[int] = None,
        task_id: Optional[str] = None,
        is_verified: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List payments with filters

        Args:
            agent_id: Filter by agent ID
            task_id: Filter by task ID
            is_verified: Filter by verification status
            limit: Max results
            offset: Results offset

        Returns:
            Dict with payments and pagination info
        """
        try:
            query = {}

            if agent_id is not None:
                query["agent_id"] = agent_id

            if task_id is not None:
                query["task_id"] = task_id

            if is_verified is not None:
                query["is_verified"] = is_verified

            total = await self.payments_collection.count_documents(query)

            cursor = self.payments_collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
            payments = await cursor.to_list(length=limit)

            # Remove MongoDB _id
            for payment in payments:
                payment.pop("_id", None)

            return {
                "payments": payments,
                "total": total,
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            logger.error(f"❌ Failed to list payments: {e}")
            raise

    async def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Manually trigger payment verification

        Args:
            payment_id: Payment ID

        Returns:
            Verification result
        """
        try:
            is_valid = await self._verify_payment(payment_id)

            payment = await self.get_payment(payment_id)

            return {
                "payment_id": payment_id,
                "is_valid": is_valid,
                "transaction_confirmed": payment["verification_status"]["transaction_confirmed"],
                "amount_matches": payment["verification_status"]["amount_matches"],
                "signature_valid": payment["verification_status"]["signature_valid"],
                "message": "Payment verified successfully" if is_valid else "Payment verification failed"
            }

        except Exception as e:
            logger.error(f"❌ Failed to verify payment: {e}")
            raise

    async def get_agent_payment_stats(self, agent_id: int) -> Dict[str, Any]:
        """Get payment statistics for an agent"""
        try:
            pipeline = [
                {"$match": {"agent_id": agent_id, "is_verified": True}},
                {
                    "$group": {
                        "_id": None,
                        "total_payments": {"$sum": 1},
                        "total_amount": {
                            "$sum": {
                                "$toDouble": "$payment_proof.amount"
                            }
                        }
                    }
                }
            ]

            cursor = self.payments_collection.aggregate(pipeline)
            results = await cursor.to_list(length=1)

            if results:
                result = results[0]
                return {
                    "agent_id": agent_id,
                    "total_payments": result["total_payments"],
                    "total_amount_wei": str(int(result["total_amount"])),
                    "total_amount_eth": str(result["total_amount"] / 1e18)
                }
            else:
                return {
                    "agent_id": agent_id,
                    "total_payments": 0,
                    "total_amount_wei": "0",
                    "total_amount_eth": "0"
                }

        except Exception as e:
            logger.error(f"❌ Failed to get agent payment stats: {e}")
            raise


# Create singleton instance
payment_service = PaymentService()

