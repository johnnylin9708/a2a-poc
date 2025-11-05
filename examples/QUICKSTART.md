# 🚀 快速开始指南

> 5 分钟内运行完整的 AI Agent 协作演示

## 📋 前提条件

确保以下服务正在运行：

```bash
# 1. 在项目根目录启动所有服务
cd /Users/johnnylin/Documents/a2a-poc
pnpm dev
```

这将启动：
- ✅ Hardhat 区块链节点 (localhost:8545)
- ✅ Backend API (localhost:8000)
- ✅ Frontend (localhost:5173)
- ✅ MongoDB (localhost:27017)

## 🎯 方式 1: 使用快速启动脚本（推荐）

```bash
cd examples

# 添加执行权限（首次运行）
chmod +x run_demo.sh

# 运行脚本
./run_demo.sh
```

然后选择：
1. **首次运行**: 选择 `1` - 设置演示数据
2. **运行演示**: 选择 `2` - 运行完整演示
3. **快速演示**: 选择 `3` - 跳过等待动画

## 🎯 方式 2: 手动步骤

### Step 1: 安装依赖

```bash
cd examples

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### Step 2: 设置演示数据

```bash
# 创建演示 Agents
python scenarios/setup_demo_data.py
```

这将创建 3 个 Agent：
- PM Agent (项目管理)
- Frontend Expert (前端开发)
- Backend Master (后端开发)

### Step 3: 运行演示

```bash
# 完整演示（有等待动画）
python scenarios/demo_todo_app.py

# 或快速模式
python scenarios/demo_todo_app.py --fast

# 或只查看状态
python scenarios/demo_todo_app.py --status
```

## 🎬 预期效果

演示将展示以下流程：

```
🚀 PM Agent 启动
    ↓
📋 接收需求: 开发 Todo List App
    ↓
🔍 自动搜索 Frontend Developer
    找到: Frontend Expert (声誉 4.5⭐)
    ↓
🔍 自动搜索 Backend Developer
    找到: Backend Master (声誉 4.8⭐)
    ↓
👥 创建 Group: "Todo List Development Team"
    成员: PM Agent + Frontend Expert + Backend Master
    ↓
📋 委派任务 1/2: Frontend Development
    分配给: Frontend Expert
    ↓
📋 委派任务 2/2: Backend API Development
    分配给: Backend Master
    ↓
⏳ 监控任务进度...
    ↓
✅ 任务完成
    ↓
⭐ 自动评价团队成员
    Frontend Expert: 5.0⭐
    Backend Master: 5.0⭐
    ↓
🎉 项目完成！
```

## 📊 查看结果

### 1. 在 Frontend 查看

打开浏览器访问：

- **Analytics Dashboard**: http://localhost:5173/analytics
  - 查看 Agents 统计
  - 查看 Tasks 完成情况
  - 查看 Trending Agents

- **Groups 页面**: http://localhost:5173/groups
  - 查看新创建的 Group
  - 查看成员列表

### 2. 在 Backend 查看

```bash
# 查看 API 文档
open http://localhost:8000/docs

# 查看 Agents
curl http://localhost:8000/api/v1/agents | jq

# 查看 Groups
curl http://localhost:8000/api/v1/groups | jq

# 查看 Tasks
curl http://localhost:8000/api/v1/tasks | jq
```

### 3. 在 MongoDB 查看

```bash
# 连接数据库
mongosh a2a_ecosystem

# 查看 Agents
db.agents.find().pretty()

# 查看 Groups
db.groups.find().pretty()

# 查看 Tasks
db.tasks.find().pretty()

# 查看 Feedbacks
db.feedbacks.find().pretty()
```

## 🎥 录制演示

参考 [RECORDING_GUIDE.md](./RECORDING_GUIDE.md) 了解如何录制演示视频。

最简单的方式：

```bash
# 安装 asciinema
brew install asciinema

# 开始录制
asciinema rec demo.cast

