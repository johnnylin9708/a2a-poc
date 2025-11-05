// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title AgentIdentityRegistry
 * @dev ERC-8004 Implementation - Agent Identity Registry (ERC-721)
 * Each AI Agent receives a unique NFT as their identity
 */
contract AgentIdentityRegistry is ERC721URIStorage, Ownable {
    uint256 private _tokenIdCounter;

    struct AgentCard {
        string name;
        string description;
        string[] capabilities;
        string endpoint;        // A2A Protocol endpoint
        string metadataURI;     // IPFS link to full metadata
        uint256 createdAt;
        bool isActive;
        address owner;
    }

    // Agent NFT ID => Agent Card
    mapping(uint256 => AgentCard) public agentCards;
    
    // Agent endpoint => NFT ID (for quick lookup)
    mapping(string => uint256) public endpointToTokenId;
    
    // Owner address => Agent IDs
    mapping(address => uint256[]) public ownerAgents;
    
    // Capability => Agent IDs (for discovery)
    mapping(string => uint256[]) private capabilityIndex;

    event AgentRegistered(
        uint256 indexed tokenId, 
        string endpoint, 
        address indexed owner,
        string name
    );
    
    event AgentCardUpdated(uint256 indexed tokenId);
    
    event AgentDeactivated(uint256 indexed tokenId);
    
    event AgentReactivated(uint256 indexed tokenId);

    constructor() ERC721("AI Agent Identity", "AGENT") Ownable(msg.sender) {}

    /**
     * @dev Register a new agent and mint identity NFT
     * @param name Agent name
     * @param description Agent description
     * @param capabilities Array of agent capabilities
     * @param endpoint A2A protocol endpoint
     * @param metadataURI IPFS URI for full metadata
     * @return newTokenId The newly minted token ID
     */
    function registerAgent(
        string memory name,
        string memory description,
        string[] memory capabilities,
        string memory endpoint,
        string memory metadataURI
    ) external returns (uint256) {
        require(bytes(endpoint).length > 0, "Endpoint cannot be empty");
        require(endpointToTokenId[endpoint] == 0, "Endpoint already registered");
        require(capabilities.length > 0, "Must have at least one capability");

        uint256 newTokenId = ++_tokenIdCounter;

        _safeMint(msg.sender, newTokenId);
        _setTokenURI(newTokenId, metadataURI);

        agentCards[newTokenId] = AgentCard({
            name: name,
            description: description,
            capabilities: capabilities,
            endpoint: endpoint,
            metadataURI: metadataURI,
            createdAt: block.timestamp,
            isActive: true,
            owner: msg.sender
        });

        endpointToTokenId[endpoint] = newTokenId;
        ownerAgents[msg.sender].push(newTokenId);

        // Index by capabilities
        for (uint i = 0; i < capabilities.length; i++) {
            capabilityIndex[capabilities[i]].push(newTokenId);
        }

        emit AgentRegistered(newTokenId, endpoint, msg.sender, name);

        return newTokenId;
    }

    /**
     * @dev Update agent card information
     * @param tokenId Agent token ID
     * @param description New description
     * @param capabilities New capabilities array
     * @param metadataURI New metadata URI
     */
    function updateAgentCard(
        uint256 tokenId,
        string memory description,
        string[] memory capabilities,
        string memory metadataURI
    ) external {
        require(ownerOf(tokenId) == msg.sender, "Not agent owner");
        require(_exists(tokenId), "Token does not exist");

        AgentCard storage card = agentCards[tokenId];
        
        // Remove from old capability indexes
        for (uint i = 0; i < card.capabilities.length; i++) {
            _removeFromCapabilityIndex(card.capabilities[i], tokenId);
        }

        // Update card
        card.description = description;
        card.capabilities = capabilities;
        card.metadataURI = metadataURI;
        
        _setTokenURI(tokenId, metadataURI);

        // Add to new capability indexes
        for (uint i = 0; i < capabilities.length; i++) {
            capabilityIndex[capabilities[i]].push(tokenId);
        }

        emit AgentCardUpdated(tokenId);
    }

    /**
     * @dev Deactivate an agent
     * @param tokenId Agent token ID
     */
    function deactivateAgent(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "Not agent owner");
        require(agentCards[tokenId].isActive, "Agent already inactive");

        agentCards[tokenId].isActive = false;
        emit AgentDeactivated(tokenId);
    }

    /**
     * @dev Reactivate an agent
     * @param tokenId Agent token ID
     */
    function reactivateAgent(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "Not agent owner");
        require(!agentCards[tokenId].isActive, "Agent already active");

        agentCards[tokenId].isActive = true;
        emit AgentReactivated(tokenId);
    }

    /**
     * @dev Find agents by capability
     * @param capability The capability to search for
     * @return Array of agent token IDs with the specified capability
     */
    function findAgentsByCapability(string memory capability) 
        external 
        view 
        returns (uint256[] memory) 
    {
        return capabilityIndex[capability];
    }

    /**
     * @dev Get all agents owned by an address
     * @param owner Owner address
     * @return Array of agent token IDs
     */
    function getAgentsByOwner(address owner) 
        external 
        view 
        returns (uint256[] memory) 
    {
        return ownerAgents[owner];
    }

    /**
     * @dev Get agent card details
     * @param tokenId Agent token ID
     * @return AgentCard struct
     */
    function getAgentCard(uint256 tokenId) 
        external 
        view 
        returns (AgentCard memory) 
    {
        require(_exists(tokenId), "Token does not exist");
        return agentCards[tokenId];
    }

    /**
     * @dev Get total number of registered agents
     * @return Total agent count
     */
    function totalAgents() external view returns (uint256) {
        return _tokenIdCounter;
    }

    /**
     * @dev Check if token exists
     */
    function _exists(uint256 tokenId) internal view returns (bool) {
        return agentCards[tokenId].createdAt > 0;
    }

    /**
     * @dev Remove agent from capability index
     */
    function _removeFromCapabilityIndex(string memory capability, uint256 tokenId) private {
        uint256[] storage agents = capabilityIndex[capability];
        for (uint i = 0; i < agents.length; i++) {
            if (agents[i] == tokenId) {
                agents[i] = agents[agents.length - 1];
                agents.pop();
                break;
            }
        }
    }

    /**
     * @dev Override _update to track owner changes
     * In OpenZeppelin v5.0, _update replaces _beforeTokenTransfer and _afterTokenTransfer
     */
    function _update(
        address to,
        uint256 tokenId,
        address auth
    ) internal virtual override returns (address) {
        address from = super._update(to, tokenId, auth);
        
        // Update owner tracking when transferring (not minting or burning)
        if (from != address(0) && to != address(0)) {
            // Update owner in AgentCard
            agentCards[tokenId].owner = to;
            
            // Update ownerAgents mapping
            ownerAgents[to].push(tokenId);
            
            // Remove from previous owner
            uint256[] storage fromAgents = ownerAgents[from];
            for (uint i = 0; i < fromAgents.length; i++) {
                if (fromAgents[i] == tokenId) {
                    fromAgents[i] = fromAgents[fromAgents.length - 1];
                    fromAgents.pop();
                    break;
                }
            }
        }
        
        return from;
    }
}

