# @a2a/frontend

React frontend for the A2A Agent Ecosystem

## 技術棧

- **React 18** + **TypeScript**
- **Vite** - 快速的開發構建工具
- **TailwindCSS** + **shadcn/ui** - 現代化 UI 組件
- **wagmi** + **RainbowKit** - Web3 錢包連接和交互
- **React Router** - 路由管理
- **TanStack Query** - 數據獲取和緩存
- **Zustand** - 狀態管理

## 功能頁面

### 1. Agent Dashboard
- 查看所有 Agents
- 搜索和篩選
- Agent 詳情展示

### 2. Agent Registration
- 註冊新 Agent
- 上傳 metadata 到 IPFS
- 鑄造 ERC-721 NFT

### 3. Group Management
- 創建 Agent 群組
- 管理成員
- 委派任務

### 4. Reputation Viewer
- 查看 Agent 聲譽
- 提交反饋評價
- 聲譽歷史

## 開發

### 安裝依賴

```bash
pnpm install
```

### 配置環境變量

```bash
cp .env.example .env
# 編輯 .env 文件
```

### 運行開發服務器

```bash
pnpm dev
```

訪問 http://localhost:5173

### 構建生產版本

```bash
pnpm build
```

### 預覽生產構建

```bash
pnpm preview
```

## 專案結構

```
src/
├── components/          # 可重用組件
│   ├── ui/             # shadcn UI 組件
│   ├── agent/          # Agent 相關組件
│   ├── group/          # Group 相關組件
│   └── layout/         # 佈局組件
├── pages/              # 頁面組件
│   ├── Dashboard.tsx
│   ├── AgentDetails.tsx
│   ├── GroupManagement.tsx
│   └── Reputation.tsx
├── hooks/              # 自定義 hooks
│   ├── useAgents.ts
│   ├── useBlockchain.ts
│   └── useGroups.ts
├── lib/                # 工具函數
│   ├── api.ts          # API 客戶端
│   ├── contracts.ts    # 合約交互
│   └── utils.ts        # 通用工具
├── store/              # Zustand stores
│   └── agentStore.ts
├── types/              # TypeScript 類型定義
│   └── index.ts
├── App.tsx             # 主應用組件
└── main.tsx            # 應用入口
```

## Web3 整合

### 連接錢包

使用 RainbowKit 連接 MetaMask, WalletConnect 等錢包。

### 智能合約交互

通過 wagmi 和 viem 與 ERC-8004 合約交互。

## API 集成

後端 API 通過 Vite proxy 代理，開發環境下自動轉發到 `http://localhost:8000`。

