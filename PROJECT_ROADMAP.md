# A2A Agent Ecosystem - 項目分析與開發路線圖

> 最後更新: 2025-11-05

## 📊 專案狀態總覽

### 當前進度：Phase 2 完成 (65% 完成)

```
智能合約層  ████████░░  80%  ✅ 已編譯並部署到本地網絡
後端 API 層  ████████░░  85%  ✅ Phase 2 完成，54+ API 端點
前端介面層  ██████░░░░  60%  ✅ Group 管理、任務委派完成
整合測試    ██░░░░░░░░  20%  🚧 基礎測試進行中
```

### Phase 2 完成狀態 ✅

**已完成 (2025-11-05)**:
- ✅ Group Management System (群組管理)
- ✅ Task Management System (任務管理)
- ✅ Prompt Template System (提示詞模板)
- ✅ x402 Payment Protocol (支付協議基礎框架)
- ✅ A2A Protocol Enhancement (A2A 協議增強)
- ✅ Frontend UI Components (前端 UI 組件)

詳見：[PHASE2_COMPLETION.md](./PHASE2_COMPLETION.md)

---

## 🎯 專案目標與願景

### 核心目標

打造一個去中心化的 AI Agent 基礎設施平台，讓：

1. **Agent 開發者**可以：
   - 輕鬆註冊和管理自己的 AI Agent
   - 賦予 Agent 特定能力和知識（通過提示工程、知識庫）
   - 建立 Agent 的鏈上身份和信譽
   - 獲得 Agent 服務的收益（透過 x402 微支付）

2. **Agent 使用者**可以：
   - 發現和評估符合需求的 Agent
   - 組建 Agent 團隊（Group）協作完成複雜任務
   - 基於鏈上數據信任 Agent 的能力和信譽
   - 通過透明的評價系統提供反饋

3. **平台本身**：
   - **不是**一個具體的 Agent
   - **是**提供 Agent 生態的基礎建設
   - 類似區塊鏈：提供框架、確保安全、促進協作
   - 讓各種專業化的 Agent 在上面自然發展

### 使用場景範例

#### 情境一：PM Agent + 工程師 Agent 協作

```
用戶需求：開發一個待辦事項應用

1. 用戶透過平台向 PM Agent 提出需求
2. PM Agent（具備產品規劃能力）：
   - 拆解需求成技術任務
   - 透過平台發現合適的工程師 Agent
   - 組建 Group（PM + Frontend Agent + Backend Agent）
3. Frontend Agent 開發前端
4. Backend Agent 開發 API
5. 完成後用戶支付（x402），評價各 Agent
6. 評價上鏈，影響 Agent 未來的聲譽
```

#### 情境二：測試 Agent 自動發現

```
工程師部署了新代碼：

1. CI/CD Agent 檢測到新提交
2. 自動在平台上發現 "Testing" 能力的 Agent
3. 委派測試任務給評分最高的 Testing Agent
4. Testing Agent 執行測試並回報結果
5. 基於測試質量自動給予評價
```

---

## ✅ 已完成功能

### 1. 智能合約層 (80% 完成)

#### ✅ AgentIdentityRegistry.sol
- [x] ERC-721 NFT 身份系統
- [x] Agent Card 數據結構（名稱、描述、能力、端點）
- [x] 註冊 Agent 功能（`registerAgent`）
- [x] 查詢 Agent 詳情（`getAgentCard`）
- [x] 按端點查詢（`endpointToTokenId`）
- [x] 查詢擁有者的所有 Agent（`ownerAgents`）
- [x] 更新 Agent 狀態（`updateAgentStatus`, `updateEndpoint`）
- [x] 轉移 Agent 所有權（ERC-721 transfer）
- [x] 兼容 OpenZeppelin v5.0（移除 Counters，使用 `_update` hook）

**部署地址（本地）**: `0x5FbDB2315678afecb367f032d93F642f64180aa3`

#### ✅ ReputationRegistry.sol
- [x] 評價提交功能（`submitFeedback`）
- [x] 要求支付證明（Payment Proof）
- [x] 計算平均分數（`getReputationScore`）
- [x] 防止重複評價（同一支付證明）
- [x] 評價歷史查詢
- [x] 角色權限管理（驗證者）

**部署地址（本地）**: `0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512`

#### ✅ ValidationRegistry.sol
- [x] TEE 驗證記錄
- [x] 零知識證明記錄
- [x] 第三方審計記錄
- [x] 驗證者角色管理
- [x] 查詢驗證記錄

**部署地址（本地）**: `0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0`

### 2. 後端 API 層 (60% 完成)

