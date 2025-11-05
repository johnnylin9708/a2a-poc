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
├── requirements.txt
└── README.md
```

## 開發

### 安裝依賴

```bash
# 創建虛擬環境
python -m venv venv

# 激活虛擬環境
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 配置環境變量

```bash
cp .env.example .env
# 編輯 .env 文件
```

### 運行服務

```bash
# 開發模式（自動重載）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Python 直接運行
python -m app.main
```

### API 文檔

啟動服務後訪問：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 測試

```bash
# 運行所有測試
pytest

# 運行特定測試
pytest tests/test_agents.py

# 生成覆蓋率報告
pytest --cov=app tests/
```

## API 端點

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

## 部署

### Docker

```bash
docker build -t a2a-backend .
docker run -p 8000:8000 a2a-backend
```

### Production

```bash
# 使用 Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
