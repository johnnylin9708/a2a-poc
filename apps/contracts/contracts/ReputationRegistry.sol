// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

interface IPaymentRegistry {
    function getPayment(bytes32 paymentId) external view returns (
        uint256 agentId,
        address payer,
        address payee,
        uint256 amount,
        address token,
        string memory serviceDescription,
        string memory taskId,
        uint256 timestamp,
        bytes32 txHash,
        bool verified,
        bool refunded
    );
    function isTransactionRecorded(bytes32 txHash) external view returns (bool);
}

/**
 * @title ReputationRegistry
 * @dev ERC-8004 Implementation - Reputation Registry
 * Decentralized feedback system tied to payment proofs (x402)
 */
contract ReputationRegistry is Ownable {
    IPaymentRegistry public paymentRegistry;
    struct Feedback {
        uint256 agentId;
        address reviewer;
        uint8 rating;           // 1-5 stars
        string comment;
        bytes32 paymentProof;   // x402 payment proof hash
        uint256 timestamp;
        bool verified;
    }

    struct ReputationScore {
        uint256 totalRating;
        uint256 feedbackCount;
        uint256 averageRating;  // Scaled by 100 (e.g., 450 = 4.50 stars)
    }

    // Agent ID => Feedback[]
    mapping(uint256 => Feedback[]) public agentFeedbacks;
    
    // Agent ID => Reputation Score
    mapping(uint256 => ReputationScore) public agentScores;
    
    // Payment proof => used (prevent double feedback)
    mapping(bytes32 => bool) public usedPaymentProofs;
    
    // Blacklisted reviewers (spam prevention)
    mapping(address => bool) public blacklistedReviewers;

    event FeedbackSubmitted(
        uint256 indexed agentId, 
        address indexed reviewer, 
        uint8 rating,
        bytes32 paymentProof
    );
    
    event FeedbackVerified(
        uint256 indexed agentId,
        uint256 feedbackIndex
    );
    
    event ReviewerBlacklisted(address indexed reviewer);
    
    event ReviewerWhitelisted(address indexed reviewer);

    constructor(address _paymentRegistry) Ownable(msg.sender) {
        require(_paymentRegistry != address(0), "Invalid payment registry address");
        paymentRegistry = IPaymentRegistry(_paymentRegistry);
    }

    /**
     * @dev Update payment registry address (owner only)
     * @param _paymentRegistry New payment registry address
     */
    function setPaymentRegistry(address _paymentRegistry) external onlyOwner {
        require(_paymentRegistry != address(0), "Invalid payment registry address");
        paymentRegistry = IPaymentRegistry(_paymentRegistry);
    }

    /**
     * @dev Submit feedback for an agent (must have valid payment proof from PaymentRegistry)
     * @param agentId The agent's token ID
     * @param rating Rating from 1 to 5
     * @param comment Feedback comment
     * @param paymentProof x402 payment ID from PaymentRegistry
     */
    function submitFeedback(
        uint256 agentId,
        uint8 rating,
        string memory comment,
        bytes32 paymentProof
    ) external {
        require(rating >= 1 && rating <= 5, "Invalid rating (1-5)");
        require(!usedPaymentProofs[paymentProof], "Payment proof already used");
        require(!blacklistedReviewers[msg.sender], "Reviewer is blacklisted");
        require(agentId > 0, "Invalid agent ID");

        // Verify payment exists and is valid
        (
            uint256 paymentAgentId,
            address payer,
            ,  // payee
            ,  // amount
            ,  // token
            ,  // serviceDescription
            ,  // taskId
            ,  // timestamp
            ,  // txHash
            bool verified,
            bool refunded
        ) = paymentRegistry.getPayment(paymentProof);

        require(paymentAgentId == agentId, "Payment is for different agent");
        require(payer == msg.sender, "Only payer can submit feedback");
        require(verified, "Payment not verified yet");
        require(!refunded, "Payment was refunded");

        usedPaymentProofs[paymentProof] = true;

        Feedback memory newFeedback = Feedback({
            agentId: agentId,
            reviewer: msg.sender,
            rating: rating,
            comment: comment,
            paymentProof: paymentProof,
            timestamp: block.timestamp,
            verified: true  // Auto-verified since payment is verified
        });

        agentFeedbacks[agentId].push(newFeedback);

        // Update reputation score
        _updateReputationScore(agentId);

        emit FeedbackSubmitted(agentId, msg.sender, rating, paymentProof);
    }

    /**
     * @dev Update average reputation score for an agent
     * @param agentId The agent's token ID
     */
    function _updateReputationScore(uint256 agentId) private {
        Feedback[] memory feedbacks = agentFeedbacks[agentId];
        require(feedbacks.length > 0, "No feedbacks");

        uint256 totalRating = 0;
        uint256 verifiedCount = 0;

        for (uint i = 0; i < feedbacks.length; i++) {
            if (feedbacks[i].verified) {
                totalRating += feedbacks[i].rating;
                verifiedCount++;
            }
        }

        if (verifiedCount > 0) {
            uint256 averageRating = (totalRating * 100) / verifiedCount;
            
            agentScores[agentId] = ReputationScore({
                totalRating: totalRating,
                feedbackCount: verifiedCount,
                averageRating: averageRating
            });
        }
    }

    /**
     * @dev Get agent reputation score
     * @param agentId The agent's token ID
     * @return averageRating Average rating (scaled by 100)
     * @return feedbackCount Total number of verified feedbacks
     */
    function getReputationScore(uint256 agentId) 
        external 
        view 
        returns (uint256 averageRating, uint256 feedbackCount) 
    {
        ReputationScore memory score = agentScores[agentId];
        return (score.averageRating, score.feedbackCount);
    }

    /**
     * @dev Get all feedbacks for an agent
     * @param agentId The agent's token ID
     * @return Array of Feedback structs
     */
    function getAgentFeedbacks(uint256 agentId) 
        external 
        view 
        returns (Feedback[] memory) 
    {
        return agentFeedbacks[agentId];
    }

    /**
     * @dev Get paginated feedbacks for an agent
     * @param agentId The agent's token ID
     * @param offset Starting index
     * @param limit Number of feedbacks to return
     * @return Array of Feedback structs
     */
    function getAgentFeedbacksPaginated(
        uint256 agentId, 
        uint256 offset, 
        uint256 limit
    ) 
        external 
        view 
        returns (Feedback[] memory) 
    {
        Feedback[] memory allFeedbacks = agentFeedbacks[agentId];
        
        if (offset >= allFeedbacks.length) {
            return new Feedback[](0);
        }

        uint256 end = offset + limit;
        if (end > allFeedbacks.length) {
            end = allFeedbacks.length;
        }

        uint256 resultLength = end - offset;
        Feedback[] memory result = new Feedback[](resultLength);

        for (uint i = 0; i < resultLength; i++) {
            result[i] = allFeedbacks[offset + i];
        }

        return result;
    }

    /**
     * @dev Get feedback count for an agent
     * @param agentId The agent's token ID
     * @return Total number of feedbacks
     */
    function getFeedbackCount(uint256 agentId) external view returns (uint256) {
        return agentFeedbacks[agentId].length;
    }

    /**
     * @dev Blacklist a reviewer (owner only)
     * @param reviewer Address to blacklist
     */
    function blacklistReviewer(address reviewer) external onlyOwner {
        blacklistedReviewers[reviewer] = true;
        emit ReviewerBlacklisted(reviewer);
    }

    /**
     * @dev Whitelist a reviewer (owner only)
     * @param reviewer Address to whitelist
     */
    function whitelistReviewer(address reviewer) external onlyOwner {
        blacklistedReviewers[reviewer] = false;
        emit ReviewerWhitelisted(reviewer);
    }

    /**
     * @dev Check if payment proof has been used
     * @param paymentProof The payment proof hash
     * @return bool Whether the proof has been used
     */
    function isPaymentProofUsed(bytes32 paymentProof) external view returns (bool) {
        return usedPaymentProofs[paymentProof];
    }

    /**
     * @dev Get reputation tier based on score
     * @param agentId The agent's token ID
     * @return tier Reputation tier (0=New, 1=Bronze, 2=Silver, 3=Gold, 4=Platinum)
     */
    function getReputationTier(uint256 agentId) external view returns (uint8 tier) {
        ReputationScore memory score = agentScores[agentId];
        
        if (score.feedbackCount == 0) {
            return 0; // New agent
        }
        
        uint256 avgRating = score.averageRating;
        uint256 count = score.feedbackCount;
        
        // Tier calculation based on average rating and feedback count
        if (avgRating >= 450 && count >= 100) {
            return 4; // Platinum (4.5+ stars, 100+ reviews)
        } else if (avgRating >= 400 && count >= 50) {
            return 3; // Gold (4.0+ stars, 50+ reviews)
        } else if (avgRating >= 350 && count >= 20) {
            return 2; // Silver (3.5+ stars, 20+ reviews)
        } else if (avgRating >= 300 && count >= 5) {
            return 1; // Bronze (3.0+ stars, 5+ reviews)
        } else {
            return 0; // New or low reputation
        }
    }
}

