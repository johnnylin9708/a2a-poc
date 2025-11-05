# @a2a/contracts

ERC-8004 智能合約實作 - Agent Identity, Reputation & Validation Registry

## 合約架構

### 1. AgentIdentityRegistry.sol
- 基於 ERC-721 的 Agent 身份註冊表
- 每個 Agent 獲得唯一的 NFT ID
- 存儲 Agent Card 信息（能力、endpoint 等）

### 2. ReputationRegistry.sol
- 去中心化的評價系統
- 與 x402 支付證明綁定
- 計算和存儲 Agent 聲譽分數

### 3. ValidationRegistry.sol
- 第三方驗證記錄
- 支持 TEE、零知識證明等多種驗證類型
- 增強 Agent 可信度

## 開發

```bash
# 安裝依賴
pnpm install

# 編譯合約
pnpm compile

# 運行測試
pnpm test

# 啟動本地節點
pnpm node

# 部署到本地網絡
pnpm deploy:local

# 部署到 Sepolia 測試網
pnpm deploy:sepolia
```

## 測試覆蓋率

```bash
pnpm coverage
```

## Gas 報告

```bash
REPORT_GAS=true pnpm test
```

## 合約驗證

```bash
pnpm verify --network sepolia DEPLOYED_CONTRACT_ADDRESS
```