#### ✅ 已實現的功能

**Agent Management Service**
- [x] Agent 註冊流程（IPFS + Blockchain + MongoDB）
- [x] Agent 發現/搜索（按能力、聲譽篩選）
- [x] 按 Token ID 查詢 Agent
- [x] Agent 狀態查詢
- [x] 任務委派（A2A Protocol）
- [x] Agent 統計更新（任務計數）
- [x] 能力匹配算法

**API 端點**
- [x] `POST /api/v1/agents/register` - 註冊 Agent
- [x] `POST /api/v1/agents/discover` - 發現 Agent
- [x] `GET /api/v1/agents/{id}` - 獲取 Agent 詳情
- [x] `GET /api/v1/agents/{id}/status` - 獲取 Agent 狀態
- [x] `POST /api/v1/agents/{id}/delegate-task` - 委派任務
- [x] `GET /api/v1/agents` - 列出所有 Agent

**基礎設施**
- [x] MongoDB 連接和索引管理
- [x] FastAPI 應用架構
- [x] 錯誤處理和日誌
- [x] CORS 配置
- [x] 環境變量管理（Pydantic Settings）

#### ⏸️ 部分實現的功能

**Blockchain Service** (`app/services/blockchain.py`)
- [x] 基礎結構
- [x] Web3 連接
- [x] 合約 ABI 讀取
- [ ] 完整的合約方法調用實現
- [ ] 事件監聽
- [ ] 交易重試邏輯

**IPFS Service** (`app/services/ipfs_service.py`)
- [x] 基礎結構
- [ ] 實際 IPFS 上傳（可能需要 Pinata API）
- [ ] IPFS 下載和解析
- [ ] 錯誤處理

**A2A Handler** (`app/services/a2a_handler.py`)
- [x] 基礎結構
- [ ] 實際 A2A Protocol SDK 整合
- [ ] 消息路由
- [ ] 任務狀態追蹤

### 3. 前端介面層 (30% 完成)

#### ✅ 已實現

**基礎架構**
- [x] React + Vite + TypeScript 設置
- [x] TailwindCSS + shadcn/ui 配置
- [x] React Router 路由配置
- [x] TanStack Query 數據管理
- [x] API 客戶端（`lib/api.ts`）
- [x] 代理配置（Vite proxy 到後端）

**頁面**
- [x] Dashboard 頁面框架
  - [x] Agent 列表展示
  - [x] 搜索和篩選 UI
  - [x] 能力標籤展示
  - [x] 聲譽分數展示
  - [x] 分頁支持

#### 🚧 待完成

- [ ] Agent 註冊頁面
- [ ] Agent 詳情頁面
- [ ] Group 管理頁面
- [ ] 聲譽/評價頁面
- [ ] Web3 錢包連接（wagmi + RainbowKit）
- [ ] 合約交互（註冊、評價）
- [ ] IPFS 上傳 UI

---

## 🚧 待開發功能清單

### Phase 1: 核心功能完善 (優先級：🔥 高)

#### 1.1 智能合約完善

**x402 支付證明整合**
- [ ] 定義 Payment Proof 結構體
- [ ] 在 ReputationRegistry 中驗證支付證明
- [ ] 支持多種支付方式（ETH, ERC-20）
- [ ] 支付金額與評價權重關聯

**事件優化**
- [ ] 為所有重要操作添加事件
- [ ] 標準化事件參數（indexed）
- [ ] 前端可訂閱的事件

**Gas 優化**
- [ ] 批量操作支持
- [ ] 存儲結構優化
- [ ] 減少鏈上數據（更多使用 IPFS）

**測試覆蓋**
- [ ] 單元測試覆蓋率 > 90%
- [ ] 整合測試
- [ ] Gas 報告
- [ ] 安全審計準備

#### 1.2 後端核心功能

**Blockchain Service 完善**
```python
# apps/backend/app/services/blockchain.py

待實現：
- [ ] register_agent() - 調用合約註冊 Agent
- [ ] get_agent_card() - 從合約讀取 Agent 詳情
- [ ] submit_feedback() - 提交評價到鏈上
- [ ] get_reputation_score() - 讀取聲譽分數
- [ ] submit_validation() - 提交驗證記錄
- [ ] listen_to_events() - 監聽合約事件
- [ ] get_transaction_status() - 查詢交易狀態
```

**IPFS Service 實現**
```python
# apps/backend/app/services/ipfs_service.py

待實現：
- [ ] upload_json() - 上傳 JSON 到 IPFS
- [ ] upload_file() - 上傳文件到 IPFS
- [ ] get_from_ipfs() - 從 IPFS 讀取數據
- [ ] pin_to_pinata() - 固定到 Pinata
- [ ] 錯誤處理和重試
```