# 运行演示
python scenarios/demo_todo_app.py

# Ctrl+D 停止录制

# 播放查看
asciinema play demo.cast
```

## 🔧 故障排除

### 问题 1: ModuleNotFoundError

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt
```

### 问题 2: 平台未运行

```bash
# 检查后端
curl http://localhost:8000/health

# 如果失败，启动平台
cd ..
pnpm dev
```

### 问题 3: 没有可用的 Agents

```bash
# 重新运行设置脚本
python scenarios/setup_demo_data.py
```

### 问题 4: MongoDB 连接失败

```bash
# 检查 MongoDB
pgrep -x mongod

# 如果未运行，启动 MongoDB
brew services start mongodb-community  # macOS
# 或
sudo systemctl start mongod            # Linux
```

### 问题 5: 区块链连接失败

```bash
# 检查 Hardhat
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# 如果失败，在另一个终端启动
cd apps/contracts
pnpm hardhat node
```

## 🧪 测试不同场景

### 场景 1: 最小化演示

```bash
python scenarios/demo_todo_app.py --fast
```

### 场景 2: 查看系统状态

```bash
python scenarios/demo_todo_app.py --status
```

### 场景 3: 自定义项目需求

编辑 `scenarios/demo_todo_app.py`，修改 `TODO_APP_REQUIREMENTS`：

```python
TODO_APP_REQUIREMENTS = {
    "name": "Your Custom App",
    "description": "...",
    "required_capabilities": {
        "frontend": ["react", "vue"],
        "backend": ["nodejs", "express"]
    }
}
```

## 📚 下一步

### 1. 探索代码

```bash
examples/
├── agents/
│   ├── base_agent.py    # Agent 基类，可扩展
│   └── pm_agent.py      # PM Agent 实现
├── utils/
│   ├── api_client.py    # API 客户端封装
│   └── logger.py        # 日志工具
└── scenarios/
    ├── setup_demo_data.py
    └── demo_todo_app.py
```

### 2. 创建自己的 Agent

```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(
            name="My Agent",
            description="...",
            capabilities=["skill1", "skill2"],
            **kwargs
        )
    
    async def custom_behavior(self):
        # 实现自定义行为
        pass
```

### 3. 集成到实际项目

参考 `agents/pm_agent.py` 了解如何：
- 使用 API 客户端
- 搜索和发现 Agents
- 创建 Groups
- 委派任务
- 提交反馈

### 4. 开发 SDK

基于 `utils/api_client.py` 和 `agents/base_agent.py`，
可以进一步封装成完整的 SDK：

```python
from a2a_sdk import Agent, Platform

# 连接平台
platform = Platform("http://localhost:8000")

# 创建 Agent
agent = Agent.create(
    name="My Agent",
    capabilities=["python", "fastapi"],
    platform=platform
)

# 自动协作
collaborators = await agent.discover(capabilities=["frontend"])
group = await agent.create_group(members=[agent, collaborators[0]])
await group.delegate_task(to=collaborators[0], task_data={...})
```

## 💡 提示

1. **首次运行**: 先运行 `setup_demo_data.py` 创建演示数据
2. **快速演示**: 使用 `--fast` 跳过等待动画
3. **调试模式**: 查看 `apps/backend/logs/` 中的日志
4. **清理数据**: `mongosh a2a_ecosystem --eval "db.dropDatabase()"`
5. **录制视频**: 使用 `asciinema` 录制终端输出

## 🎯 成功标志

✅ PM Agent 成功启动  
✅ 自动搜索到 2 个开发者  
✅ 成功创建 Group  
✅ 成功委派 2 个任务  
✅ 任务状态更新正常  
✅ 自动评价完成  
✅ Dashboard 显示新数据  

---

**准备好了吗？开始你的第一个 Demo！** 🚀

```bash
cd examples
./run_demo.sh
```

有问题？查看 [README.md](./README.md) 获取详细信息。

