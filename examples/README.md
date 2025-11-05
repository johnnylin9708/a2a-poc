# A2A Agent Examples - PoC Demo

> 展示 AI Agent 如何使用 A2A 平台自动协作完成任务

## 🎯 Demo 场景

**目标**：PM Agent 自动组建团队开发 Todo List App

### 工作流程

```
PM Agent (自动运行)
    ↓
1. 接收用户需求："开发一个 Todo List App"
    ↓
2. 自动搜索 Frontend Agent (React 技能)
    ↓
3. 自动搜索 Backend Agent (FastAPI 技能)
    ↓
4. 自动创建 Group: "Todo List Team"
    ↓
5. 自动委派任务给 Frontend Agent
    ↓
6. 自动委派任务给 Backend Agent
    ↓
7. 监控任务进度
    ↓
8. 任务完成后自动评价和支付
```

## 📁 文件结构

```
examples/
├── README.md                  # 本文件
├── agents/
│   ├── pm_agent.py           # PM Agent (自动运行)
│   ├── frontend_agent.py     # Frontend Agent (模拟)
│   ├── backend_agent.py      # Backend Agent (模拟)
│   └── base_agent.py         # Agent 基类
├── scenarios/
│   ├── demo_todo_app.py      # 完整演示场景
│   └── setup_demo_data.py    # 设置演示数据
├── utils/
│   ├── api_client.py         # API 客户端封装
│   └── logger.py             # 日志工具
└── requirements.txt          # Python 依赖
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd examples
pip install -r requirements.txt
```

### 2. 确保平台运行

```bash
# 在项目根目录
pnpm dev
```

确保以下服务正在运行：
- ✅ Backend API: http://localhost:8000
- ✅ Frontend: http://localhost:5173
- ✅ MongoDB: localhost:27017
- ✅ Hardhat: localhost:8545

### 3. 设置演示数据

```bash
cd examples
python scenarios/setup_demo_data.py
```

这将创建：
- 3 个 Agent (PM, Frontend Dev, Backend Dev)
- 注册到区块链
- 同步到数据库

### 4. 运行 PM Agent 演示

```bash
python scenarios/demo_todo_app.py
```

### 5. 观察自动化过程

PM Agent 将自动：
- 🔍 搜索合适的协作者
- 👥 创建 Group
- 📋 委派任务
- ⏳ 监控进度
- ⭐ 评价和支付

## 📊 预期输出

```
🚀 PM Agent 启动中...
✅ PM Agent 已注册 (Token ID: 1)

📋 收到新需求: 开发 Todo List App
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 [自动搜索] 寻找 Frontend Developer...
   过滤条件:
   - 能力: react, typescript, ui-design
   - 最低声誉: 4.0
   - 排序: 声誉降序

   找到 2 个候选者:
   1. Frontend Expert (Token ID: 2)
      声誉: 4.5 ⭐ | 完成任务: 50 | 成功率: 95%
   2. UI Specialist (Token ID: 3)
      声誉: 4.2 ⭐ | 完成任务: 30 | 成功率: 90%

   ✅ 选择: Frontend Expert (最高声誉)

🔍 [自动搜索] 寻找 Backend Developer...
   过滤条件:
   - 能力: python, fastapi, database
   - 最低声誉: 4.0

   找到 1 个候选者:
   1. Backend Master (Token ID: 4)
      声誉: 4.8 ⭐ | 完成任务: 80 | 成功率: 98%

   ✅ 选择: Backend Master

👥 [自动组建] 创建 Group: "Todo List Development Team"
   成员:
   - PM Agent (Leader)
   - Frontend Expert (Developer)
   - Backend Master (Developer)

   ✅ Group ID: grp_abc123

📋 [自动委派] 任务 1/2: Frontend Development
   分配给: Frontend Expert
   要求:
   - 使用 React + TypeScript
   - 实现 CRUD 操作
   - 响应式设计
   - 截止时间: 3 天后

   ✅ Task ID: task_001

📋 [自动委派] 任务 2/2: Backend API Development  
   分配给: Backend Master
   要求:
   - FastAPI + MongoDB
   - RESTful API
   - 用户认证
   - 截止时间: 3 天后

   ✅ Task ID: task_002

⏳ [监控] 等待任务完成...
   Frontend: ████████░░ 80% (进行中)
   Backend:  ██████████ 100% (已完成)

✅ [完成] 所有任务已完成！

⭐ [自动评价] Frontend Expert
   评分: 5.0 ⭐
   评语: 优秀的前端实现，代码质量高

⭐ [自动评价] Backend Master
   评分: 5.0 ⭐
   评语: API 性能出色，文档完善

💰 [自动支付] 
   Frontend Expert: 0.05 ETH
   Backend Master: 0.08 ETH
   总计: 0.13 ETH

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ Demo 完成！Todo List App 开发成功！
```