**A2A Protocol Handler 實現**
```python
# apps/backend/app/services/a2a_handler.py

待實現：
- [ ] send_task() - 向 Agent 發送 A2A 任務
- [ ] receive_task() - 接收來自其他 Agent 的任務
- [ ] send_response() - 發送任務響應
- [ ] route_message() - 消息路由
- [ ] handle_workflow() - 多步驟工作流程
- [ ] validate_a2a_message() - 消息驗證
```

**Group Management API**
```python
# apps/backend/app/api/v1/groups.py

待實現：
- [ ] POST /api/v1/groups - 創建群組
- [ ] GET /api/v1/groups/{id} - 獲取群組詳情
- [ ] POST /api/v1/groups/{id}/add-agent - 添加成員
- [ ] POST /api/v1/groups/{id}/remove-agent - 移除成員
- [ ] POST /api/v1/groups/{id}/delegate-task - 群組任務委派
- [ ] GET /api/v1/groups/{id}/tasks - 群組任務列表
```

**Reputation API**
```python
# apps/backend/app/api/v1/reputation.py

待實現：
- [ ] GET /api/v1/reputation/{agent_id} - 獲取聲譽詳情
- [ ] POST /api/v1/reputation/feedback - 提交評價
- [ ] GET /api/v1/reputation/{agent_id}/history - 評價歷史
- [ ] GET /api/v1/reputation/leaderboard - 聲譽排行榜
```

**Validation API**
```python
# apps/backend/app/api/v1/validation.py

待實現：
- [ ] POST /api/v1/validation/submit - 提交驗證
- [ ] GET /api/v1/validation/{agent_id} - 獲取驗證記錄
- [ ] GET /api/v1/validation/{agent_id}/types - 按類型查詢
```

#### 1.3 前端核心頁面

**Agent 註冊頁面** (`apps/frontend/src/pages/RegisterAgent.tsx`)
```typescript
待實現：
- [ ] 連接錢包按鈕（wagmi + RainbowKit）
- [ ] Agent 基本信息表單
  - [ ] 名稱、描述輸入
  - [ ] 能力標籤選擇/輸入
  - [ ] Endpoint URL 配置
- [ ] Metadata 上傳到 IPFS
- [ ] 調用智能合約註冊（metamask 簽名）
- [ ] 交易狀態追蹤
- [ ] 成功後跳轉到 Agent 詳情頁
```

**Agent 詳情頁面** (`apps/frontend/src/pages/AgentDetails.tsx`)
```typescript
待實現：
- [ ] 讀取鏈上 Agent Card 數據
- [ ] 顯示 Agent 完整信息
- [ ] 聲譽分數和歷史圖表
- [ ] 能力列表
- [ ] 最近任務記錄
- [ ] 評價列表（分頁）
- [ ] 委派任務按鈕和表單
- [ ] 如果是所有者：編輯按鈕
```

**Group 管理頁面** (`apps/frontend/src/pages/GroupManagement.tsx`)
```typescript
待實現：
- [ ] 創建 Group 表單
- [ ] Group 列表展示
- [ ] Group 詳情（成員、任務）
- [ ] 添加/移除成員
- [ ] 向 Group 委派任務
- [ ] Task Queue 可視化
```

**聲譽頁面** (`apps/frontend/src/pages/Reputation.tsx`)
```typescript
待實現：
- [ ] Agent 聲譽排行榜
- [ ] 聲譽趨勢圖表
- [ ] 評價提交表單（需要 Payment Proof）
- [ ] 我的評價歷史
- [ ] 篩選器（按能力、時間範圍）
```

**Web3 整合**
```typescript
待實現：
- [ ] wagmi 配置（hooks/useBlockchain.ts）
- [ ] RainbowKit 錢包連接
- [ ] 合約 hooks（useAgentRegistry, useReputation）
- [ ] 交易狀態 toast 通知
- [ ] 網絡切換提示
- [ ] 錯誤處理（用戶拒絕、Gas 不足）
```

---

### Phase 2: 進階功能 (優先級：🔶 中)

#### 2.1 Agent 能力賦能

**Prompt Template 系統**
- [ ] Agent Prompt 模板管理
- [ ] 用戶可上傳自定義 Prompt
- [ ] Prompt 版本控制
- [ ] Prompt 市場（共享/購買優質 Prompt）

**Knowledge Base 整合**
- [ ] 向量資料庫整合（Pinecone / Weaviate）
- [ ] Agent 可上傳知識文件（PDF, docs）
- [ ] RAG（檢索增強生成）支持
- [ ] 知識庫版本管理

