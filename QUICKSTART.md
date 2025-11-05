# ⚡ Quick Start Guide

快速啟動 A2A Agent Ecosystem 開發環境

## 🎯 目標

5 分鐘內啟動完整的開發環境，包括：
- ✅ 智能合約本地節點
- ✅ 後端 API 服務
- ✅ 前端應用

## 📦 前置要求

```bash
node --version    # >= 18.0.0
python --version  # >= 3.11
pnpm --version    # >= 8.0.0
mongod --version  # MongoDB running
```

## 🚀 5 分鐘設置

### 1️⃣ 安裝依賴 (2 分鐘)

```bash
# Root 依賴
pnpm install

# Python 依賴
cd apps/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ../..
```

### 2️⃣ 啟動服務 (1 分鐘)

開啟 3 個終端窗口：

**Terminal 1 - 區塊鏈節點:**
```bash
cd apps/contracts
pnpm node
```

**Terminal 2 - 部署合約 & 啟動後端:**
```bash
# 部署合約
cd apps/contracts
pnpm compile
pnpm deploy:local

# 記下合約地址，然後啟動後端
cd ../backend
source venv/bin/activate
python -m app.main
```

**Terminal 3 - 前端:**
```bash
cd apps/frontend
pnpm dev
```

### 3️⃣ 訪問應用 (30 秒)

- 🌐 **前端**: http://localhost:5173
- 📡 **API 文檔**: http://localhost:8000/docs
- ⛓️ **區塊鏈**: http://localhost:8545

## ✨ 第一次使用

### 註冊測試 Agent

使用 Hardhat 提供的測試賬戶：

```javascript
// 測試賬戶 #0
Address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
```

通過 API 註冊 Agent:

```bash
curl -X POST http://localhost:8000/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TestAgent",
    "description": "My first agent",
    "capabilities": ["coding", "testing"],
    "endpoint": "http://localhost:3000",
    "owner_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "private_key": "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
  }'
```

### 查看 Agents

訪問 http://localhost:5173 查看已註冊的 Agents

## 🎮 常用命令

```bash
# 查看所有可用命令
pnpm -r run

# 運行所有服務（使用 Turborepo）
pnpm dev

# 清理所有構建產物
pnpm clean

# 運行測試
pnpm test
```

## 🐛 常見問題

### MongoDB 連接失敗

```bash
# 啟動 MongoDB
mongod

# 或在 apps/backend/.env 中使用 MongoDB Atlas
MONGODB_URL=mongodb+srv://...
```

### 合約部署失敗

```bash
# 重啟 Hardhat 節點
cd apps/contracts
pnpm node

# 在新終端重新部署
pnpm deploy:local
```

### 端口被占用

```bash
# 查找並關閉進程
lsof -i :5173  # Frontend
lsof -i :8000  # Backend
lsof -i :8545  # Hardhat
```

## 📚 下一步

- 📖 閱讀完整 [README.md](./README.md)
- 🚀 查看 [DEPLOYMENT.md](./DEPLOYMENT.md)
- 📝 查看 [API 文檔](http://localhost:8000/docs)
- 🎓 閱讀 [A2A Protocol 文檔](https://github.com/a2aproject/a2a-samples)

## 💡 提示

- 使用 `pnpm dev` 在 root 目錄一次性啟動所有服務
- Hardhat 提供 20 個測試賬戶，每個有 10000 ETH
- MongoDB 數據存儲在本地，重啟不會丟失
- 智能合約更改需要重新編譯和部署

祝你開發愉快！🎉

