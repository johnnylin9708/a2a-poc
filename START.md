# 🚀 啟動指南

## 快速啟動所有服務

### 方法 1：使用 Turbo 並行啟動（推薦）

```bash
pnpm dev
# 或
pnpm dev:all
```

這會同時啟動：
- ⛓️ **Hardhat 本地節點** (http://localhost:8545)
- 🐍 **Backend API** (http://localhost:8000)
- ⚛️ **Frontend** (http://localhost:5173)

### 方法 2：分別啟動（三個終端）

如果你需要更好的日誌控制，可以在三個終端分別啟動：

**Terminal 1 - 區塊鏈節點:**
```bash
pnpm contracts:dev
# 或
cd apps/contracts && pnpm dev
```

**Terminal 2 - 後端 API:**
```bash
pnpm backend:dev
# 或
cd apps/backend && pnpm dev
```

**Terminal 3 - 前端:**
```bash
pnpm frontend:dev
# 或
cd apps/frontend && pnpm dev
```

## 📦 初次設置

### 1. 安裝依賴

```bash
# Root 依賴
pnpm install

# Python 依賴
cd apps/backend
python -m venv venv
source venv/bin/activate  # Mac/Linux
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
cd ../..
```

### 2. 配置環境變量

```bash
# 後端環境變量
cd apps/backend
cp .env.example .env
# 編輯 .env 文件

# 合約環境變量（如需部署到測試網）
cd ../contracts
cp .env.example .env
# 編輯 .env 文件
```

### 3. 部署智能合約（首次運行）

```bash
# 啟動本地節點（Terminal 1）
pnpm contracts:dev

# 在新的 Terminal 2 中部署合約
cd apps/contracts
pnpm compile
pnpm deploy:local

# 記下合約地址，更新到 apps/backend/.env
```

## 🎮 常用命令

### 開發

```bash
pnpm dev                 # 啟動所有服務（Turbo 並行）
pnpm dev:all             # 強制並行啟動所有服務
pnpm contracts:dev       # 只啟動區塊鏈節點
pnpm backend:dev         # 只啟動後端
pnpm frontend:dev        # 只啟動前端
```

### 構建

```bash
pnpm build              # 構建所有項目
pnpm --filter @a2a/contracts compile
pnpm --filter @a2a/frontend build
```

### 測試

```bash
pnpm test               # 運行所有測試
cd apps/contracts && pnpm test    # 合約測試
cd apps/backend && pytest         # 後端測試
```

### 清理

```bash
pnpm clean              # 清理所有構建產物
```

## 🔍 訪問服務

- 🌐 **前端**: http://localhost:5173
- 📡 **API 文檔**: http://localhost:8000/docs
- ⛓️ **區塊鏈 RPC**: http://localhost:8545

## 🐛 常見問題

### Backend 啟動失敗

確保已安裝 Python 依賴：
```bash
cd apps/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend 編譯錯誤

重新安裝依賴：
```bash
pnpm install
```

### Hardhat 端口被占用

檢查並關閉占用 8545 端口的進程：
```bash
lsof -i :8545
kill -9 <PID>
```

### MongoDB 連接失敗

確保 MongoDB 正在運行：
```bash
# Mac
brew services start mongodb-community

# 或使用 Docker
docker run -d -p 27017:27017 mongo
```

## 💡 開發技巧

1. **使用 Turbo 緩存**: Turbo 會自動緩存構建結果，加快後續構建速度
2. **並行開發**: `pnpm dev` 會並行啟動所有服務，但日誌會混在一起
3. **分離日誌**: 如果需要查看特定服務的日誌，使用分別啟動的方式
4. **熱重載**: 前端和後端都支持熱重載，修改代碼會自動刷新

## 📚 下一步

- 📖 閱讀 [README.md](./README.md) 了解專案架構
- 🚀 查看 [QUICKSTART.md](./QUICKSTART.md) 快速上手
- 📝 查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 部署指南