**Custom Settings**
- [ ] Agent 參數配置（溫度、最大 token）
- [ ] 行為模式設定（語氣、風格）
- [ ] 輸出格式定義
- [ ] 私密配置（加密存儲）

#### 2.2 Agent 協作與工作流

**Workflow Orchestration**
- [ ] 定義多步驟工作流
- [ ] DAG（有向無環圖）任務依賴
- [ ] 條件分支（if-else, switch）
- [ ] 並行任務執行
- [ ] 失敗重試和回退

**Message Routing**
- [ ] Agent 間異步消息隊列
- [ ] 消息優先級
- [ ] 消息持久化（Redis / RabbitMQ）
- [ ] 消息追蹤和日誌

**Group Dynamics**
- [ ] Group 角色定義（Leader, Member）
- [ ] 任務自動分配算法
- [ ] Group 共識機制
- [ ] Group 收益分配

#### 2.3 支付與經濟系統

**x402 Payment Protocol**
- [ ] 微支付合約實現
- [ ] Payment Proof 生成和驗證
- [ ] 自動結算
- [ ] 支付歷史查詢

**收益分配**
- [ ] Group 收益自動分配
- [ ] 平台手續費（可配置）
- [ ] 推薦獎勵機制
- [ ] 質押和獎勵系統

**定價機制**
- [ ] Agent 自定義定價
- [ ] 動態定價（根據需求）
- [ ] 訂閱制支持
- [ ] 免費試用配額

---

### Phase 3: 生態與優化 (優先級：🔵 低)

#### 3.1 生態建設

**Agent 市場**
- [ ] Agent 發現和搜索優化
- [ ] Agent 標籤系統
- [ ] Agent 推薦算法
- [ ] 熱門 Agent 排行

**社區功能**
- [ ] Agent 開發者論壇
- [ ] 最佳實踐分享
- [ ] 任務模板市場
- [ ] 問題追蹤和支持

**數據分析**
- [ ] Agent 性能儀表板
- [ ] 收益統計
- [ ] 用戶行為分析
- [ ] 生態健康指標

#### 3.2 安全與監控

**安全強化**
- [ ] Rate Limiting
- [ ] API Key 管理
- [ ] Agent 行為審計
- [ ] 惡意行為檢測

**監控系統**
- [ ] APM（Application Performance Monitoring）
- [ ] 錯誤追蹤（Sentry）
- [ ] 鏈上事件監控
- [ ] 告警系統

#### 3.3 多鏈與跨鏈

**多鏈部署**
- [ ] Polygon 部署
- [ ] Arbitrum 部署
- [ ] Optimism 部署
- [ ] BSC 部署

**跨鏈橋接**
- [ ] Agent Identity 跨鏈
- [ ] 聲譽跨鏈同步
- [ ] 跨鏈支付

---

## 📅 開發時間線（建議）

### Milestone 1: MVP 基礎功能 (4-6 週)

**Week 1-2: 智能合約與後端核心**
- [ ] 完善 Blockchain Service
- [ ] 實現 IPFS Service（使用 Pinata）
- [ ] 完成 Agent 註冊流程（端到端）
- [ ] 單元測試和整合測試

**Week 3-4: 前端核心頁面**
- [ ] Web3 錢包連接（RainbowKit）
- [ ] Agent 註冊頁面完整實現
- [ ] Agent 詳情頁面
- [ ] 合約交互和交易狀態管理

**Week 5-6: 聲譽系統與整合測試**
- [ ] 完善 Reputation API
- [ ] 聲譽頁面實現
- [ ] 評價提交流程
- [ ] 端到端測試
- [ ] Bug 修復和優化

**里程碑產出**：
- ✅ 用戶可以註冊 Agent
- ✅ 用戶可以搜索和發現 Agent
- ✅ 用戶可以查看 Agent 詳情和聲譽
- ✅ 用戶可以提交評價
- ✅ 所有數據同步到區塊鏈和 IPFS

### Milestone 2: Group 與任務系統 (3-4 週)

**Week 7-8: Group 功能**
- [ ] Group Service 實現
- [ ] Group API 端點
- [ ] Group 管理頁面
- [ ] 成員管理和權限

**Week 9-10: A2A Protocol 與任務委派**
- [ ] A2A Handler 實現
- [ ] 任務委派流程
- [ ] 任務狀態追蹤
- [ ] Webhook 通知

**里程碑產出**：
- ✅ 用戶可以創建和管理 Group
- ✅ 用戶可以向 Agent/Group 委派任務
- ✅ Agent 可以接收和響應任務
- ✅ 任務狀態實時更新

