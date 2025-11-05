# 🐍 後端啟動指南

## ✅ 依賴已安裝完成！

所有 Python 依賴已成功安裝到 venv 中（包括 FastAPI, Web3.py, MongoDB 等）。

## 🚀 快速啟動

### 方法 1：直接啟動（需要 MongoDB）

```bash
# 確保 MongoDB 正在運行
mongod

# 在新終端啟動後端
cd /Users/johnnylin/Documents/a2a-poc
pnpm backend:dev
```

### 方法 2：使用 Docker MongoDB

```bash
# 啟動 MongoDB Docker 容器
docker run -d -p 27017:27017 --name a2a-mongodb mongo

# 啟動後端
pnpm backend:dev
```

### 方法 3：使用 MongoDB Atlas（雲端）

1. 註冊 [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)（免費）
2. 創建集群並獲取連接字串
3. 更新 `.env`:
   ```
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
   ```
4. 啟動後端

## 📝 配置環境變量

編輯 `apps/backend/.env`（如果不存在則創建）：

```bash
# MongoDB（選擇一種）
MONGODB_URL=mongodb://localhost:27017  # 本地
# 或
# MONGODB_URL=mongodb+srv://...  # Atlas

# 其他配置
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# 合約地址（部署後填入）
IDENTITY_REGISTRY_ADDRESS=
REPUTATION_REGISTRY_ADDRESS=
VALIDATION_REGISTRY_ADDRESS=
```

## 🧪 測試啟動

```bash
# 啟動後端
pnpm backend:dev

# 在另一個終端測試
curl http://localhost:8000/
curl http://localhost:8000/health
```

## 🌐 訪問 API 文檔

啟動後訪問：
- http://localhost:8000/docs （Swagger UI）
- http://localhost:8000/redoc （ReDoc）

## 🐛 常見問題

### 1. MongoDB 連接失敗

**症狀**：`Database not initialized`

**解決方案**：
```bash
# Mac
brew services start mongodb-community

# 或使用 Docker
docker run -d -p 27017:27017 mongo
```

### 2. Port 8000 被占用

**解決方案**：
```bash
# 查找並關閉占用進程
lsof -i :8000
kill -9 <PID>

# 或修改 .env 中的 API_PORT
```

### 3. Python 依賴問題

**解決方案**：
```bash
cd apps/backend
./venv/bin/pip install -r requirements.txt
```

## 📊 成功啟動的標誌

你應該看到：
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
✅ Connected to MongoDB: a2a_ecosystem
✅ Database indexes created
🌐 Server running on 0.0.0.0:8000
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 🎉 下一步

1. 部署智能合約
2. 更新 `.env` 中的合約地址
3. 註冊第一個 Agent
4. 啟動前端查看 Dashboard

