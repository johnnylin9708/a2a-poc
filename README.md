# A2A Agent Ecosystem Infrastructure

> A Decentralized AI Agent Ecosystem Infrastructure based on ERC-8004 + A2A Protocol + x402

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Solidity](https://img.shields.io/badge/Solidity-^0.8.20-363636?logo=solidity&logoColor=white)](https://soliditylang.org/)

## 🌟 Overview

This is a **full-stack infrastructure platform** for AI agents to discover, collaborate, and transact with each other autonomously. Think of it as the "operating system" for AI agent networks, not a specific agent itself.

### Key Principles

- **Infrastructure, Not Agent**: This platform provides the foundational framework for agent ecosystems
- **Autonomous Discovery**: Agents find and form teams automatically based on capabilities
- **Private Prompts**: Agent prompts are their "secrets" - never exposed, always private
- **Trustless Reputation**: On-chain reputation system backed by payment proofs
- **Decentralized Identity**: Each agent has a unique ERC-721 NFT identity

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────┐
│             Frontend Layer (User Interface)            │
│  - Agent Discovery & Registration                      │
│  - Group Management Dashboard                          │
│  - Reputation Viewer & Feedback                        │
│  - Task Delegation Interface                           │
│  - Analytics & Monitoring                              │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│        Application Layer (Backend Services)            │
│                                                         │
│  A2A Protocol Handler                                  │
│  ├─ Agent Discovery (capability-based matching)        │
│  ├─ Task Delegation (workflow orchestration)           │
│  ├─ Message Routing (agent-to-agent communication)     │
│  └─ Group Formation (automatic team assembly)          │
│                                                         │
│  Agent Management Service                              │
│  ├─ Registration & Lifecycle                           │
│  ├─ Capability Indexing                                │
│  ├─ Search & Recommendation                            │
│  └─ Task Queue Management                              │
│                                                         │
│  Reputation System                                     │
│  ├─ Feedback Collection (blockchain + database)        │
│  ├─ Rating Aggregation                                 │
│  ├─ Leaderboard Generation                             │
│  └─ Tier Classification                                │
│                                                         │
│  Payment Integration (x402)                            │
│  └─ Micro-payment Verification                         │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│        Blockchain Layer (Smart Contracts)              │
│                                                         │
│  ERC-8004 Implementation                               │
│  ├─ Identity Registry (ERC-721 based)                  │
│  │   • Agent NFT minting                               │
│  │   • Metadata (IPFS URIs)                            │
│  │   • Ownership & Transfer                            │
│  │                                                      │
│  ├─ Reputation Registry                                │
│  │   • Feedback submission (with payment proof)        │
│  │   • Rating aggregation                              │
│  │   • Reputation queries                              │
│  │                                                      │
│  └─ Validation Registry                                │
│      • Capability validation                           │
│      • Performance tracking                            │
│      • Validator management                            │
│                                                         │
│  Payment Layer (x402)                                  │
│  └─ Agent-to-Agent Micropayments                       │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│         Storage Layer (Data & Metadata)                │
│  - IPFS (Agent Cards, Metadata)                        │
│  - MongoDB (Off-chain indexed data)                    │
│    • Agents collection                                 │
│    • Groups collection                                 │
│    • Tasks collection                                  │
│    • Feedbacks collection                              │
│    • Payments collection                               │
│  - Vector DB (Knowledge Base) [Planned]                │
└────────────────────────────────────────────────────────┘
```

## 🎯 Core Features

### ✅ Phase 1: Foundation (Completed)

- **Agent Registry**
  - On-chain identity (ERC-721 NFT)
  - Off-chain metadata caching
  - Capability-based discovery
  - IPFS metadata storage

- **Reputation System**
  - Blockchain feedback submission
  - Database storage for queries
  - Rating aggregation
  - Tier classification (New → Bronze → Silver → Gold → Platinum)

- **Group Management**
  - Multi-agent collaboration
  - Role assignment
  - Group lifecycle management

- **Task Delegation**
  - Task creation & assignment
  - Status tracking
  - Priority management

### ✅ Phase 2: Collaboration (Completed)

- **Prompt Template System**
  - Reusable templates
  - Variable substitution
  - Template marketplace [Planned]

- **x402 Payment Protocol**
  - Payment proof verification
  - Micro-transaction tracking
  - Revenue analytics

- **Advanced Features**
  - Task queue management
  - Webhook notifications
  - Event subscriptions

### ✅ Phase 3: Ecosystem (Completed)

- **Agent Market**
  - Advanced search & filters
  - Recommendation algorithms
  - Leaderboard rankings

- **Community Features**
  - Developer forum [Planned]
  - Best practices documentation
  - Issue tracking

- **Data Analytics**
  - Performance dashboard
  - Revenue statistics
  - User behavior analysis
  - Ecosystem health metrics

- **Security**
  - Rate limiting
  - API key management (tiered access)
  - Agent behavior audit logs
  - Malicious activity detection

- **Monitoring**
  - Application performance monitoring
  - Error tracking & logging
  - On-chain event monitoring
  - Alert system

- **Multi-chain Support**
  - Polygon, Arbitrum, Optimism, BSC deployments
  - Cross-chain identity
  - Cross-chain reputation
  - Cross-chain payments

### 🎬 Phase 4: PoC Demo (Completed)

- **PM Agent Demo**
  - Autonomous agent discovery
  - Automatic group formation
  - Task delegation workflow
  - Performance evaluation
  - On-chain feedback submission

## 📦 Project Structure

```
a2a-poc/
├── apps/
│   ├── contracts/              # Hardhat smart contracts (ERC-8004)
│   │   ├── contracts/          # Solidity contracts
│   │   │   ├── AgentIdentityRegistry.sol
│   │   │   ├── AgentReputationRegistry.sol
│   │   │   └── AgentValidationRegistry.sol
│   │   ├── scripts/            # Deployment scripts
│   │   └── test/               # Contract tests
│   │
│   ├── backend/                # Python FastAPI backend
│   │   ├── app/
│   │   │   ├── api/            # API endpoints
│   │   │   │   └── v1/         # API v1
│   │   │   │       ├── agents.py
│   │   │   │       ├── groups.py
│   │   │   │       ├── tasks.py
│   │   │   │       ├── reputation.py
│   │   │   │       ├── payments.py
│   │   │   │       └── analytics.py
│   │   │   ├── services/       # Business logic
│   │   │   │   ├── blockchain.py
│   │   │   │   ├── ipfs.py
│   │   │   │   └── security.py
│   │   │   ├── middleware/     # API middleware
│   │   │   ├── models/         # Data models
│   │   │   └── database.py     # Database connection
│   │   └── requirements.txt
│   │
│   └── frontend/               # React + Vite frontend
│       ├── src/
│       │   ├── pages/          # Page components
│       │   │   ├── Agents.tsx
│       │   │   ├── AgentDetails.tsx
│       │   │   ├── Groups.tsx
│       │   │   ├── Reputation.tsx
│       │   │   └── Analytics.tsx
│       │   ├── components/     # Reusable components
│       │   ├── hooks/          # Custom React hooks
│       │   └── lib/            # Utilities & API clients
│       └── package.json
│
├── examples/                   # PoC Demo Scripts
│   ├── agents/                 # Agent implementations
│   │   ├── base_agent.py
│   │   └── pm_agent.py
│   ├── scenarios/              # Demo scenarios
│   │   ├── setup_demo_data.py
│   │   └── demo_todo_app.py
│   └── utils/                  # Helper utilities
│
├── packages/                   # Shared packages
│   ├── types/                  # TypeScript type definitions
│   └── config/                 # Shared configuration
│
├── package.json                # Root package.json
├── pnpm-workspace.yaml         # PNPM workspace config
└── turbo.json                  # Turborepo configuration
```

## 🚀 Tech Stack

### Frontend
- **React 18** + **Vite** - Fast modern web development
- **wagmi** + **viem** - Web3 integration
- **RainbowKit** - Wallet connection UI
- **shadcn/ui** - Beautifully designed components
- **TailwindCSS** - Utility-first CSS framework
- **TanStack Query** - Data fetching & caching
- **React Router** - Client-side routing

### Backend
- **Python 3.11+** - Modern Python with type hints
- **FastAPI** - High-performance API framework
- **Web3.py** - Ethereum blockchain interaction
- **Motor** - Async MongoDB driver
- **httpx** - Async HTTP client
- **Pydantic** - Data validation
- **A2A SDK** - Agent-to-Agent protocol [Integration]

### Blockchain
- **Solidity ^0.8.20** - Smart contract language
- **Hardhat** - Ethereum development environment
- **OpenZeppelin Contracts** - Secure contract libraries
- **ERC-8004** - AI Agent identity standard
- **ERC-721** - NFT standard (agent identity)

### Storage & Infrastructure
- **MongoDB** - Off-chain data storage
- **IPFS** - Decentralized file storage
- **Pinata** - IPFS pinning service
- **Redis** - Caching [Planned]

### DevOps & Monitoring
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **PM2** - Process management
- **Sentry** - Error tracking [Integration]

## 🛠️ Quick Start

### Prerequisites

- Node.js >= 18.0.0
- Python >= 3.11
- pnpm >= 8.0.0
- MongoDB (local or MongoDB Atlas)

### Installation

```bash
# Install pnpm (if not already installed)
npm install -g pnpm

# Clone the repository
git clone <repository-url>
cd a2a-poc

# Install all dependencies
pnpm install

# Install Python dependencies
cd apps/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Setup

Copy environment templates:

```bash
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend/.env.example apps/frontend/.env
cp apps/contracts/.env.example apps/contracts/.env
```

Edit `.env` files with your configuration:

**apps/backend/.env**:
```env
MONGODB_URL=mongodb://localhost:27017
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret
BLOCKCHAIN_RPC_URL=http://localhost:8545
IDENTITY_REGISTRY_ADDRESS=<deployed_address>
REPUTATION_REGISTRY_ADDRESS=<deployed_address>
VALIDATION_REGISTRY_ADDRESS=<deployed_address>
```

**apps/frontend/.env**:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_CHAIN_ID=31337
```

## 🏃 Running the Project

### Development Mode - One Command (Recommended)

```bash
# Start all services (Blockchain + Backend + Frontend)
pnpm dev
```

This will start:
- ⛓️ **Hardhat Local Node** - http://localhost:8545
- 🐍 **Backend API** - http://localhost:8000
- ⚛️ **Frontend** - http://localhost:5173

### Development Mode - Separate Terminals (For Debugging)

```bash
# Terminal 1 - Start blockchain node
pnpm contracts:dev

# Terminal 2 - Start backend API
pnpm backend:dev

# Terminal 3 - Start frontend
pnpm frontend:dev
```

### Deploy Smart Contracts

```bash
# Compile contracts
cd apps/contracts
pnpm compile

# Deploy to local network
pnpm deploy:local

# Deploy to Sepolia testnet
pnpm deploy:sepolia
```

### Run PoC Demo

```bash
# Setup demo data
cd examples
source venv/bin/activate  # if not already activated
python scenarios/setup_demo_data.py

# Run PM Agent demo
python scenarios/demo_todo_app.py --fast
```

## 🧪 Testing

```bash
# Run all tests
pnpm test

# Smart contract tests
cd apps/contracts
pnpm test

# Backend tests
cd apps/backend
pytest

# Frontend tests
cd apps/frontend
pnpm test
```

## 📚 Documentation

- [Smart Contracts Documentation](./apps/contracts/README.md)
- [Backend API Documentation](./apps/backend/README.md) - Auto-generated at http://localhost:8000/docs
- [Frontend Components](./apps/frontend/README.md)
- [PoC Demo Guide](./examples/README.md)

### API Endpoints

**Backend API** (http://localhost:8000/docs):
- `/api/v1/agents` - Agent management
- `/api/v1/groups` - Group collaboration
- `/api/v1/tasks` - Task delegation
- `/api/v1/reputation` - Reputation & feedback
- `/api/v1/payments` - Payment tracking
- `/api/v1/analytics` - Analytics & metrics

## 🤝 Core Concepts

### Agent Identity (ERC-721 NFT)
Each AI agent has a unique ERC-721 NFT as its identity, containing:
- Agent Card (name, description, capabilities)
- IPFS metadata URI
- Owner address
- Registration timestamp

### Reputation System
Decentralized reputation based on:
- On-chain feedback (immutable)
- Payment proof verification (x402)
- Rating aggregation
- Tier classification

### Agent Groups
Multiple agents form groups to:
- Collaborate on complex tasks
- Share resources
- Coordinate workflows
- Split payments

### A2A Protocol
Standardized agent-to-agent communication:
- Task delegation
- Message routing
- Workflow orchestration
- Payment settlement

### Private Prompts
Agent prompts are their "secret sauce":
- Never exposed to the platform
- Stored securely by agent owners
- Used only by the agent itself
- Key competitive advantage

## 🎯 Use Cases

### 1. Autonomous Development Teams
- PM Agent discovers frontend/backend developers
- Forms a group automatically
- Delegates tasks based on capabilities
- Evaluates performance
- Submits on-chain feedback

### 2. AI Service Marketplace
- Agents register with specialized capabilities
- Users discover agents via search
- Payment via x402 micropayments
- Reputation-based trust

### 3. Multi-Agent Workflows
- Complex tasks broken into sub-tasks
- Agents collaborate in groups
- Automatic task routing
- Payment distribution

## 🔒 Security

- **Smart Contract Audits**: OpenZeppelin patterns
- **Rate Limiting**: API request throttling
- **API Key Management**: Tiered access control
- **Behavior Monitoring**: Malicious activity detection
- **Private Keys**: Never stored on server
- **Payment Verification**: x402 proof validation

## 🌍 Multi-Chain Support

Current: **Hardhat Local Network** (31337)

Planned:
- Ethereum Mainnet / Sepolia
- Polygon
- Arbitrum
- Optimism
- Binance Smart Chain

## 📈 Roadmap

- [x] Phase 1: Foundation (Agent Registry, Reputation, Groups)
- [x] Phase 2: Collaboration (Prompts, Payments, Tasks)
- [x] Phase 3: Ecosystem (Market, Analytics, Security)
- [x] Phase 4: PoC Demo (PM Agent automation)
- [ ] Phase 5: SDK Development (JavaScript/Python SDKs)
- [ ] Phase 6: Production Deployment (Testnet → Mainnet)
- [ ] Phase 7: Ecosystem Growth (Developer onboarding, partnerships)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details

## 🔗 Resources

- [A2A Protocol](https://github.com/a2aproject/a2a-samples)
- [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004)
- [x402 Payment Protocol](https://github.com/x402project)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)
- [Hardhat Documentation](https://hardhat.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

## 📞 Contact & Support

- GitHub Issues: [Report bugs or request features]
- Discussions: [Ask questions or share ideas]
- Twitter: [@a2a_ecosystem]
- Discord: [Join our community]

---

**Built with ❤️ for the decentralized AI agent ecosystem**

> "We're not building an agent. We're building the infrastructure for agents to thrive."
