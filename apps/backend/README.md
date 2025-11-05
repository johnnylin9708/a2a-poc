# @a2a/backend

FastAPI backend for the A2A Agent Ecosystem

## 功能特性

- **Agent Management API** - Agent 註冊、查詢、更新
- **A2A Protocol Handler** - Agent 間通信協議處理
- **Blockchain Integration** - 與 ERC-8004 智能合約交互
- **MongoDB Storage** - Off-chain 數據存儲
- **IPFS Integration** - 去中心化文件存儲
- **RESTful API** - 完整的 REST API 接口

## 專案結構

```
backend/
├── app/
│   ├── main.py              # FastAPI 應用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # MongoDB 連接
│   ├── api/
│   │   ├── v1/
│   │   │   ├── agents.py    # Agent 相關 API
│   │   │   ├── groups.py    # Group 管理 API
│   │   │   ├── reputation.py # 聲譽系統 API
│   │   │   └── validation.py # 驗證 API
│   ├── services/
│   │   ├── blockchain.py    # 區塊鏈服務
│   │   ├── a2a_handler.py   # A2A 協議處理
│   │   ├── ipfs_service.py  # IPFS 服務
│   │   └── agent_manager.py # Agent 管理服務
│   ├── models/
│   │   ├── agent.py         # Agent 數據模型
│   │   ├── group.py         # Group 數據模型
│   │   └── task.py          # Task 數據模型
│   └── schemas/
│       ├── agent.py         # Agent Pydantic schemas
│       ├── group.py         # Group Pydantic schemas
│       └── task.py          # Task Pydantic schemas
├── tests/
│   ├── test_agents.py
│   ├── test_blockchain.py
│   └── test_a2a.py
├── venv/                    # Python 虛擬環境
├── requirements.txt
└── README.md
```

## 🚀 快速開始

### 方法 1：從項目根目錄啟動（推薦）

```bash
# 確保 MongoDB 正在運行
brew services start mongodb-community

# 從根目錄啟動所有服務
cd /Users/johnnylin/Documents/a2a-poc
pnpm dev

# 或只啟動後端
pnpm backend:dev
```

### 方法 2：直接運行後端

```bash
cd apps/backend

# 激活虛擬環境
source venv/bin/activate

# 運行
python -m app.main
```

## 📋 前置需求

### 1. Python 依賴

依賴已安裝在 `venv/` 虛擬環境中。如需重新安裝：

```bash
cd apps/backend

# 創建虛擬環境（如果不存在）
python3 -m venv venv

# 激活虛擬環境
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 2. MongoDB 設置

**選項 A: 本地 MongoDB（推薦用於開發）**

```bash
# Mac
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# 驗證
mongosh --eval "db.version()"
```

**選項 B: Docker MongoDB**

```bash
docker run -d -p 27017:27017 --name a2a-mongodb mongo

# 停止
docker stop a2a-mongodb

# 啟動
docker start a2a-mongodb
```

**選項 C: MongoDB Atlas（雲端）**

1. 註冊 [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)（免費）
2. 創建集群並獲取連接字串
3. 更新 `.env` 中的 `MONGODB_URL`

### 3. 環境變量配置

創建或編輯 `apps/backend/.env`：

```bash
# MongoDB 配置
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=a2a_agent_ecosystem

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# 區塊鏈配置（部署合約後填入）
IDENTITY_REGISTRY_ADDRESS=
REPUTATION_REGISTRY_ADDRESS=
VALIDATION_REGISTRY_ADDRESS=
WEB3_PROVIDER_URI=http://127.0.0.1:8545

# IPFS 配置
IPFS_HOST=127.0.0.1
IPFS_PORT=5001
```

## 🧪 測試運行

```bash
# 啟動後端
pnpm backend:dev

# 在另一個終端測試
curl http://localhost:8000/
curl http://localhost:8000/health

# 查看 API 文檔
open http://localhost:8000/docs
```

## 📊 成功啟動的標誌

你應該看到：

```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
✅ Connected to MongoDB: a2a_agent_ecosystem
✅ Database indexes created
✅ Agent Management Service initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 🌐 API 文檔

啟動服務後訪問：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API 端點

### Agents

