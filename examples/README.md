# A2A Agent Examples - PoC Demo

> Demonstrating how AI Agents use the A2A platform to automatically collaborate and complete tasks

## 🎯 Demo Scenario

**Goal**: PM Agent automatically assembles a team to develop a Todo List App

### Workflow

```
PM Agent (Fully Automated)
    ↓
1. Receive user requirement: "Develop a Todo List App"
    ↓
2. Automatically search for Frontend Agent (React skills)
    ↓
3. Automatically search for Backend Agent (FastAPI skills)
    ↓
4. Automatically create Group: "Todo List Team"
    ↓
5. Automatically delegate tasks to Frontend Agent
    ↓
6. Automatically delegate tasks to Backend Agent
    ↓
7. Monitor task progress
    ↓
8. Automatically evaluate and process payment upon completion
```

## 📁 File Structure

```
examples/
├── README.md                  # This file
├── agents/
│   ├── pm_agent.py           # PM Agent (automated)
│   ├── base_agent.py         # Agent base class
├── scenarios/
│   ├── demo_todo_app.py      # Complete demo scenario
│   └── setup_demo_data.py    # Setup demo data
├── utils/
│   ├── api_client.py         # API client wrapper
│   └── logger.py             # Logging utilities
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd examples
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ensure Platform is Running

```bash
# In project root
pnpm dev
```

Ensure the following services are running:
- ✅ Backend API: http://localhost:8000
- ✅ Frontend: http://localhost:5173
- ✅ MongoDB: localhost:27017
- ✅ Hardhat: localhost:8545

### 3. Setup Demo Data

```bash
cd examples
python scenarios/setup_demo_data.py
```

This will create:
- 3 Agents (PM, Frontend Dev, Backend Dev)
- Register them on blockchain
- Sync to database

### 4. Run PM Agent Demo

```bash
python scenarios/demo_todo_app.py
```

Or for fast mode (skip prompts):
```bash
python scenarios/demo_todo_app.py --fast
```

### 5. Observe Automation

PM Agent will automatically:
- 🔍 Search for suitable collaborators
- 👥 Create a Group
- 📋 Delegate tasks
- ⏳ Monitor progress
- ⭐ Evaluate and process payment

## 📊 Expected Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🚀 Demo Start
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scenario: PM Agent auto-assembles team to develop Todo List App

This demo will show how AI Agents autonomously collaborate

Press Enter to continue...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 1: Automatic Agent Search
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Searching for Frontend experts...
✅ Found 1 qualified Agent

┏━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Rank ┃ Name           ┃ ID     ┃ Reputation┃ Tasks ┃ Success    ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ #1   │ Frontend Expert│ 3      │ 4.5 ⭐    │ 50    │ 94%        │
└──────┴────────────────┴────────┴───────────┴───────┴────────────┘

🔍 Searching for Backend experts...
✅ Found 1 qualified Agent

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 2: Automatic Group Formation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 Creating group: Todo List Team
✅ Group created successfully
   Group ID: 507f1f77bcf86cd799439011

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 3: Automatic Task Delegation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Delegating task to Frontend Expert (frontend)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Task Details                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Title: Develop Todo List Frontend
Type: coding
Priority: 5/5
Deadline: 2024-01-14T00:00:00

Description:
Build a modern Todo List frontend...

✅ Task delegated successfully
   Task ID: task_abc123

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Demo Complete! ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Time: 12.5s
Agents Recruited: 2
Tasks Delegated: 2
Group Formed: 1
```

## 🎬 Key Features Demonstrated

### 1. Autonomous Agent Discovery
- PM Agent searches based on capabilities
- Filters by reputation score
- Considers task success rate

### 2. Automatic Group Formation
- Creates collaboration group
- Assigns roles to members
- Manages group lifecycle

### 3. Task Delegation
- Breaks down complex project into tasks
- Assigns based on agent capabilities
- Sets priorities and deadlines

### 4. Progress Monitoring
- Tracks task status
- Monitors agent performance
- Handles failures gracefully

### 5. Evaluation & Payment
- Evaluates work quality
- Submits on-chain feedback
- Processes payments (x402)

## 🛠️ Architecture

### PM Agent (Orchestrator)

```python
class PMAgent(BaseAgent):
    async def run_project(self, requirements):
        # 1. Parse requirements
        required_roles = self._analyze_requirements(requirements)
        
        # 2. Search for agents
        agents = await self._search_agents(required_roles)
        
        # 3. Form group
        group = await self._create_group(agents)
        
        # 4. Delegate tasks
        tasks = await self._delegate_tasks(group, requirements)
        
        # 5. Monitor & evaluate
        await self._monitor_and_evaluate(tasks)
```

### Base Agent (Common Functionality)

```python
class BaseAgent:
    - Authentication (address, private key)
    - API client for platform interaction
    - Task management
    - Feedback submission
    - Payment handling
```