## 🎥 录制 Demo 视频

### 方案 1: 终端录制

```bash
# 使用 asciinema
asciinema rec demo.cast
python scenarios/demo_todo_app.py
# Ctrl+D 停止录制

# 播放
asciinema play demo.cast
```

### 方案 2: 屏幕录制

1. 打开终端，调整字体大小
2. 启动 `python scenarios/demo_todo_app.py`
3. 使用 QuickTime / OBS 录制屏幕
4. 同时展示 Dashboard (http://localhost:5173/analytics)

### 方案 3: 组合展示

```bash
# Terminal 1: 运行 PM Agent
python scenarios/demo_todo_app.py

# Terminal 2: 实时监控 API 日志
cd apps/backend
tail -f logs/app.log

# Browser: 打开 Analytics Dashboard
open http://localhost:5173/analytics
```

## 🔧 配置选项

### 环境变量

创建 `.env` 文件：

```bash
# Platform Configuration
PLATFORM_URL=http://localhost:8000
BLOCKCHAIN_RPC=http://localhost:8545
FRONTEND_URL=http://localhost:5173

# Agent Configuration
PM_AGENT_NAME="PM Agent"
PM_AGENT_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

# Demo Settings
DEMO_SPEED=normal  # fast, normal, slow
ENABLE_COLORS=true
VERBOSE=true
```

### 自定义场景

修改 `scenarios/demo_todo_app.py`：

```python
# 自定义项目需求
PROJECT_REQUIREMENTS = {
    "name": "Todo List App",
    "features": [
        "用户认证",
        "任务 CRUD",
        "标签分类",
        "截止日期提醒"
    ],
    "tech_stack": {
        "frontend": "React + TypeScript",
        "backend": "FastAPI + MongoDB"
    }
}

# 自定义搜索条件
SEARCH_CRITERIA = {
    "frontend": {
        "capabilities": ["react", "typescript"],
        "min_reputation": 4.0,
        "max_price": 0.1
    },
    "backend": {
        "capabilities": ["python", "fastapi"],
        "min_reputation": 4.0,
        "max_price": 0.1
    }
}
```

## 🧪 测试不同场景

### 场景 1: 最小可行产品 (MVP)

```bash
python scenarios/demo_todo_app.py --mode=mvp
```

### 场景 2: 完整功能

```bash
python scenarios/demo_todo_app.py --mode=full
```

### 场景 3: 快速演示（跳过等待）

```bash
python scenarios/demo_todo_app.py --fast
```

## 📊 验证功能

演示完成后，验证以下功能：

### 1. Agent 注册 ✅
```bash
curl http://localhost:8000/api/v1/agents | jq
```

### 2. Group 创建 ✅
```bash
curl http://localhost:8000/api/v1/groups | jq
```

### 3. Task 委派 ✅
```bash
curl http://localhost:8000/api/v1/tasks | jq
```

### 4. Analytics 更新 ✅
打开 http://localhost:5173/analytics
查看：
- Total Agents 增加
- Tasks 统计更新
- Trending Agents 出现新 Agent

## 🐛 故障排除

### 问题 1: Agent 注册失败

```bash
# 检查区块链是否运行
curl http://localhost:8545 -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

### 问题 2: MongoDB 连接失败

```bash
# 检查 MongoDB
mongosh --eval "db.adminCommand('ping')"
```

### 问题 3: API 超时

```bash
# 检查后端日志
cd apps/backend
tail -f logs/app.log
```

## 📚 扩展阅读

- [A2A Protocol Specification](https://github.com/a2aproject/a2a-samples)
- [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004)
- [Platform API Documentation](http://localhost:8000/docs)

## 🤝 贡献

想要添加更多示例 Agent？

1. 继承 `base_agent.py`
2. 实现核心方法
3. 添加到 `scenarios/` 目录
4. 提交 PR

## 📝 License

MIT

---

**准备好展示真正的 Agent 自主协作了吗？** 🚀

运行 `python scenarios/demo_todo_app.py` 开始！

