"""
Blockchain service for interacting with ERC-8004 smart contracts
"""

from typing import List, Dict, Optional, Tuple
from web3 import Web3
from web3.contract import Contract
from eth_account import Account
import json
import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


class BlockchainService:
    """Service for blockchain interactions"""
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URI))
        self.chain_id = settings.CHAIN_ID
        
        # Load contract ABIs and addresses
        self.identity_registry = self._load_contract(
            settings.IDENTITY_REGISTRY_ADDRESS,
            "AgentIdentityRegistry"
        )
        self.reputation_registry = self._load_contract(
            settings.REPUTATION_REGISTRY_ADDRESS,
            "ReputationRegistry"
        )
        self.validation_registry = self._load_contract(
            settings.VALIDATION_REGISTRY_ADDRESS,
            "ValidationRegistry"
        )
        
        logger.info(f"✅ Connected to blockchain (Chain ID: {self.chain_id})")
    
    def _load_contract(self, address: str, contract_name: str) -> Optional[Contract]:
        """Load contract from ABI and address"""
        if not address or address == "":
            logger.warning(f"⚠️ {contract_name} address not configured")
            return None
        
        try:
            # Try to load ABI from contracts artifacts
            abi_path = Path(__file__).parent.parent.parent.parent / "contracts" / "artifacts" / "contracts" / f"{contract_name}.sol" / f"{contract_name}.json"
            
            if abi_path.exists():
                with open(abi_path, 'r') as f:
                    contract_json = json.load(f)
                    abi = contract_json['abi']
            else:
                logger.error(f"❌ ABI file not found for {contract_name}")
                return None
            
            contract = self.w3.eth.contract(address=address, abi=abi)
            logger.info(f"✅ Loaded {contract_name} at {address}")
            return contract
            
        except Exception as e:
            logger.error(f"❌ Failed to load {contract_name}: {e}")
            return None
    
    async def register_agent(
        self,
        name: str,
        description: str,
        capabilities: List[str],
        endpoint: str,
        metadata_uri: str,
        owner_address: str,
        private_key: str
    ) -> int:
        """
        Register a new agent on blockchain and mint NFT
        
        Returns:
            Token ID of the newly registered agent
        """
        if not self.identity_registry:
            raise ValueError("Identity Registry contract not initialized")
        
        try:
            # Build transaction
            tx = self.identity_registry.functions.registerAgent(
                name,
                description,
                capabilities,
                endpoint,
                metadata_uri
            ).build_transaction({
                'from': owner_address,
                'nonce': self.w3.eth.get_transaction_count(owner_address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.chain_id
            })
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)  # 改为 raw_transaction
            logger.info(f"📤 Transaction sent: {tx_hash.hex()}")
            
            # Wait for receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.info(f"✅ Transaction confirmed in block {tx_receipt['blockNumber']}")
            
            # Extract token ID from event logs
            token_id = self._extract_token_id_from_receipt(tx_receipt)
            logger.info(f"✅ Agent registered with Token ID: {token_id}")
            
            return token_id
            
        except Exception as e:
            logger.error(f"❌ Failed to register agent: {e}")
            raise
    
    def _extract_token_id_from_receipt(self, tx_receipt) -> int:
        """Extract token ID from transaction receipt"""
        if not self.identity_registry:
            raise ValueError("Identity Registry not initialized")
        
        # Get AgentRegistered event
        event_signature_hash = self.w3.keccak(text="AgentRegistered(uint256,string,address,string)")
        
        for log in tx_receipt['logs']:
            if log['topics'][0] == event_signature_hash:
                # First topic after signature is the token ID
                token_id = int(log['topics'][1].hex(), 16)
                return token_id
        
        raise ValueError("AgentRegistered event not found in transaction receipt")
    
    async def get_agent_card(self, token_id: int) -> Dict:
        """Get agent card from blockchain"""
        if not self.identity_registry:
            raise ValueError("Identity Registry not initialized")
        
        try:
            agent_card = self.identity_registry.functions.getAgentCard(token_id).call()
            
            return {
                "name": agent_card[0],
                "description": agent_card[1],
                "capabilities": list(agent_card[2]),
                "endpoint": agent_card[3],
                "metadata_uri": agent_card[4],
                "created_at": agent_card[5],
                "is_active": agent_card[6],
                "owner_address": agent_card[7]
            }
        except Exception as e:
            logger.error(f"❌ Failed to get agent card: {e}")
            raise
    
    async def find_agents_by_capability(self, capability: str) -> List[int]:
        """Find agents by capability"""
        if not self.identity_registry:
            raise ValueError("Identity Registry not initialized")
        
        try:
            agent_ids = self.identity_registry.functions.findAgentsByCapability(capability).call()
            return list(agent_ids)
        except Exception as e:
            logger.error(f"❌ Failed to find agents: {e}")
            raise
    
    async def get_reputation_score(self, agent_id: int) -> Tuple[float, int]:
        """
        Get reputation score for an agent
        
        Returns:
            Tuple of (average_rating, feedback_count)
        """
        if not self.reputation_registry:
            raise ValueError("Reputation Registry not initialized")
        
        try:
            score, count = self.reputation_registry.functions.getReputationScore(agent_id).call()
            # Convert score from 0-500 to 0.0-5.0
            average_rating = score / 100.0
            return average_rating, count
        except Exception as e:
            logger.error(f"❌ Failed to get reputation score: {e}")
            return 0.0, 0
    
    async def submit_feedback(
        self,
        agent_id: int,
        rating: int,
        comment: str,
        payment_proof: bytes,
        reviewer_address: str,
        private_key: str
    ):
        """Submit feedback for an agent"""
        if not self.reputation_registry:
            raise ValueError("Reputation Registry not initialized")
        
        try:
            # 确保 payment_proof 是 32 字节
            if len(payment_proof) < 32:
                # 填充到 32 字节
                payment_proof = payment_proof + b'\x00' * (32 - len(payment_proof))
            elif len(payment_proof) > 32:
                # 截断到 32 字节
                payment_proof = payment_proof[:32]
            
            tx = self.reputation_registry.functions.submitFeedback(
                agent_id,
                rating,
                comment,
                payment_proof
            ).build_transaction({
                'from': reviewer_address,
                'nonce': self.w3.eth.get_transaction_count(reviewer_address),
                'gas': 3000000,  # 增加 gas limit
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.chain_id
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)  # 改为 raw_transaction
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"✅ Feedback submitted for agent {agent_id} (tx: {tx_hash.hex()})")
            return tx_receipt
            
        except Exception as e:
            logger.error(f"❌ Failed to submit feedback: {e}")
            raise
    
    async def get_validation_stats(self, agent_id: int) -> Dict:
        """Get validation statistics for an agent"""
        if not self.validation_registry:
            raise ValueError("Validation Registry not initialized")
        
        try:
            stats = self.validation_registry.functions.getValidationStats(agent_id).call()
            return {
                "total_validations": stats[0],
                "passed_validations": stats[1],
                "failed_validations": stats[2],
                "last_validation_time": stats[3]
            }
        except Exception as e:
            logger.error(f"❌ Failed to get validation stats: {e}")
            return {
                "total_validations": 0,
                "passed_validations": 0,
                "failed_validations": 0,
                "last_validation_time": 0
            }
    
    def is_connected(self) -> bool:
        """Check if connected to blockchain"""
        return self.w3.is_connected()


# Create singleton instance
blockchain_service = BlockchainService()

