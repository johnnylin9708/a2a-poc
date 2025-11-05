# 🚀 A2A Agent Ecosystem - 快速启动指南

> 5 分钟内启动完整的 Agent 生态系统

## 📋 前置需求

确保已安装：
- ✅ Node.js >= 18
- ✅ Python >= 3.11
- ✅ pnpm >= 8.0
- ✅ MongoDB
- ✅ MetaMask 浏览器扩展

## ⚡ 快速启动（推荐）

### 方法 1: 一键启动所有服务

```bash
# 1. 进入项目目录
cd /Users/johnnylin/Documents/a2a-poc

# 2. 确保 MongoDB 运行
brew services start mongodb-community

# 3. 启动所有服务（区块链 + 后端 + 前端）
pnpm dev
```

这会同时启动：
- ⛓️ **Hardhat 本地节点** - http://localhost:8545
- 🐍 **Backend API** - http://localhost:8000
- ⚛️ **Frontend** - http://localhost:5173

### 方法 2: 分别启动（推荐调试时使用）

```bash
# Terminal 1 - 启动区块链
cd /Users/johnnylin/Documents/a2a-poc
pnpm contracts:dev

# Terminal 2 - 启动后端
pnpm backend:dev

# Terminal 3 - 启动前端
pnpm frontend:dev
```

## 🔧 配置 MetaMask

### 1. 添加 Hardhat 本地网络

在 MetaMask 中添加自定义网络：
- **Network Name**: Hardhat Local
- **RPC URL**: http://127.0.0.1:8545
- **Chain ID**: 31337
- **Currency Symbol**: ETH

### 2. 导入测试账户

导入 Hardhat Account #0（有 10000 ETH）：
```
Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
Address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
```

## 🎯 使用流程

### 1. 访问应用
打开浏览器访问 http://localhost:5173

### 2. 连接钱包
点击右上角 "Connect Wallet" 按钮

### 3. 注册 Agent
1. 点击 "Register Agent"
2. 填写信息：
   - Name: "My First Agent"
   - Description: "A test agent for coding tasks"
   - Endpoint: "https://my-agent.example.com/a2a"
   - Capabilities: 添加 "coding", "testing"
3. 提交并在 MetaMask 中确认交易
4. 等待交易确认（几秒钟）
5. 查看 Agent 详情

### 4. 浏览 Agents
- 返回 Dashboard
- 使用搜索功能查找特定能力
- 点击 Agent 卡片查看详情

### 5. 提交评价
1. 访问 "Reputation" 页面
2. 切换到 "Submit Feedback"
3. 输入 Agent ID
4. 选择评分（1-5 星）
5. 填写评论
6. Payment Proof 可以输入任意 bytes32（测试用）
   - 例如：`0x0000000000000000000000000000000000000000000000000000000000000001`
7. 提交并确认交易

### 6. 查看排行榜
- 访问 "Reputation" 页面
- 查看 "Leaderboard" 标签
- 观察 Agent 排名和等级

## 📚 API 文档

后端 API 文档（启动后端后访问）：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐛 常见问题

### 问题 1: 前端无法连接后端

**症状**: 前端显示 `ECONNREFUSED ::1:8000`

**解决方案**: 
```bash
# 检查 vite.config.ts 中的 proxy 配置
# 应该使用 127.0.0.1 而不是 localhost
```

### 问题 2: MongoDB 连接失败

**症状**: `Database not initialized`

**解决方案**:
```bash
# Mac
brew services start mongodb-community

# 或使用 Docker
docker run -d -p 27017:27017 --name a2a-mongodb mongo
```

### 问题 3: 合约部署失败

**症状**: `HH108: Cannot connect to the network`

**解决方案**:
```bash
# 确保 Hardhat 节点正在运行
cd apps/contracts
pnpm dev

# 在新终端部署
pnpm deploy:local
```

### 问题 4: MetaMask 交易失败

**症状**: `Nonce too high` 或类似错误

**解决方案**:
1. 在 MetaMask 中点击设置
2. 高级 → 重置账户
3. 重新尝试交易

### 问题 5: Python 依赖问题

**症状**: `ModuleNotFoundError`

**解决方案**:
```bash
cd apps/backend
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 验证启动成功

### 后端健康检查
```bash
curl http://localhost:8000/health
# 应返回: {"status":"healthy"}
```

### 区块链连接检查
```bash
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
# 应返回: {"jsonrpc":"2.0","id":1,"result":"0x7a69"}
```

### 前端访问
打开 http://localhost:5173，应该看到：
- ✅ 导航栏
- ✅ "Connect Wallet" 按钮
- ✅ Agent Dashboard

## 🎯 下一步

成功启动后，你可以：
1. 📖 阅读 [PROJECT_ROADMAP.md](./PROJECT_ROADMAP.md) 了解项目规划
2. 🎉 查看 [PHASE1_COMPLETION.md](./PHASE1_COMPLETION.md) 了解已完成功能
3. 🚀 开始 Phase 2 开发
4. 🧪 运行端到端测试
5. 🌐 部署到测试网（Sepolia）

## 💡 提示

- 使用 `pnpm dev` 可以一次启动所有服务
- 使用分别启动可以更好地查看每个服务的日志
- MetaMask 的 Hardhat 账户有充足的测试 ETH
- 所有交易在本地网络上都是即时确认的

## 📞 获取帮助

如果遇到问题：
1. 检查所有服务是否都在运行
2. 查看浏览器控制台和终端日志
3. 参考 [README.md](./README.md) 和各模块的文档
4. 查看 [PHASE1_COMPLETION.md](./PHASE1_COMPLETION.md) 的测试建议

---

**准备好探索 Agent 生态系统了！** 🎊

