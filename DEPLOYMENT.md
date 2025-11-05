# 🚀 Deployment Guide

完整的部署指南，用於在本地開發環境和生產環境中部署 A2A Agent Ecosystem。

## 📋 前置要求

### 系統要求
- **Node.js**: >= 18.0.0
- **Python**: >= 3.11
- **pnpm**: >= 8.0.0
- **MongoDB**: 本地或 MongoDB Atlas
- **IPFS**: 本地節點或 Pinata 帳號（可選）
- **Ethereum Node**: Hardhat 本地節點、Infura、或 Alchemy

### 開發工具
- Git
- VS Code（推薦）
- MetaMask 或其他 Web3 錢包

## 🛠️ 本地開發環境設置

### 步驟 1: 克隆專案

```bash
cd /Users/johnnylin/Documents/a2a-poc
```

### 步驟 2: 安裝依賴

```bash
# 安裝 pnpm（如果尚未安裝）
npm install -g pnpm

# 安裝所有依賴
pnpm install

# 安裝 Python 依賴
cd apps/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ../..
```

### 步驟 3: 設置環境變量

#### 智能合約環境變量
```bash
cd apps/contracts
cp .env.example .env
# 編輯 .env 並填入:
# - SEPOLIA_RPC_URL (from Infura/Alchemy)
# - PRIVATE_KEY (for deployment)
# - ETHERSCAN_API_KEY (for verification)
```

#### 後端環境變量
```bash
cd apps/backend
cp .env.example .env
# 編輯 .env 並填入:
# - MONGODB_URL
# - WEB3_PROVIDER_URI
# - Contract addresses (after deployment)
# - IPFS 配置
```

#### 前端環境變量
```bash
cd apps/frontend
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_CHAIN_ID=31337
EOF
```

### 步驟 4: 啟動本地區塊鏈

在新的終端窗口中：

```bash
cd apps/contracts
pnpm node
```

這將啟動 Hardhat 本地節點（默認在 `http://localhost:8545`）

### 步驟 5: 部署智能合約

在另一個終端窗口中：

```bash
cd apps/contracts
pnpm compile
pnpm deploy:local
```

部署完成後，記下合約地址並更新 `apps/backend/.env` 中的：
- `IDENTITY_REGISTRY_ADDRESS`
- `REPUTATION_REGISTRY_ADDRESS`
- `VALIDATION_REGISTRY_ADDRESS`

### 步驟 6: 啟動 MongoDB

確保 MongoDB 正在運行：

```bash
# 如果使用本地 MongoDB
mongod

# 或使用 MongoDB Atlas（更新 backend/.env 中的 MONGODB_URL）
```

### 步驟 7: 啟動後端 API

```bash
cd apps/backend
source venv/bin/activate
python -m app.main
```

後端將運行在 `http://localhost:8000`

訪問 API 文檔: http://localhost:8000/docs

### 步驟 8: 啟動前端

在新的終端窗口中：

```bash
cd apps/frontend
pnpm dev
```

前端將運行在 `http://localhost:5173`

## 🧪 測試

### 運行智能合約測試

```bash
cd apps/contracts
pnpm test
```

### 運行後端測試

```bash
cd apps/backend
pytest
```

### 運行前端測試

```bash
cd apps/frontend
pnpm test
```

## 📦 生產環境部署

### 部署智能合約到 Sepolia 測試網

1. 確保 `.env` 中有正確的配置
2. 確保部署錢包有足夠的 Sepolia ETH

```bash
cd apps/contracts
pnpm deploy:sepolia
```

3. 驗證合約：

```bash
pnpm verify --network sepolia <CONTRACT_ADDRESS>
```

### 部署後端到生產環境

#### 使用 Docker

```bash
cd apps/backend

# 創建 Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# 構建
docker build -t a2a-backend .

# 運行
docker run -p 8000:8000 --env-file .env a2a-backend
```

#### 使用傳統部署

```bash
# 安裝依賴
pip install -r requirements.txt

# 使用 Gunicorn 運行
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 部署前端到生產環境

#### 構建靜態資產

```bash
cd apps/frontend
pnpm build
```

構建輸出在 `dist/` 目錄

#### 部署到 Vercel

```bash
# 安裝 Vercel CLI
npm i -g vercel

# 部署
cd apps/frontend
vercel
```

#### 部署到 Netlify

```bash
# 使用 Netlify CLI
npm i -g netlify-cli

cd apps/frontend
netlify deploy --prod
```

#### 使用 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/a2a-poc/apps/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 🔐 安全性檢查清單

- [ ] 智能合約已經過審計
- [ ] 私鑰使用環境變量，不提交到 Git
- [ ] API 啟用 CORS 限制
- [ ] MongoDB 啟用認證
- [ ] 使用 HTTPS（生產環境）
- [ ] 合約地址已驗證
- [ ] 設置 rate limiting
- [ ] 啟用日誌監控

## 📊 監控和維護

### 日誌監控

後端日誌位置：
- Development: stdout
- Production: `/var/log/a2a-backend/`

### 數據庫備份

```bash
# MongoDB 備份
mongodump --uri="mongodb://localhost:27017/a2a_ecosystem" --out=/backup/

# 恢復
mongorestore --uri="mongodb://localhost:27017/a2a_ecosystem" /backup/
```

### 健康檢查端點

- Backend: http://localhost:8000/health
- Frontend: http://localhost:5173

## 🐛 故障排除

### 合約部署失敗

1. 檢查錢包 ETH 餘額
2. 確認 RPC URL 正確
3. 檢查 gas price 設置

### 後端無法連接到 MongoDB

1. 確認 MongoDB 正在運行
2. 檢查 `MONGODB_URL` 配置
3. 確認網絡連接

### 前端無法調用 API

1. 檢查 backend 是否運行
2. 確認 CORS 配置
3. 檢查 Vite proxy 配置

## 📚 相關資源

- [Hardhat 文檔](https://hardhat.org/docs)
- [FastAPI 文檔](https://fastapi.tiangolo.com/)
- [Vite 文檔](https://vitejs.dev/)
- [wagmi 文檔](https://wagmi.sh/)
- [ERC-8004 標準](https://eips.ethereum.org/EIPS/eip-8004)

## 🆘 獲取幫助

如有問題，請：
1. 檢查日誌文件
2. 查看 GitHub Issues
3. 參考文檔
4. 聯繫開發團隊

