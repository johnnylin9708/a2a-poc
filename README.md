# A2A Agent Ecosystem Infrastructure

> 基於 ERC-8004 + A2A Protocol + x402 的去中心化 AI Agent 生態系統基礎設施

## 🌟 專案架構

這是一個使用 **Monorepo** 架構的全端專案，整合了區塊鏈、後端服務和前端介面。

```
┌──────────────────────────────────────────────────┐
│             前端層 (Frontend)                     │
│  - Agent Dashboard                               │
│  - Group Management UI                           │
│  - Reputation Viewer                             │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│        應用層 (Application Layer)                │
│                                                   │
│  A2A Protocol Handler                            │
│  ├─ Agent Discovery                              │
│  ├─ Task Delegation                              │
│  ├─ Message Routing                              │
│  └─ Workflow Orchestration                       │
│                                                   │
│  Agent Management Service                        │
│  ├─ Agent Registration                           │
│  ├─ Capability Matching                          │
│  ├─ Group Formation                              │
│  └─ Task Queue                                   │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│        區塊鏈層 (Blockchain Layer)               │
│                                                   │
│  ERC-8004 Smart Contracts                        │
│  ├─ Identity Registry (ERC-721)                  │
│  ├─ Reputation Registry                          │
│  └─ Validation Registry                          │
│                                                   │
│  Payment Layer (x402)                            │
│  └─ Agent-to-Agent Micropayments                 │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│         存儲層 (Storage Layer)                   │
│  - IPFS (Agent Cards, Metadata)                  │
│  - MongoDB (Off-chain Data)                      │
│  - Vector DB (Knowledge Base)                    │
└──────────────────────────────────────────────────┘
```

## 📦 專案結構

```
a2a-poc/
├── apps/
│   ├── contracts/          # Hardhat 智能合約專案 (ERC-8004)
│   ├── backend/            # Python FastAPI 後端
│   └── frontend/           # React + Vite 前端
├── packages/
│   ├── types/              # 共享的 TypeScript 類型定義
│   └── config/             # 共享的配置
├── package.json            # Root package.json
├── pnpm-workspace.yaml     # PNPM workspace 配置
└── turbo.json              # Turborepo 配置
```

## 🚀 技術棧

### 前端
- **React 18** + **Vite**
- **wagmi** + **ethers.js** - Web3 整合
- **shadcn/ui** - UI 組件庫
- **TailwindCSS** - 樣式

### 後端
- **Python 3.11+**
- **FastAPI** - API 框架
- **Web3.py** - 與區塊鏈交互
- **Motor** - 異步 MongoDB 驅動
- **A2A SDK** - Agent-to-Agent 協議

### 區塊鏈
- **Solidity ^0.8.20**
- **Hardhat** - 開發框架
- **OpenZeppelin Contracts** - 安全的合約庫
- **ERC-8004** 標準實作

### 存儲
- **MongoDB** - Off-chain 數據存儲
- **IPFS** - 去中心化文件存儲
- **Pinata** - IPFS Pinning 服務

## 🛠️ 開發環境設置

### 前置要求

- Node.js >= 18.0.0
- Python >= 3.11
- pnpm >= 8.0.0
- MongoDB (本地或 MongoDB Atlas)

### 安裝依賴

```bash
# 安裝 pnpm (如果尚未安裝)
npm install -g pnpm

# 安裝所有依賴
pnpm install

# 安裝 Python 依賴
cd apps/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 環境變量配置

複製環境變量模板：

```bash
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend/.env.example apps/frontend/.env
cp apps/contracts/.env.example apps/contracts/.env
```

編輯 `.env` 文件並填入必要的配置。

## 🏃 運行專案

### 開發模式 - 一鍵啟動（推薦）

```bash
# 同時啟動所有服務（區塊鏈 + 後端 + 前端）
pnpm dev
```

這會並行啟動：
- ⛓️ **Hardhat 本地節點** - http://localhost:8545
- 🐍 **Backend API** - http://localhost:8000
- ⚛️ **Frontend** - http://localhost:5173

### 開發模式 - 分別啟動（推薦調試時使用）

如果需要查看每個服務的獨立日誌，可以在**三個終端**分別啟動：

```bash
# Terminal 1 - 啟動區塊鏈節點
pnpm contracts:dev

# Terminal 2 - 啟動後端 API
pnpm backend:dev

# Terminal 3 - 啟動前端
pnpm frontend:dev
```

### 部署智能合約

```bash
# 編譯合約
cd apps/contracts
pnpm compile

# 部署到本地網絡
pnpm deploy:local

# 部署到 Sepolia 測試網
pnpm deploy:sepolia
```

## 🧪 測試

```bash
# 運行所有測試
pnpm test

# 智能合約測試
cd apps/contracts
pnpm test

# 後端測試
cd apps/backend
pytest

# 前端測試
cd apps/frontend
pnpm test
```

## 📚 文檔

- [智能合約文檔](./apps/contracts/README.md)
- [後端 API 文檔](./apps/backend/README.md) - 啟動後訪問 http://localhost:8000/docs
- [前端組件文檔](./apps/frontend/README.md)

## 🤝 核心概念

### Agent Identity (ERC-721 NFT)
每個 AI Agent 都有一個唯一的 ERC-721 NFT 作為身份標識，包含 Agent Card 信息。

### Reputation System
基於真實交易的去中心化評價系統，與 x402 支付證明綁定。

### Agent Groups
多個 Agents 可以組成群組協作完成複雜任務。

### A2A Protocol
標準化的 Agent 間通信協議，支持任務委派、消息路由等。

## 📄 授權

MIT License

## 🔗 相關資源

- [A2A Protocol](https://github.com/a2aproject/a2a-samples)
- [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004)
- [x402 Payment Protocol](https://github.com/x402project)

---

Built with ❤️ for the decentralized AI agent ecosystem