- `POST /api/v1/agents/register` - 註冊新 Agent
- `GET /api/v1/agents` - 查詢 Agents
- `GET /api/v1/agents/{agent_id}` - 獲取 Agent 詳情
- `PUT /api/v1/agents/{agent_id}` - 更新 Agent
- `POST /api/v1/agents/discover` - 發現符合條件的 Agents

### Groups

- `POST /api/v1/groups` - 創建 Group
- `GET /api/v1/groups/{group_id}` - 獲取 Group 詳情
- `POST /api/v1/groups/{group_id}/add-agent` - 添加 Agent 到 Group
- `POST /api/v1/groups/{group_id}/tasks` - 委派任務到 Group

### Reputation

- `GET /api/v1/reputation/{agent_id}` - 獲取 Agent 聲譽
- `POST /api/v1/reputation/feedback` - 提交反饋

### Validation

- `GET /api/v1/validation/{agent_id}` - 獲取驗證記錄
- `POST /api/v1/validation/submit` - 提交驗證結果

## 🧪 測試

```bash
cd apps/backend

# 運行所有測試
pytest

# 運行特定測試
pytest tests/test_agents.py

# 生成覆蓋率報告
pytest --cov=app tests/

# 生成 HTML 覆蓋率報告
pytest --cov=app --cov-report=html tests/
```

## 🐛 常見問題排查

### 1. MongoDB 連接失敗

**症狀**: `RuntimeError: Database not initialized`

**解決方案**:
```bash
# 檢查 MongoDB 是否運行
brew services list | grep mongodb
ps aux | grep mongod

# 啟動 MongoDB
brew services start mongodb-community

# 或使用 Docker
docker run -d -p 27017:27017 --name a2a-mongodb mongo
```

### 2. Port 8000 被占用

**症狀**: `Address already in use`

**解決方案**:
```bash
# 查找占用進程
lsof -i :8000

# 關閉進程
kill -9 <PID>

# 或修改 .env 中的 API_PORT
echo "API_PORT=8001" >> .env
```

### 3. Python 依賴問題

**症狀**: `ModuleNotFoundError`

**解決方案**:
```bash
cd apps/backend

# 確認虛擬環境
source venv/bin/activate

# 重新安裝依賴
pip install -r requirements.txt

# 驗證安裝
pip list | grep fastapi
```

### 4. 區塊鏈連接問題

**症狀**: 無法連接到區塊鏈

**解決方案**:
```bash
# 確保 Hardhat 節點正在運行
cd apps/contracts
pnpm node

# 檢查 .env 中的 WEB3_PROVIDER_URI
echo $WEB3_PROVIDER_URI
```

## 🔧 開發工具

### 開發模式（自動重載）

```bash
cd apps/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 代碼格式化

```bash
# 使用 black
black app/

# 使用 isort（排序 imports）
isort app/

# 使用 flake8（檢查）
flake8 app/
```

### 類型檢查

```bash
# 使用 mypy
mypy app/
```

## 🚀 部署

### Docker 部署

```bash
# 構建鏡像
docker build -t a2a-backend .

# 運行容器
docker run -d \
  -p 8000:8000 \
  --name a2a-backend \
  -e MONGODB_URL=mongodb://host.docker.internal:27017 \
  a2a-backend
```

### Production 部署

```bash
# 使用 Gunicorn + Uvicorn workers
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

## 🎯 完整開發流程

1. **啟動 MongoDB**
   ```bash
   brew services start mongodb-community
   ```

2. **啟動區塊鏈節點**
   ```bash
   cd apps/contracts
   pnpm dev
   ```

3. **部署智能合約**
   ```bash
   cd apps/contracts
   pnpm deploy:local
   # 記下合約地址
   ```

4. **更新後端環境變量**
   ```bash
   cd apps/backend
   # 編輯 .env，填入合約地址
   ```

5. **啟動後端**
   ```bash
   cd apps/backend
   pnpm dev
   ```

6. **測試 API**
   - 訪問 http://localhost:8000/docs
   - 註冊第一個 Agent
   - 測試 Agent 發現功能

## 🔗 相關鏈接

- [FastAPI 文檔](https://fastapi.tiangolo.com/)
- [Motor (Async MongoDB)](https://motor.readthedocs.io/)
- [Web3.py](https://web3py.readthedocs.io/)
- [A2A Protocol](https://github.com/a2aproject/a2a-samples)
- [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004)

## 📝 License

MIT
