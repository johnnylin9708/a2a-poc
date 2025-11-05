# @a2a/backend

Fast API backend for the A2A Agent Ecosystem Infrastructure

## 🌟 Features

- **Agent Management API** - Register, query, and update agents
- **A2A Protocol Handler** - Agent-to-agent communication protocol
- **Blockchain Integration** - Interact with ERC-8004 smart contracts
- **MongoDB Storage** - Off-chain data storage and caching
- **IPFS Integration** - Decentralized file storage
- **RESTful API** - Complete REST API with auto-generated docs
- **Reputation System** - On-chain reputation with database caching
- **Payment Integration** - x402 micro-payment verification
- **Rate Limiting** - API throttling and abuse prevention
- **API Key Management** - Tiered access control
- **Analytics** - Performance metrics and ecosystem health
- **Security** - Behavior auditing and malicious activity detection

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI application entry
│   ├── config.py                  # Configuration management
│   ├── database.py                # MongoDB connection
│   ├── api/
│   │   └── v1/
│   │       ├── agents.py          # Agent APIs
│   │       ├── groups.py          # Group management APIs
│   │       ├── tasks.py           # Task delegation APIs
│   │       ├── reputation.py      # Reputation system APIs
│   │       ├── payments.py        # Payment tracking APIs
│   │       ├── analytics.py       # Analytics APIs
│   │       └── security.py        # Security APIs
│   ├── services/
│   │   ├── blockchain.py          # Blockchain service (Web3.py)
│   │   ├── ipfs.py                # IPFS service (Pinata)
│   │   ├── security.py            # Security monitoring
│   │   └── analytics.py           # Analytics service
│   ├── middleware/
│   │   ├── rate_limit.py          # Rate limiting
│   │   ├── auth.py                # Authentication
│   │   └── logging.py             # Request logging
│   ├── models/
│   │   ├── agent.py               # Agent data model
│   │   ├── group.py               # Group data model
│   │   ├── task.py                # Task data model
│   │   ├── feedback.py            # Feedback data model
│   │   └── payment.py             # Payment data model
│   └── schemas/
│       ├── agent.py               # Agent Pydantic schemas
│       ├── group.py               # Group Pydantic schemas
│       ├── task.py                # Task Pydantic schemas
│       └── reputation.py          # Reputation Pydantic schemas
├── tests/
│   ├── test_agents.py
│   ├── test_blockchain.py
│   ├── test_reputation.py
│   └── test_api.py
├── logs/                          # Application logs
├── venv/                          # Python virtual environment
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python >= 3.11
- MongoDB (local or Atlas)
- Hardhat node running (for blockchain)

### Installation

```bash
# Navigate to backend directory
cd apps/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=a2a_ecosystem

# Blockchain (Hardhat Local)
BLOCKCHAIN_RPC_URL=http://localhost:8545
CHAIN_ID=31337

# Contract Addresses (update after deployment)
IDENTITY_REGISTRY_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
REPUTATION_REGISTRY_ADDRESS=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
VALIDATION_REGISTRY_ADDRESS=0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0

# IPFS (Pinata)
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
API_V1_PREFIX=/api/v1

# Security
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Running the Server

```bash
# Development mode with auto-reload
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Documentation

### Auto-Generated Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API testing
  - Request/response examples
  - Schema definitions

- **ReDoc**: http://localhost:8000/redoc
  - Alternative documentation format
  - Better for reading
  - Print-friendly

### API Endpoints Overview

#### Agent Management
```
GET    /api/v1/agents/           # List all agents
POST   /api/v1/agents/           # Register new agent
GET    /api/v1/agents/{id}       # Get agent details
PUT    /api/v1/agents/{id}       # Update agent
DELETE /api/v1/agents/{id}       # Delete agent
POST   /api/v1/agents/discover   # Discover agents by capabilities
GET    /api/v1/agents/search     # Search agents (advanced)
```

#### Group Management
```
GET    /api/v1/groups/           # List all groups
POST   /api/v1/groups/           # Create new group
GET    /api/v1/groups/{id}       # Get group details
PUT    /api/v1/groups/{id}       # Update group
DELETE /api/v1/groups/{id}       # Delete group
POST   /api/v1/groups/{id}/members  # Add member
DELETE /api/v1/groups/{id}/members/{agent_id}  # Remove member
```

#### Task Management
```
GET    /api/v1/tasks/            # List tasks
POST   /api/v1/tasks/delegate    # Delegate new task
GET    /api/v1/tasks/{id}        # Get task details
PUT    /api/v1/tasks/{id}        # Update task status
GET    /api/v1/tasks/agent/{id}  # Get agent's tasks
```

#### Reputation System
```
GET    /api/v1/reputation/{agent_id}         # Get agent reputation
POST   /api/v1/reputation/feedback           # Submit feedback
GET    /api/v1/reputation/{agent_id}/history # Get feedback history
GET    /api/v1/reputation/all-feedbacks      # Get all feedbacks
GET    /api/v1/reputation/leaderboard/top    # Get leaderboard
```

#### Payment Tracking
```
GET    /api/v1/payments/                     # List payments
POST   /api/v1/payments/                     # Record payment
GET    /api/v1/payments/{id}                 # Get payment details
GET    /api/v1/payments/agent/{agent_id}    # Get agent payments
GET    /api/v1/payments/stats                # Payment statistics
```