### Milestone 3: 能力賦能與優化 (4-6 週)

**Week 11-13: Prompt & Knowledge Base**
- [ ] Prompt 模板系統
- [ ] 知識庫整合
- [ ] RAG 實現
- [ ] 配置管理 UI

**Week 14-16: x402 支付與優化**
- [ ] x402 Payment Protocol
- [ ] 支付流程整合
- [ ] 收益分配
- [ ] 性能優化和測試

**里程碑產出**：
- ✅ Agent 可以使用自定義 Prompt
- ✅ Agent 可以上傳知識庫
- ✅ 自動支付和評價綁定
- ✅ 生產環境就緒

---

## 🔧 技術實現細節

### 1. Agent 註冊完整流程

```
┌─────────────┐
│   User      │
│  (Frontend) │
└──────┬──────┘
       │ 1. 填寫 Agent 表單
       │ 2. 連接錢包
       ▼
┌─────────────────────────────────────────┐
│  Frontend                               │
│  - 驗證輸入                              │
│  - 上傳 Metadata 到 Backend             │
└──────┬──────────────────────────────────┘
       │ POST /api/v1/agents/register
       ▼
┌─────────────────────────────────────────┐
│  Backend (FastAPI)                      │
│  1. 準備 Metadata JSON                  │
│  2. 上傳到 IPFS (Pinata)                │
│     └─> 獲得 metadata_uri (ipfs://...)  │
│  3. 調用區塊鏈合約                       │
│     └─> registerAgent(...)              │
│  4. 等待交易確認                         │
│  5. 存儲到 MongoDB (Off-chain cache)    │
│  6. 返回 token_id 和 tx_hash            │
└──────┬──────────────────────────────────┘
       │ token_id, tx_hash
       ▼
┌─────────────────────────────────────────┐
│  Frontend                               │
│  - 顯示交易狀態                          │
│  - 交易確認後跳轉到 Agent 詳情           │
└─────────────────────────────────────────┘

區塊鏈上：
┌───────────────────────────────────────────┐
│  AgentIdentityRegistry Contract          │
│  - 鑄造 ERC-721 NFT (token_id)           │
│  - 存儲 Agent Card (name, endpoint, ...)│
│  - 發射 AgentRegistered 事件            │
└───────────────────────────────────────────┘

IPFS 上：
┌───────────────────────────────────────────┐
│  Agent Metadata JSON                     │
│  {                                       │
│    "name": "...",                        │
│    "description": "...",                 │
│    "capabilities": [...],                │
│    "version": "1.0",                     │
│    "created_at": "..."                   │
│  }                                       │
└───────────────────────────────────────────┘
```

### 2. Agent 發現與任務委派流程

```
User 搜索 "coding" 能力的 Agent
       │
       ▼
Frontend: POST /api/v1/agents/discover
       │ { capability: "coding", min_reputation: 4.0 }
       ▼
Backend: Agent Manager
       │
       ├─> MongoDB 快速查詢
       │   SELECT * FROM agents
       │   WHERE "coding" IN capabilities
       │   AND reputation_score >= 4.0
       │   ORDER BY reputation_score DESC
       │
       ├─> 並行從區塊鏈讀取最新聲譽
       │   (更新 MongoDB cache)
       │
       └─> 返回匹配的 Agent 列表
       │
       ▼
Frontend: 顯示 Agent 卡片
       │
User 選擇 Agent #123，點擊「委派任務」
       │
       ▼
Frontend: POST /api/v1/agents/123/delegate-task
       │ { 
       │   "task_type": "code_generation",
       │   "requirements": "...",
       │   "deadline": "..."
       │ }
       ▼
Backend: A2A Handler
       │
       ├─> 1. 查詢 Agent #123 的 endpoint
       │
       ├─> 2. 構建 A2A Protocol 消息
       │      {
       │        "protocol": "a2a/v1",
       │        "type": "task_request",
       │        "from": "platform",
       │        "to": "agent_123",
       │        "payload": { ... }
       │      }
       │
       ├─> 3. 發送 HTTP POST 到 Agent endpoint
       │      POST https://agent-123.example.com/a2a/task
       │
       ├─> 4. 創建 Task 記錄到 MongoDB
       │
       └─> 5. 返回 task_id
       │
       ▼
Agent #123 接收任務
       │
       ├─> 處理任務
       │
       ├─> 回傳結果（A2A Protocol Response）
       │
       └─> Platform 更新 Task 狀態
       │
       ▼
User 查看任務結果
       │
       └─> 提交評價（需包含 Payment Proof）
```

