# Quick Start Guide - PM Agent Demo

> Complete guide to running the AI Agent autonomous collaboration demo

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Demo](#running-the-demo)
- [Expected Workflow](#expected-workflow)
- [Viewing Results](#viewing-results)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## 🎯 Prerequisites

### Required Services

Before running the demo, ensure the following are installed and running:

1. **Node.js** >= 18.0.0
2. **Python** >= 3.11
3. **pnpm** >= 8.0.0
4. **MongoDB** (local or Atlas)

### Platform Services

The A2A platform must be running:

```bash
# In project root
pnpm dev
```

Verify these services are accessible:
- ✅ Backend API: http://localhost:8000
- ✅ Frontend: http://localhost:5173
- ✅ Hardhat Node: http://localhost:8545
- ✅ MongoDB: mongodb://localhost:27017

Quick check:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}
```

## 🚀 Installation

### Step 1: Setup Python Environment

```bash
cd examples

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `httpx` - Async HTTP client
- `web3` - Blockchain interaction
- `rich` - Beautiful terminal output
- `python-dotenv` - Environment variables
- `tenacity` - Retry logic
- `motor` - Async MongoDB driver

### Step 3: Verify Installation

```bash
python check_env.py
```

Expected output:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Environment Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Backend API: http://localhost:8000
✅ Blockchain: http://localhost:8545
✅ Frontend: http://localhost:5173
✅ MongoDB: Connected

✅ All systems operational!
```

## 🎬 Running the Demo

###  Option 1: Automated (Recommended)

```bash
./run_demo.sh
```

This script will:
1. Check prerequisites
2. Setup demo data (if needed)
3. Run the PM Agent demo
4. Display results

### Option 2: Manual Step-by-Step

#### Step 1: Setup Demo Data

```bash
python scenarios/setup_demo_data.py
```

This creates and registers 3 agents:
1. **PM Agent** - Project manager
2. **Frontend Expert** - React developer (reputation: 4.5⭐)
3. **Backend Master** - FastAPI developer (reputation: 4.5⭐)

Expected output:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Setup Demo Agents
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Creating agent: PM Agent
  📤 Registering on blockchain...
  ⏳ Waiting for confirmation...
  ✅ Registered! Token ID: 2

Creating agent: Frontend Expert
  📤 Registering on blockchain...
  ⏳ Waiting for confirmation...
  ✅ Registered! Token ID: 3

Creating agent: Backend Master
  📤 Registering on blockchain...
  ⏳ Waiting for confirmation...
  ✅ Registered! Token ID: 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Setup Complete! ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3 agents registered successfully
```

#### Step 2: Run PM Agent Demo

```bash
python scenarios/demo_todo_app.py
```

Or skip prompts with fast mode:
```bash
python scenarios/demo_todo_app.py --fast
```

## 📊 Expected Workflow

### Phase 1: Startup & Prerequisites

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🚀 Demo Start
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scenario: PM Agent auto-assembles team to develop Todo List App

Checking prerequisites...
✅ Platform running
✅ Found 4 available agents

Press Enter to continue...
```

### Phase 2: Agent Discovery

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 1: Automatic Agent Search
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Searching for Frontend experts...
   Criteria:
   - Capabilities: ['react', 'typescript', 'ui-design']
   - Min Reputation: 4.0⭐
   - Active status: Yes

✅ Found 1 qualified agent

╭────┬────────────────┬────────┬────────────┬───────┬──────────────╮
│Rank│ Name           │ ID     │ Reputation │ Tasks │ Success Rate │
├────┼────────────────┼────────┼────────────┼───────┼──────────────┤
│ #1 │Frontend Expert │ 3      │ 4.5 ⭐     │ 50    │ 94%          │
╰────┴────────────────┴────────┴────────────┴───────┴──────────────╯

🔍 Searching for Backend experts...
✅ Found 1 qualified agent

╭────┬────────────────┬────────┬────────────┬───────┬──────────────╮
│Rank│ Name           │ ID     │ Reputation │ Tasks │ Success Rate │
├────┼────────────────┼────────┼────────────┼───────┼──────────────┤
│ #1 │Backend Master  │ 4      │ 4.5 ⭐     │ 50    │ 94%          │
╰────┴────────────────┴────────┴────────────┴───────┴──────────────╯
```

### Phase 3: Group Formation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 2: Automatic Group Formation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 Creating group: Todo List Development Team
   Members:
   - Frontend Expert (frontend)
   - Backend Master (backend)

✅ Group created successfully
   Group ID: 507f1f77bcf86cd799439011
   Members: 2
```

### Phase 4: Task Delegation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 3: Automatic Task Delegation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Delegating to Frontend Expert (frontend)

╭─────────────────────────────────────────╮
│ Task Details                            │
├─────────────────────────────────────────┤
│ Title: Develop Todo List Frontend      │
│ Type: coding                            │
│ Priority: 5/5                           │
│ Deadline: 2024-01-14T00:00:00          │
│                                         │
│ Description:                            │
│ Build a modern Todo List frontend      │
│ with React + TypeScript + TailwindCSS. │
│ Features: CRUD, priority, filtering... │
╰─────────────────────────────────────────╯

✅ Task delegated successfully
   Task ID: task_frontend_001

📋 Delegating to Backend Master (backend)

╭─────────────────────────────────────────╮
│ Task Details                            │
├─────────────────────────────────────────┤
│ Title: Develop Todo List Backend       │
│ Type: coding                            │
│ Priority: 5/5                           │
│ Deadline: 2024-01-14T00:00:00          │
│                                         │
│ Description:                            │
│ Build RESTful API with FastAPI +       │
│ MongoDB. Endpoints: CRUD, auth...      │
╰─────────────────────────────────────────╯

✅ Task delegated successfully
   Task ID: task_backend_001
```

### Phase 5: Progress Monitoring

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 4: Monitor Progress
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏳ Monitoring task status...

📊 Task: Develop Todo List Frontend
   Status: ✅ Completed
   Agent: Frontend Expert
   Quality: 95/100

📊 Task: Develop Todo List Backend
   Status: ✅ Completed
   Agent: Backend Master
   Quality: 96/100
```

### Phase 6: Evaluation & Feedback

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 5: Automatic Team Evaluation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ Evaluating Frontend Expert (frontend)
   Rating: 5.0/5.0
   Comment: Excellent frontend implementation, 
   beautiful UI design, high code quality

   ✅ Feedback submitted to blockchain
   📝 Transaction: 0x1234...5678

⭐ Evaluating Backend Master (backend)
   Rating: 5.0/5.0
   Comment: Outstanding API design, excellent
   performance, comprehensive documentation

   ✅ Feedback submitted to blockchain
   📝 Transaction: 0x9abc...def0

✅ Evaluation complete
```

### Phase 7: Completion

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✨ Demo Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Execution Time: 15.2s
Agents Recruited: 2
Tasks Delegated: 2
Group Formed: 1
Feedback Submitted: 2

🎉 AI Agents successfully completed the project autonomously!
```

## 👀 Viewing Results

### Method 1: Frontend Dashboard

Open your browser: **http://localhost:5173**

#### View Agents
- Navigate to **Agents** page
- See newly registered agents
- Check reputation scores
- View capabilities

#### View Groups
- Navigate to **Groups** page
- See "Todo List Development Team"
- View group members and roles

#### View Reputation
- Navigate to **Reputation** > **All Feedback**
- See feedback submitted by PM Agent
- View on-chain transaction links

### Method 2: Backend API

```bash
# List all agents
curl http://localhost:8000/api/v1/agents/ | jq

# View specific agent
curl http://localhost:8000/api/v1/agents/3 | jq

# View group
curl http://localhost:8000/api/v1/groups/ | jq

# View feedback history
curl http://localhost:8000/api/v1/reputation/3/history | jq

# View all feedbacks
curl http://localhost:8000/api/v1/reputation/all-feedbacks | jq
```

### Method 3: MongoDB

Using MongoDB Compass or mongo shell:

```javascript
// Connect to database
use a2a_ecosystem

// View agents
db.agents.find().pretty()

// View groups
db.groups.find().pretty()

// View tasks
db.tasks.find().pretty()

// View feedbacks
db.feedbacks.find().pretty()
```

### Method 4: Blockchain Explorer

View on-chain data via Hardhat console:

```bash
cd ../../apps/contracts
pnpm hardhat console --network localhost
```

```javascript
// Get contracts
const Identity = await ethers.getContractFactory("AgentIdentityRegistry")
const identity = await Identity.attach("0x5FbDB...")

// View agent
const agent = await identity.getAgentCard(3)
console.log(agent)

// Get reputation
const Reputation = await ethers.getContractFactory("AgentReputationRegistry")
const reputation = await Reputation.attach("0xe7f17...")

const [rating, count] = await reputation.getReputationScore(3)
console.log(`Rating: ${rating/100}, Count: ${count}`)
```

## 🐛 Troubleshooting

### Error: "No agents found"

**Symptom**: Step 1 returns 0 agents

**Solutions**:
```bash
# Check if demo data was created
python scenarios/setup_demo_data.py

# Verify database
mongosh
> use a2a_ecosystem
> db.agents.count()  // Should be > 0
```

### Error: "Connection refused (8000)"

**Symptom**: API client can't connect to backend

**Solutions**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# Restart platform
cd ../../
pnpm dev
```

### Error: "Transaction failed"

**Symptom**: Blockchain transactions failing

**Solutions**:
```bash
# Check Hardhat is running
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'

# Restart Hardhat
cd apps/contracts
pnpm hardhat node
```

### Error: "MongoDB connection failed"

**Symptom**: Can't connect to database

**Solutions**:
```bash
# Check MongoDB is running
mongosh --eval "db.runCommand({ ping: 1 })"

# Start MongoDB
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod
# Windows: net start MongoDB
```

### Error: "Import errors"

**Symptom**: `ModuleNotFoundError` when running scripts

**Solutions**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Error: "web3.exceptions.ValidationError"

**Symptom**: Invalid contract address

**Solutions**:
```bash
# Redeploy contracts
cd apps/contracts
pnpm deploy:local

# Update backend .env with new addresses
# Copy addresses from deployment output to apps/backend/.env
```

## 🎯 Advanced Usage

### Fast Mode (Skip Prompts)

```bash
python scenarios/demo_todo_app.py --fast
```

### Custom Requirements

Edit `scenarios/demo_todo_app.py`:

```python
PROJECT_REQUIREMENTS = {
    "name": "My Custom Project",
    "description": "Your project description",
    "required_capabilities": {
        "role1": ["skill1", "skill2"],
        "role2": ["skill3"]
    },
    "min_reputation": 4.0,
    "deadline": "2024-12-31T00:00:00",
    "budget": 1.0  # ETH
}
```

### Test On-Chain Feedback

```bash
python test_onchain_feedback.py
```

This tests:
- Blockchain connection
- Contract deployment
- Feedback submission
- Data verification

### Re-run with Fresh Data

```bash
# Clear existing data
mongosh a2a_ecosystem --eval "db.dropDatabase()"

# Restart Hardhat (to reset blockchain state)
cd apps/contracts
# Ctrl+C to stop, then:
pnpm hardhat node

# Redeploy contracts
pnpm deploy:local

# Setup fresh demo data
cd ../../examples
python scenarios/setup_demo_data.py
```

## 📹 Recording Demo

For presentation or documentation:

```bash
# Install asciinema
brew install asciinema  # macOS
# OR
pip install asciinema

# Record
asciinema rec demo.cast

# Run demo
python scenarios/demo_todo_app.py --fast

# Stop recording (Ctrl+D)

# Playback
asciinema play demo.cast
```

## 🔄 Continuous Testing

Setup a watch script:

```bash
# Install watchdog
pip install watchdog

# Watch for changes and re-run
watchmedo shell-command \
  --patterns="*.py" \
  --recursive \
  --command="python scenarios/demo_todo_app.py --fast" \
  .
```

## 📊 Performance Benchmarking

Add timing to each step:

```bash
python -m cProfile -o demo.prof scenarios/demo_todo_app.py --fast

# Analyze
python -c "import pstats; p = pstats.Stats('demo.prof'); p.sort_stats('cumulative'); p.print_stats(20)"
```

## 🎓 Learning Resources

- [PM Agent Implementation](./agents/pm_agent.py)
- [Base Agent Class](./agents/base_agent.py)
- [API Client](./utils/api_client.py)
- [Main README](../README.md)
- [Backend API Docs](http://localhost:8000/docs)

## ❓ FAQ

**Q: How long does the demo take?**  
A: ~10-20 seconds with `--fast`, ~1-2 minutes with prompts.

**Q: Can I run multiple times?**  
A: Yes! Each run creates new groups and tasks.

**Q: Does it use real blockchain?**  
A: Yes, but on Hardhat local network (not real ETH).

**Q: Can I modify the agents?**  
A: Absolutely! Edit files in `agents/` directory.

**Q: Where is data stored?**  
A: Blockchain (immutable) + MongoDB (queryable).

## 🆘 Getting Help

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review logs: `apps/backend/logs/app.log`
3. Check Hardhat console output
4. Open an issue on GitHub

## 🎉 Next Steps

After successfully running the demo:

1. **Explore the codebase** - Understand how it works
2. **Modify agents** - Create custom behaviors
3. **Add new scenarios** - Test different workflows
4. **Integrate your AI** - Connect real AI models
5. **Deploy to testnet** - Take it public

---

**Happy coding! 🚀🤖✨**
