// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title PaymentRegistry
 * @dev x402 Payment Protocol Implementation
 * Records and verifies payments for agent services
 */
contract PaymentRegistry is Ownable, ReentrancyGuard {
    
    struct Payment {
        uint256 agentId;           // Agent token ID
        address payer;             // Who paid
        address payee;             // Agent owner (recipient)
        uint256 amount;            // Payment amount in wei
        address token;             // Token address (address(0) for ETH)
        string serviceDescription; // What service was paid for
        string taskId;             // Related task ID (optional)
        uint256 timestamp;
        bytes32 txHash;            // Original transaction hash
        bool verified;             // Whether payment is verified
        bool refunded;             // Whether payment was refunded
    }

    // Payment ID => Payment
    mapping(bytes32 => Payment) public payments;
    
    // Agent ID => Payment IDs
    mapping(uint256 => bytes32[]) public agentPayments;
    
    // Payer => Payment IDs
    mapping(address => bytes32[]) public payerPayments;
    
    // Transaction hash => Payment ID (prevent double recording)
    mapping(bytes32 => bytes32) public txHashToPaymentId;
    
    // Agent ID => Total earnings
    mapping(uint256 => uint256) public agentEarnings;
    
    // Payment statistics
    uint256 public totalPayments;
    uint256 public totalVolume;

    event PaymentRecorded(
        bytes32 indexed paymentId,
        uint256 indexed agentId,
        address indexed payer,
        uint256 amount,
        bytes32 txHash
    );
    
    event PaymentVerified(
        bytes32 indexed paymentId,
        uint256 indexed agentId
    );
    
    event PaymentRefunded(
        bytes32 indexed paymentId,
        uint256 indexed agentId,
        uint256 amount
    );

    constructor() Ownable(msg.sender) {}

    /**
     * @dev Record a payment for agent services
     * @param agentId The agent's token ID
     * @param payee The agent owner's address
     * @param amount Payment amount
     * @param token Token address (address(0) for ETH)
     * @param serviceDescription Description of service
     * @param taskId Related task ID (optional)
     * @param txHash Transaction hash
     * @return paymentId The generated payment ID
     */
    function recordPayment(
        uint256 agentId,
        address payee,
        uint256 amount,
        address token,
        string memory serviceDescription,
        string memory taskId,
        bytes32 txHash
    ) external returns (bytes32 paymentId) {
        require(agentId > 0, "Invalid agent ID");
        require(payee != address(0), "Invalid payee address");
        require(amount > 0, "Amount must be greater than 0");
        require(txHash != bytes32(0), "Invalid transaction hash");
        require(txHashToPaymentId[txHash] == bytes32(0), "Transaction already recorded");

        // Generate payment ID
        paymentId = keccak256(
            abi.encodePacked(
                agentId,
                msg.sender,
                amount,
                block.timestamp,
                txHash
            )
        );

        require(payments[paymentId].timestamp == 0, "Payment ID collision");

        payments[paymentId] = Payment({
            agentId: agentId,
            payer: msg.sender,
            payee: payee,
            amount: amount,
            token: token,
            serviceDescription: serviceDescription,
            taskId: taskId,
            timestamp: block.timestamp,
            txHash: txHash,
            verified: false,
            refunded: false
        });

        agentPayments[agentId].push(paymentId);
        payerPayments[msg.sender].push(paymentId);
        txHashToPaymentId[txHash] = paymentId;

        totalPayments++;
        totalVolume += amount;

        emit PaymentRecorded(paymentId, agentId, msg.sender, amount, txHash);

        return paymentId;
    }

    /**
     * @dev Verify a payment (can be called by owner or automated oracle)
     * @param paymentId The payment ID
     */
    function verifyPayment(bytes32 paymentId) external onlyOwner {
        Payment storage payment = payments[paymentId];
        require(payment.timestamp > 0, "Payment not found");
        require(!payment.verified, "Payment already verified");
        require(!payment.refunded, "Payment was refunded");

        payment.verified = true;
        agentEarnings[payment.agentId] += payment.amount;

        emit PaymentVerified(paymentId, payment.agentId);
    }

    /**
     * @dev Get payment by ID
     * @param paymentId The payment ID
     * @return Payment struct
     */
    function getPayment(bytes32 paymentId) 
        external 
        view 
        returns (Payment memory) 
    {
        return payments[paymentId];
    }

    /**
     * @dev Get all payment IDs for an agent
     * @param agentId The agent's token ID
     * @return Array of payment IDs
     */
    function getAgentPayments(uint256 agentId) 
        external 
        view 
        returns (bytes32[] memory) 
    {
        return agentPayments[agentId];
    }

    /**
     * @dev Get all payment IDs for a payer
     * @param payer The payer's address
     * @return Array of payment IDs
     */
    function getPayerPayments(address payer) 
        external 
        view 
        returns (bytes32[] memory) 
    {
        return payerPayments[payer];
    }

    /**
     * @dev Get agent's total earnings
     * @param agentId The agent's token ID
     * @return Total earnings in wei
     */
    function getAgentEarnings(uint256 agentId) 
        external 
        view 
        returns (uint256) 
    {
        return agentEarnings[agentId];
    }

    /**
     * @dev Get agent payment statistics
     * @param agentId The agent's token ID
     * @return paymentCount Number of payments
     * @return totalEarnings Total earnings
     * @return verifiedCount Number of verified payments
     */
    function getAgentPaymentStats(uint256 agentId) 
        external 
        view 
        returns (
            uint256 paymentCount,
            uint256 totalEarnings,
            uint256 verifiedCount
        ) 
    {
        bytes32[] memory paymentIds = agentPayments[agentId];
        paymentCount = paymentIds.length;
        totalEarnings = agentEarnings[agentId];
        
        verifiedCount = 0;
        for (uint i = 0; i < paymentIds.length; i++) {
            if (payments[paymentIds[i]].verified) {
                verifiedCount++;
            }
        }
        
        return (paymentCount, totalEarnings, verifiedCount);
    }

    /**
     * @dev Check if transaction hash has been recorded
     * @param txHash Transaction hash
     * @return bool Whether the tx has been recorded
     */
    function isTransactionRecorded(bytes32 txHash) 
        external 
        view 
        returns (bool) 
    {
        return txHashToPaymentId[txHash] != bytes32(0);
    }

    /**
     * @dev Get payment ID by transaction hash
     * @param txHash Transaction hash
     * @return paymentId The payment ID
     */
    function getPaymentIdByTxHash(bytes32 txHash) 
        external 
        view 
        returns (bytes32) 
    {
        return txHashToPaymentId[txHash];
    }

    /**
     * @dev Batch verify payments (gas optimization)
     * @param paymentIds Array of payment IDs
     */
    function batchVerifyPayments(bytes32[] memory paymentIds) 
        external 
        onlyOwner 
    {
        for (uint i = 0; i < paymentIds.length; i++) {
            Payment storage payment = payments[paymentIds[i]];
            
            if (payment.timestamp > 0 && 
                !payment.verified && 
                !payment.refunded) {
                payment.verified = true;
                agentEarnings[payment.agentId] += payment.amount;
                emit PaymentVerified(paymentIds[i], payment.agentId);
            }
        }
    }

    /**
     * @dev Get global payment statistics
     * @return totalPaymentCount Total number of payments
     * @return totalPaymentVolume Total payment volume
     */
    function getGlobalStats() 
        external 
        view 
        returns (uint256 totalPaymentCount, uint256 totalPaymentVolume) 
    {
        return (totalPayments, totalVolume);
    }
}