#### Analytics
```
GET    /api/v1/analytics/dashboard           # Dashboard metrics
GET    /api/v1/analytics/agents              # Agent statistics
GET    /api/v1/analytics/ecosystem           # Ecosystem health
GET    /api/v1/analytics/revenue             # Revenue analytics
```

#### Security & Admin
```
POST   /api/v1/security/api-keys             # Generate API key
GET    /api/v1/security/audit-logs           # Get audit logs
GET    /api/v1/security/rate-limits          # Check rate limits
```

### Example API Calls

#### Register an Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Agent",
    "description": "AI assistant for data analysis",
    "capabilities": ["python", "data-science", "ml"],
    "endpoint": "https://myagent.example.com/api",
    "owner_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "private_key": "0x..."
  }'
```

#### Discover Agents

```bash
curl -X POST "http://localhost:8000/api/v1/agents/discover" \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "react",
    "min_reputation": 4.0,
    "is_active": true,
    "limit": 10
  }'
```

#### Create a Group

```bash
curl -X POST "http://localhost:8000/api/v1/groups/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Development Team",
    "description": "Full-stack development group",
    "admin_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "initial_agents": [1, 2, 3]
  }'
```

#### Submit Feedback

```bash
curl -X POST "http://localhost:8000/api/v1/reputation/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 1,
    "rating": 5,
    "comment": "Excellent work!",
    "reviewer_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "payment_proof": "0xabcd...",
    "private_key": "0x..."
  }'
```

## 🏗️ Architecture

### Tech Stack

- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation using Python type hints
- **Motor** - Async MongoDB driver
- **Web3.py** - Ethereum blockchain interaction
- **httpx** - Async HTTP client
- **python-dotenv** - Environment variable management
- **Rich** - Beautiful terminal formatting

### Design Patterns

#### Layered Architecture
```
API Layer (FastAPI Routes)
    ↓
Service Layer (Business Logic)
    ↓
Data Layer (MongoDB + Blockchain)
```

#### Dependency Injection
FastAPI's dependency injection system for clean, testable code.

#### Async/Await
All I/O operations use async/await for better performance.

#### Lazy Loading
Blockchain connections initialized on-demand to avoid startup delays.

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_agents.py
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Test Categories

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# API tests
pytest tests/api/
```

## 🔒 Security

### Rate Limiting

Default limits (configurable in .env):
- 60 requests per minute
- 1000 requests per hour

Exceeding limits returns `429 Too Many Requests`.

### API Key Management

Generate API keys with different tiers:

```bash
curl -X POST "http://localhost:8000/api/v1/security/api-keys" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key",
    "tier": "premium"
  }'
```

Tiers:
- **free**: 100 req/hour
- **basic**: 1000 req/hour
- **premium**: 10000 req/hour

### Audit Logging

All sensitive operations are logged:
- Agent registration
- Feedback submission
- Payment recording
- Group modifications

View audit logs:
```bash
curl "http://localhost:8000/api/v1/security/audit-logs?limit=50"
```

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "environment": "development",
  "blockchain": {
    "provider": "http://localhost:8545",
    "chain_id": 31337
  }
}
```

### Application Logs

Logs are stored in `logs/app.log`:

```bash
tail -f logs/app.log
```

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Metrics

Access metrics at:
```bash
curl http://localhost:8000/api/v1/analytics/dashboard
```

## 🐛 Troubleshooting

### Issue: "MongoDB connection failed"

**Solution**:
```bash
# Check MongoDB is running
mongosh --eval "db.runCommand({ ping: 1 })"

# Start MongoDB
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod  
# Windows: net start MongoDB
```

### Issue: "Blockchain connection failed"

**Solution**:
```bash
# Check Hardhat is running
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'

# Start Hardhat
cd ../contracts
pnpm hardhat node
```

### Issue: "Contract not deployed"

**Solution**:
```bash
# Deploy contracts
cd ../contracts
pnpm deploy:local

# Update .env with new addresses
```

### Issue: "IPFS upload failed"

**Solution**:
- Verify Pinata API keys in `.env`
- Check Pinata dashboard: https://pinata.cloud
- Ensure file size < 100MB

## 🚀 Deployment

### Production Setup

1. **Use Production MongoDB**:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
```

2. **Configure Production Blockchain**:
```env
BLOCKCHAIN_RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY
CHAIN_ID=1  # Ethereum Mainnet
```

3. **Set Environment**:
```env
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

4. **Use Production Server**:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t a2a-backend .
docker run -p 8000:8000 --env-file .env a2a-backend
```

## 📝 Development

### Code Style

We follow PEP 8 with:
```bash
# Format code
black app/

# Check linting
flake8 app/

# Type checking
mypy app/
```

### Adding New Endpoints

1. Create route in `app/api/v1/`
2. Add business logic in `app/services/`
3. Define Pydantic schemas in `app/schemas/`
4. Write tests in `tests/`

Example:
```python
# app/api/v1/my_endpoint.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/my-resource")
async def get_resource():
    return {"message": "Hello World"}
```

## 🔗 Related

- [Main README](../../README.md)
- [Smart Contracts](../contracts/README.md)
- [Frontend](../frontend/README.md)
- [PoC Demo](../../examples/README.md)

---

**Built with FastAPI for high performance and developer experience** ⚡🐍
