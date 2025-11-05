# @a2a/contracts

ERC-8004 Smart Contract Implementation - Agent Identity, Reputation & Validation Registry

## 📋 Contract Architecture

### 1. AgentIdentityRegistry.sol
- ERC-721 based agent identity registry
- Each agent receives a unique NFT ID
- Stores Agent Card information (capabilities, endpoint, metadata URI)
- IPFS integration for decentralized metadata storage
- Owner-based access control

**Key Functions:**
```solidity
function registerAgent(
    string name,
    string description,
    string[] capabilities,
    string endpoint,
    string metadataURI
) external returns (uint256 tokenId)

function getAgentCard(uint256 tokenId) 
    external view returns (AgentCard)

function updateAgent(uint256 tokenId, ...) external
```

### 2. AgentReputationRegistry.sol
- Decentralized reputation system
- Tied to x402 payment proofs to prevent spam
- Calculate and store agent reputation scores
- On-chain feedback with ratings and comments

**Key Functions:**
```solidity
function submitFeedback(
    uint256 agentId,
    uint256 rating,
    string comment,
    bytes32 paymentProof
) external

function getReputationScore(uint256 agentId)
    external view returns (uint256 avgRating, uint256 count)
```

### 3. AgentValidationRegistry.sol
- Third-party validation records
- Supports multiple validation types (TEE, ZK proofs, etc.)
- Enhances agent trustworthiness
- Validator management and permissions

**Key Functions:**
```solidity
function submitValidation(
    uint256 agentId,
    ValidationType validationType,
    bytes proof,
    string metadata
) external

function getValidationStats(uint256 agentId)
    external view returns (ValidationStats)
```

## 🚀 Development

### Prerequisites
- Node.js >= 18.0.0
- pnpm >= 8.0.0

### Installation

```bash
# Install dependencies
pnpm install
```

### Compile Contracts

```bash
# Compile all contracts
pnpm compile

# Clean and recompile
pnpm clean && pnpm compile
```

### Run Tests

```bash
# Run all tests
pnpm test

# Run specific test file
pnpm hardhat test test/AgentIdentityRegistry.test.ts

# Run tests with gas reporting
REPORT_GAS=true pnpm test
```

### Local Development

```bash
# Start local Hardhat node
pnpm node

# In another terminal, deploy contracts
pnpm deploy:local

# Interact with contracts
pnpm hardhat console --network localhost
```

### Deploy to Networks

```bash
# Deploy to Sepolia testnet
pnpm deploy:sepolia

# Deploy to Polygon Mumbai
pnpm deploy:mumbai

# Deploy to mainnet (use with caution!)
pnpm deploy:mainnet
```

## 🧪 Testing

### Test Coverage

```bash
pnpm coverage
```

This generates a coverage report in `coverage/index.html`.

### Gas Report

```bash
REPORT_GAS=true pnpm test
```

Example output:
```
·--------------------------------------|----------------------------|-------------|-----------------------------·
|        Solc version: 0.8.20          ·  Optimizer enabled: true  ·  Runs: 200  ·  Block limit: 30000000 gas  │
·······································|····························|·············|······························
|  Methods                                                                                                      │
··························|············|·············|·············|··············|···············|··············
|  Contract               ·  Method    ·  Min        ·  Max        ·  Avg         ·  # calls      ·  usd (avg)  │
··························|············|·············|·············|··············|···············|··············
|  AgentIdentityRegistry  ·  register  ·     150000  ·     180000  ·      165000  ·           42  ·          -  │
·-------------------------|------------|-------------|-------------|--------------|---------------|-------------·
```

## 🔍 Contract Verification

After deployment, verify contracts on block explorers:

```bash
# Verify on Etherscan (Sepolia)
pnpm hardhat verify --network sepolia DEPLOYED_CONTRACT_ADDRESS "Constructor Arg1" "Arg2"

# Example
pnpm hardhat verify --network sepolia 0x5FbDB2315678afecb367f032d93F642f64180aa3
```

## 📁 Project Structure

```
contracts/
├── contracts/
│   ├── AgentIdentityRegistry.sol       # ERC-721 agent identity
│   ├── AgentReputationRegistry.sol     # Reputation system
│   ├── AgentValidationRegistry.sol     # Validation records
│   └── interfaces/
│       └── IERC8004.sol                # ERC-8004 interface
├── scripts/
│   └── deploy.ts                       # Deployment script
├── test/
│   ├── AgentIdentityRegistry.test.ts
│   ├── AgentReputationRegistry.test.ts
│   └── AgentValidationRegistry.test.ts
├── hardhat.config.ts                   # Hardhat configuration
└── README.md
```

## 🛠️ Hardhat Tasks

### Custom Tasks

```bash
# Get agent info
pnpm hardhat agent-info --token-id 1 --network localhost

# Submit test feedback
pnpm hardhat submit-feedback --agent-id 1 --rating 5 --network localhost
```

### Built-in Tasks

```bash
# List accounts
pnpm hardhat accounts

# Check balance
pnpm hardhat balance --account 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

# Get block number
pnpm hardhat block-number --network localhost
```

## 🔐 Security

### Auditing

Before mainnet deployment:
1. Run all tests with 100% coverage
2. Use static analysis tools (Slither, Mythril)
3. Conduct professional security audit
4. Bug bounty program

### Static Analysis

```bash
# Install Slither
pip3 install slither-analyzer

# Run analysis
slither .

# Generate report
slither . --print human-summary > audit-report.txt
```

## 📊 Gas Optimization

Tips for reducing gas costs:
1. Use `uint256` instead of smaller uints (except in structs)
2. Mark functions as `external` when possible
3. Use `calldata` instead of `memory` for read-only arrays
4. Cache storage variables in memory
5. Use events instead of storage when possible

## 🌐 Multi-chain Deployment

### Supported Networks

- **Local**: Hardhat Network (Chain ID: 31337)
- **Testnet**: Sepolia, Mumbai, Goerli
- **Mainnet**: Ethereum, Polygon, Arbitrum, Optimism, BSC

### Network Configuration

Edit `hardhat.config.ts`:

```typescript
networks: {
  sepolia: {
    url: process.env.SEPOLIA_RPC_URL,
    accounts: [process.env.PRIVATE_KEY],
    chainId: 11155111
  },
  polygon: {
    url: process.env.POLYGON_RPC_URL,
    accounts: [process.env.PRIVATE_KEY],
    chainId: 137
  }
}
```

## 📖 Resources

- [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)
- [Hardhat Documentation](https://hardhat.org/docs)
- [Solidity Documentation](https://docs.soliditylang.org/)

## 🐛 Troubleshooting

### Issue: Compilation fails

```bash
# Clear cache and rebuild
pnpm clean
pnpm compile
```

### Issue: Tests fail with "nonce too low"

```bash
# Restart Hardhat node
# Ctrl+C to stop, then:
pnpm node
```

### Issue: Deployment fails

Check:
- Sufficient ETH for gas fees
- Correct RPC URL in .env
- Network is accessible
- Private key is valid

---

**Built with Hardhat and OpenZeppelin for security and reliability** 🔒⛓️