### 3. 聲譽系統與 x402 整合

```
User 完成與 Agent 的交易
       │
       ├─> 1. 通過 x402 支付
       │      - 生成 Payment Proof
       │      - 包含：amount, timestamp, signature
       │
       ▼
User 提交評價
       │
Frontend: POST /api/v1/reputation/feedback
       │ {
       │   "agent_id": 123,
       │   "rating": 5,
       │   "comment": "Excellent work!",
       │   "payment_proof": { ... }
       │ }
       ▼
Backend: Reputation API
       │
       ├─> 1. 驗證 Payment Proof 簽名
       │
       ├─> 2. 檢查 Proof 是否已使用
       │
       ├─> 3. 調用智能合約
       │      submitFeedback(
       │        agent_id,
       │        rating,
       │        payment_proof
       │      )
       │
       ▼
ReputationRegistry Contract
       │
       ├─> 1. 驗證 Payment Proof 唯一性
       │
       ├─> 2. 存儲評價記錄
       │
       ├─> 3. 更新平均分數
       │      new_avg = (old_avg * count + rating) / (count + 1)
       │
       ├─> 4. 發射 FeedbackSubmitted 事件
       │
       └─> 返回交易 hash
       │
       ▼
Backend: 更新 MongoDB cache
       │
       └─> agent.reputation_score = new_avg
       │   agent.feedback_count += 1
       │
       ▼
Frontend: 顯示成功通知
```

---

## 🎨 前端組件架構

```
src/
├── components/
│   ├── ui/                     # shadcn/ui 基礎組件
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   │
│   ├── agent/                  # Agent 相關組件
│   │   ├── AgentCard.tsx       # Agent 卡片
│   │   ├── AgentList.tsx       # Agent 列表
│   │   ├── AgentSearchBar.tsx  # 搜索欄
│   │   ├── AgentFilter.tsx     # 篩選器
│   │   ├── CapabilityBadge.tsx # 能力標籤
│   │   ├── ReputationScore.tsx # 聲譽分數顯示
│   │   └── AgentForm.tsx       # Agent 註冊表單
│   │
│   ├── group/                  # Group 相關組件
│   │   ├── GroupCard.tsx
│   │   ├── GroupMemberList.tsx
│   │   ├── GroupTaskQueue.tsx
│   │   └── GroupForm.tsx
│   │
│   ├── task/                   # 任務相關組件
│   │   ├── TaskCard.tsx
│   │   ├── TaskList.tsx
│   │   ├── TaskStatus.tsx
│   │   └── TaskForm.tsx
│   │
│   ├── reputation/             # 聲譽相關組件
│   │   ├── FeedbackForm.tsx    # 評價表單
│   │   ├── FeedbackList.tsx    # 評價列表
│   │   ├── ReputationChart.tsx # 聲譽趨勢圖
│   │   └── Leaderboard.tsx     # 排行榜
│   │
│   ├── web3/                   # Web3 組件
│   │   ├── ConnectWallet.tsx   # 錢包連接按鈕
│   │   ├── NetworkSwitch.tsx   # 網絡切換
│   │   ├── TransactionStatus.tsx # 交易狀態
│   │   └── AddressDisplay.tsx  # 地址顯示
│   │
│   └── layout/
│       ├── Layout.tsx          # 主佈局
│       ├── Header.tsx          # 頂部導航
│       ├── Sidebar.tsx         # 側邊欄
│       └── Footer.tsx          # 底部
│
├── hooks/                      # 自定義 hooks
│   ├── useAgents.ts            # Agent 相關 hooks
│   ├── useGroups.ts            # Group 相關 hooks
│   ├── useReputation.ts        # 聲譽相關 hooks
│   ├── useTasks.ts             # 任務相關 hooks
│   ├── useBlockchain.ts        # 區塊鏈交互
│   ├── useIPFS.ts              # IPFS 上傳
│   └── useWeb3.ts              # Web3 通用 hooks
│
├── lib/                        # 工具庫
│   ├── api.ts                  # API 客戶端
│   ├── contracts.ts            # 合約 ABIs 和地址
│   ├── ipfs.ts                 # IPFS 工具
│   ├── utils.ts                # 通用工具函數
│   └── constants.ts            # 常量定義
│
├── store/                      # 狀態管理 (Zustand)
│   ├── agentStore.ts
│   ├── userStore.ts
│   └── notificationStore.ts
│
├── types/                      # TypeScript 類型
│   ├── agent.ts
│   ├── group.ts
│   ├── task.ts
│   ├── reputation.ts
│   └── index.ts
│
└── pages/                      # 頁面組件
    ├── Dashboard.tsx           # ✅ 已實現
    ├── RegisterAgent.tsx       # 🚧 待完善
    ├── AgentDetails.tsx        # 🚧 待實現
    ├── GroupManagement.tsx     # 🚧 待實現
    └── Reputation.tsx          # 🚧 待實現
```

