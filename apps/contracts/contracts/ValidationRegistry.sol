// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title ValidationRegistry
 * @dev ERC-8004 Implementation - Validation Registry
 * Third-party validation records for agent behaviors
 */
contract ValidationRegistry is AccessControl {
    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");

    enum ValidationType {
        TEE_ORACLE,             // Trusted Execution Environment
        ZERO_KNOWLEDGE_PROOF,   // ZK Proof
        STAKE_INFERENCE,        // Staked inference
        MANUAL_REVIEW,          // Human review
        AUTOMATED_TEST,         // Automated testing
        THIRD_PARTY_AUDIT       // External audit
    }

    struct Validation {
        uint256 agentId;
        ValidationType validationType;
        address validator;
        bool passed;
        string resultHash;      // IPFS hash of detailed validation result
        uint256 timestamp;
        uint256 expiresAt;      // Validation expiry timestamp (0 = never expires)
        string metadata;        // Additional metadata (JSON string)
    }

    struct ValidationStats {
        uint256 totalValidations;
        uint256 passedValidations;
        uint256 failedValidations;
        uint256 lastValidationTime;
    }

    // Agent ID => Validation[]
    mapping(uint256 => Validation[]) public agentValidations;
    
    // Agent ID => ValidationStats
    mapping(uint256 => ValidationStats) public agentValidationStats;
    
    // Validator address => is authorized
    mapping(address => bool) public authorizedValidators;
    
    // Validation ID => Dispute status
    mapping(bytes32 => bool) public disputedValidations;

    event ValidationSubmitted(
        uint256 indexed agentId, 
        ValidationType indexed validationType,
        address indexed validator,
        bool passed,
        string resultHash
    );
    
    event ValidatorAuthorized(address indexed validator);
    
    event ValidatorRevoked(address indexed validator);
    
    event ValidationDisputed(bytes32 indexed validationId, uint256 agentId);
    
    event DisputeResolved(bytes32 indexed validationId, bool outcome);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(VALIDATOR_ROLE, msg.sender);
    }

    /**
     * @dev Submit a validation result
     * @param agentId The agent's token ID
     * @param validationType Type of validation performed
     * @param passed Whether the validation passed
     * @param resultHash IPFS hash of detailed results
     * @param expiresAt Expiration timestamp (0 for no expiry)
     * @param metadata Additional metadata
     */
    function submitValidation(
        uint256 agentId,
        ValidationType validationType,
        bool passed,
        string memory resultHash,
        uint256 expiresAt,
        string memory metadata
    ) external onlyRole(VALIDATOR_ROLE) {
        require(agentId > 0, "Invalid agent ID");
        require(bytes(resultHash).length > 0, "Result hash required");

        Validation memory newValidation = Validation({
            agentId: agentId,
            validationType: validationType,
            validator: msg.sender,
            passed: passed,
            resultHash: resultHash,
            timestamp: block.timestamp,
            expiresAt: expiresAt,
            metadata: metadata
        });

        agentValidations[agentId].push(newValidation);

        // Update stats
        ValidationStats storage stats = agentValidationStats[agentId];
        stats.totalValidations++;
        if (passed) {
            stats.passedValidations++;
        } else {
            stats.failedValidations++;
        }
        stats.lastValidationTime = block.timestamp;

        emit ValidationSubmitted(agentId, validationType, msg.sender, passed, resultHash);
    }

    /**
     * @dev Get all validations for an agent
     * @param agentId The agent's token ID
     * @return Array of Validation structs
     */
    function getValidations(uint256 agentId) 
        external 
        view 
        returns (Validation[] memory) 
    {
        return agentValidations[agentId];
    }

    /**
     * @dev Get active (non-expired) validations for an agent
     * @param agentId The agent's token ID
     * @return Array of active Validation structs
     */
    function getActiveValidations(uint256 agentId) 
        external 
        view 
        returns (Validation[] memory) 
    {
        Validation[] memory allValidations = agentValidations[agentId];
        uint256 activeCount = 0;

        // Count active validations
        for (uint i = 0; i < allValidations.length; i++) {
            if (_isValidationActive(allValidations[i])) {
                activeCount++;
            }
        }

        // Create result array
        Validation[] memory activeValidations = new Validation[](activeCount);
        uint256 index = 0;

        for (uint i = 0; i < allValidations.length; i++) {
            if (_isValidationActive(allValidations[i])) {
                activeValidations[index] = allValidations[i];
                index++;
            }
        }

        return activeValidations;
    }

    /**
     * @dev Get validations by type for an agent
     * @param agentId The agent's token ID
     * @param validationType The validation type to filter by
     * @return Array of Validation structs
     */
    function getValidationsByType(
        uint256 agentId, 
        ValidationType validationType
    ) 
        external 
        view 
        returns (Validation[] memory) 
    {
        Validation[] memory allValidations = agentValidations[agentId];
        uint256 matchCount = 0;

        // Count matching validations
        for (uint i = 0; i < allValidations.length; i++) {
            if (allValidations[i].validationType == validationType) {
                matchCount++;
            }
        }

        // Create result array
        Validation[] memory matchedValidations = new Validation[](matchCount);
        uint256 index = 0;

        for (uint i = 0; i < allValidations.length; i++) {
            if (allValidations[i].validationType == validationType) {
                matchedValidations[index] = allValidations[i];
                index++;
            }
        }

        return matchedValidations;
    }

    /**
     * @dev Get validation statistics for an agent
     * @param agentId The agent's token ID
     * @return ValidationStats struct
     */
    function getValidationStats(uint256 agentId) 
        external 
        view 
        returns (ValidationStats memory) 
    {
        return agentValidationStats[agentId];
    }

    /**
     * @dev Calculate validation score for an agent (0-100)
     * @param agentId The agent's token ID
     * @return score Validation score
     */
    function getValidationScore(uint256 agentId) 
        external 
        view 
        returns (uint256 score) 
    {
        ValidationStats memory stats = agentValidationStats[agentId];
        
        if (stats.totalValidations == 0) {
            return 0;
        }

        // Score = (passed / total) * 100
        return (stats.passedValidations * 100) / stats.totalValidations;
    }

    /**
     * @dev Authorize a validator (admin only)
     * @param validator Address to authorize
     */
    function authorizeValidator(address validator) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
    {
        grantRole(VALIDATOR_ROLE, validator);
        authorizedValidators[validator] = true;
        emit ValidatorAuthorized(validator);
    }

    /**
     * @dev Revoke a validator (admin only)
     * @param validator Address to revoke
     */
    function revokeValidator(address validator) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
    {
        revokeRole(VALIDATOR_ROLE, validator);
        authorizedValidators[validator] = false;
        emit ValidatorRevoked(validator);
    }

    /**
     * @dev Dispute a validation result
     * @param agentId The agent's token ID
     * @param validationIndex Index of validation to dispute
     */
    function disputeValidation(uint256 agentId, uint256 validationIndex) 
        external 
    {
        require(validationIndex < agentValidations[agentId].length, "Invalid index");
        
        Validation memory validation = agentValidations[agentId][validationIndex];
        bytes32 validationId = keccak256(
            abi.encodePacked(agentId, validation.validator, validation.timestamp)
        );
        
        require(!disputedValidations[validationId], "Already disputed");
        
        disputedValidations[validationId] = true;
        emit ValidationDisputed(validationId, agentId);
    }

    /**
     * @dev Resolve a dispute (admin only)
     * @param validationId The validation ID
     * @param outcome Dispute outcome (true = validation upheld)
     */
    function resolveDispute(bytes32 validationId, bool outcome) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
    {
        require(disputedValidations[validationId], "No active dispute");
        
        if (!outcome) {
            disputedValidations[validationId] = false;
        }
        
        emit DisputeResolved(validationId, outcome);
    }

    /**
     * @dev Check if a validation is currently active
     */
    function _isValidationActive(Validation memory validation) 
        private 
        view 
        returns (bool) 
    {
        if (validation.expiresAt == 0) {
            return true; // Never expires
        }
        return block.timestamp < validation.expiresAt;
    }

    /**
     * @dev Check if an agent has any active validation of a specific type
     * @param agentId The agent's token ID
     * @param validationType The validation type to check
     * @return bool Whether agent has active validation of this type
     */
    function hasActiveValidation(
        uint256 agentId, 
        ValidationType validationType
    ) 
        external 
        view 
        returns (bool) 
    {
        Validation[] memory validations = agentValidations[agentId];
        
        for (uint i = 0; i < validations.length; i++) {
            if (validations[i].validationType == validationType && 
                validations[i].passed &&
                _isValidationActive(validations[i])) {
                return true;
            }
        }
        
        return false;
    }
}