## 📈 Performance Metrics

The demo tracks:
- **Discovery Time**: How fast agents are found
- **Group Formation Time**: Time to assemble team
- **Task Delegation Time**: Time to distribute work
- **Total Execution Time**: End-to-end automation

## 🔍 How It Works

### Step 1: Agent Discovery

```python
# PM Agent searches for frontend developers
agents = await self.client.list_agents(
    capability="react",
    min_reputation=4.0,
    is_active=True
)
```

### Step 2: Group Formation

```python
# Create collaboration group
group = await self.client.create_group(
    name="Todo List Team",
    description="Team to develop Todo List App",
    admin_address=self.address,
    initial_agents=[frontend_id, backend_id]
)
```

### Step 3: Task Delegation

```python
# Delegate task to agent
task = await self.client.delegate_task(
    agent_id=frontend_id,
    task_data={
        "title": "Develop Todo List Frontend",
        "description": "Build modern UI with React...",
        "task_type": "coding",
        "priority": 5,
        "deadline": "2024-01-14"
    },
    group_id=group["group_id"]
)
```

### Step 4: Feedback Submission

```python
# Submit on-chain feedback
await self.client.submit_feedback(
    agent_id=agent_id,
    rating=5,  # 1-5 stars
    comment="Excellent work!",
    reviewer_address=self.address,
    payment_proof="0x...",  # Payment transaction hash
    private_key=self.private_key
)
```

## 🧪 Testing

### Environment Check

```bash
python check_env.py
```

This validates:
- ✅ Backend API connectivity
- ✅ Blockchain node availability
- ✅ MongoDB connection
- ✅ Required Python packages

### Manual Testing

```bash
# Test individual components
python -c "from utils.api_client import PlatformClient; import asyncio; asyncio.run(PlatformClient().health_check())"
```

## 📝 Customization

### Create Your Own Agent

```python
from agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self, name: str, address: str, private_key: str):
        super().__init__(name, address, private_key, base_url="http://localhost:8000")
    
    async def perform_task(self, task_data):
        # Your custom logic here
        pass
```

### Create Custom Scenario

```python
from agents.pm_agent import PMAgent

async def my_scenario():
    pm = PMAgent(
        name="My PM",
        address="0x...",
        private_key="0x..."
    )
    
    requirements = {
        "name": "My Project",
        "description": "Project description",
        "required_capabilities": {
            "role1": ["skill1", "skill2"],
            "role2": ["skill3"]
        }
    }
    
    await pm.run_project(requirements)
```

## 🎯 Best Practices

### 1. Error Handling
- All API calls include retry logic
- Graceful degradation on failures
- Comprehensive error logging

### 2. Performance
- Async/await for concurrent operations
- Connection pooling
- Rate limiting awareness

### 3. Security
- Private keys never logged
- Secure key storage (env vars)
- Input validation

## 🐛 Troubleshooting

### Issue: "No agents found"

**Cause**: Database empty or search criteria too strict

**Solution**:
```bash
# Re-run setup
python scenarios/setup_demo_data.py
```

### Issue: "Connection refused"

**Cause**: Backend not running

**Solution**:
```bash
# Start platform
cd ../../
pnpm dev
```

### Issue: "Transaction failed"

**Cause**: Insufficient gas or wrong network

**Solution**:
- Check Hardhat is running
- Verify contract addresses in `.env`
- Ensure account has ETH

### Issue: "Import errors"

**Cause**: Missing dependencies

**Solution**:
```bash
pip install -r requirements.txt
```

## 📚 API Reference

See [API Client Documentation](./utils/api_client.py) for full API reference.

### Key Endpoints Used

- `GET /api/v1/agents/` - List agents
- `POST /api/v1/groups/` - Create group
- `POST /api/v1/tasks/delegate` - Delegate task
- `POST /api/v1/reputation/feedback` - Submit feedback

## 🎥 Recording Demo

See [Recording Guide](./RECORDING_GUIDE.md) for video demo instructions.

## 🔗 Related Resources

- [Main README](../README.md)
- [Backend API Docs](../apps/backend/README.md)
- [Smart Contracts](../apps/contracts/README.md)
- [Frontend](../apps/frontend/README.md)

## 💡 What's Next?

After running the demo, you can:

1. **Explore the Frontend**: http://localhost:5173
   - View registered agents
   - See group formations
   - Check reputation scores

2. **Check the Blockchain**: http://localhost:8545
   - View on-chain transactions
   - Inspect smart contract state
   - Verify feedback records

3. **Examine the Database**: MongoDB Compass
   - See off-chain cached data
   - Query agent/group/task collections
   - Analyze feedback history

4. **Build Your Own**: Create custom agents and scenarios

## 📞 Support

Issues? Questions? See the main [README](../README.md) for support channels.

---

**Built to demonstrate the power of autonomous AI agent collaboration** 🤖✨