---

## 🗄️ 數據庫設計

### MongoDB Collections

#### `agents` Collection
```javascript
{
  "_id": ObjectId,
  "token_id": 123,                    // 對應鏈上 NFT ID
  "name": "Code Generator Agent",
  "description": "...",
  "capabilities": ["coding", "testing", "debugging"],
  "endpoint": "https://agent.example.com/a2a",
  "metadata_uri": "ipfs://Qm...",
  "owner_address": "0x...",
  "created_at": ISODate,
  "updated_at": ISODate,
  "is_active": true,
  
  // Cache (從區塊鏈定期同步)
  "reputation_score": 4.5,
  "feedback_count": 120,
  
  // Stats
  "total_tasks": 500,
  "completed_tasks": 480,
  "failed_tasks": 20,
  
  // Indexes
  "capabilities_index": ["coding", "testing"],  // 用於快速搜索
}

Indexes:
- { "token_id": 1 } unique
- { "endpoint": 1 } unique
- { "owner_address": 1 }
- { "capabilities": 1 }
- { "reputation_score": -1 }
- { "is_active": 1, "reputation_score": -1 }
```

#### `groups` Collection
```javascript
{
  "_id": ObjectId,
  "group_id": "uuid",
  "name": "Full-stack Dev Team",
  "description": "...",
  "owner_address": "0x...",
  "members": [
    {
      "agent_id": 123,
      "role": "leader",
      "joined_at": ISODate
    },
    {
      "agent_id": 456,
      "role": "member",
      "joined_at": ISODate
    }
  ],
  "created_at": ISODate,
  "updated_at": ISODate,
  "is_active": true,
  "total_tasks": 50,
  "completed_tasks": 45
}

Indexes:
- { "group_id": 1 } unique
- { "owner_address": 1 }
- { "members.agent_id": 1 }
```

#### `tasks` Collection
```javascript
{
  "_id": ObjectId,
  "task_id": "uuid",
  "agent_id": 123,                    // null if group task
  "group_id": "uuid",                 // null if single agent
  "agent_name": "...",
  "task_type": "code_generation",
  "task_data": {
    "requirements": "...",
    "input": { ... },
    "deadline": ISODate
  },
  "status": "pending",                // pending, in_progress, completed, failed
  "created_at": ISODate,
  "updated_at": ISODate,
  "started_at": ISODate,
  "completed_at": ISODate,
  "result": {
    "output": { ... },
    "metadata": { ... }
  },
  "error": null                       // 失敗時的錯誤信息
}

Indexes:
- { "task_id": 1 } unique
- { "agent_id": 1, "status": 1 }
- { "group_id": 1, "status": 1 }
- { "created_at": -1 }
```

#### `feedbacks` Collection (Cache from blockchain)
```javascript
{
  "_id": ObjectId,
  "agent_id": 123,
  "rating": 5,
  "comment": "Excellent!",
  "reviewer_address": "0x...",
  "payment_proof": {
    "amount": "0.1",
    "token": "ETH",
    "timestamp": ISODate,
    "signature": "0x..."
  },
  "tx_hash": "0x...",               // 鏈上交易 hash
  "created_at": ISODate
}

Indexes:
- { "agent_id": 1, "created_at": -1 }
- { "reviewer_address": 1 }
```

---

## 🔐 環境變量配置

### Backend `.env`
```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=a2a_agent_ecosystem

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:5173"]

# Blockchain
WEB3_PROVIDER_URI=http://127.0.0.1:8545  # 本地 Hardhat
# WEB3_PROVIDER_URI=https://sepolia.infura.io/v3/YOUR_KEY  # Sepolia
IDENTITY_REGISTRY_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
REPUTATION_REGISTRY_ADDRESS=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
VALIDATION_REGISTRY_ADDRESS=0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0

# IPFS (Pinata)
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_API_KEY=your_pinata_secret
IPFS_GATEWAY=https://gateway.pinata.cloud

# A2A Protocol
A2A_ENDPOINT=http://localhost:8000/a2a

# Security
JWT_SECRET=your_jwt_secret_key
API_KEY_SALT=your_api_key_salt
```

### Frontend `.env`
```bash
# API
VITE_API_BASE_URL=http://localhost:8000

# Blockchain
VITE_CHAIN_ID=31337  # Hardhat local
# VITE_CHAIN_ID=11155111  # Sepolia
VITE_RPC_URL=http://127.0.0.1:8545
VITE_IDENTITY_REGISTRY_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
VITE_REPUTATION_REGISTRY_ADDRESS=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
VITE_VALIDATION_REGISTRY_ADDRESS=0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0

# IPFS
VITE_IPFS_GATEWAY=https://gateway.pinata.cloud

# WalletConnect
VITE_WALLETCONNECT_PROJECT_ID=your_walletconnect_project_id
```

### Contracts `.env`
```bash
# Deployment
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80  # Hardhat Account #0
DEPLOYER_ADDRESS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

# Networks
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
MAINNET_RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY

# Etherscan
ETHERSCAN_API_KEY=your_etherscan_api_key

# Gas
REPORT_GAS=false
```

---

## 📊 關鍵指標 (KPIs)

### 開發階段 KPIs

**代碼質量**
- [ ] 測試覆蓋率 > 80%
- [ ] 無嚴重 linter 錯誤
- [ ] TypeScript strict mode 通過
- [ ] 所有 API 端點有文檔

**性能指標**
- [ ] API 響應時間 < 200ms (p95)
- [ ] 前端 Lighthouse 分數 > 90
- [ ] 合約 Gas 優化（< 300k gas per tx）

**功能完整性**
- [ ] Agent 註冊流程端到端可用
- [ ] Agent 發現功能可用
- [ ] 評價系統可用
- [ ] 所有核心 API 實現

### 上線後 KPIs

**用戶指標**
- 註冊 Agent 數量
- 活躍 Agent 數量（7日/30日）
- 任務委派數量
- 用戶留存率

**生態指標**
- Group 創建數量
- Agent 協作次數
- 平均聲譽分數
- 評價提交率

**技術指標**
- API 可用性 > 99.9%
- 區塊鏈交易成功率 > 95%
- IPFS 上傳成功率 > 99%

---

## 🚨 風險與挑戰

### 技術風險

1. **區塊鏈交易延遲**
   - 影響：用戶體驗差
   - 緩解：使用樂觀 UI 更新，MongoDB cache

2. **Gas 費用過高**
   - 影響：用戶不願上鏈
   - 緩解：Layer 2 部署，批量操作

3. **IPFS 穩定性**
   - 影響：Metadata 無法讀取
   - 緩解：使用 Pinata pinning，備份到 S3

4. **A2A Protocol 標準化**
   - 影響：不同 Agent 無法互操作
   - 緩解：嚴格遵循協議規範，提供 SDK

### 產品風險

1. **Agent 質量參差不齊**
   - 影響：用戶體驗差
   - 緩解：驗證系統、聲譽門檻、審核機制

2. **冷啟動問題**
   - 影響：早期無足夠 Agent
   - 緩解：官方提供示範 Agent，激勵早期開發者

3. **網絡效應不足**
   - 影響：生態無法起飛
   - 緩解：先在垂直領域（如開發工具）建立網絡

### 安全風險

1. **智能合約漏洞**
   - 影響：資金損失
   - 緩解：安全審計、Bug Bounty、保險

2. **惡意 Agent 攻擊**
   - 影響：用戶資產/數據損失
   - 緩解：沙盒執行、權限控制、黑名單

3. **Sybil 攻擊（刷聲譽）**
   - 影響：聲譽系統失效
   - 緩解：Payment Proof 驗證、反作弊算法

---

## 📚 參考資源

### 協議與標準
- [A2A Protocol Specification](https://github.com/a2aproject/a2a-samples)
- [ERC-8004 Draft](https://eips.ethereum.org/EIPS/eip-8004)
- [ERC-721 Standard](https://eips.ethereum.org/EIPS/eip-721)
- [x402 Payment Protocol](https://github.com/x402project)

### 技術文檔
- [Hardhat Documentation](https://hardhat.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [wagmi Documentation](https://wagmi.sh/)
- [RainbowKit Documentation](https://www.rainbowkit.com/)
- [Pinata IPFS API](https://docs.pinata.cloud/)

### 相關項目
- [LangChain](https://www.langchain.com/) - Agent 框架
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) - 自主 Agent
- [CrewAI](https://www.crewai.com/) - Multi-Agent 協作

---

## 💬 聯絡與支持

- **GitHub Issues**: 技術問題和 Bug 報告
- **開發文檔**: 查看各模組的 README
- **API 文檔**: http://localhost:8000/docs

---

**下一步行動**: 根據此路線圖，建議從 Phase 1 開始，優先完成 MVP 核心功能。建議每週 review 進度並調整優先級。

