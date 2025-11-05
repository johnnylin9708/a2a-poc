#!/bin/bash

# A2A Demo Quick Start Script
# 快速启动演示脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  A2A Agent Ecosystem - Demo Launcher${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 未安装${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 创建 Python 虚拟环境...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}✓${NC} 激活虚拟环境"
source venv/bin/activate

# Install dependencies
if [ ! -f "venv/.installed" ]; then
    echo -e "${YELLOW}📦 安装依赖...${NC}"
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    touch venv/.installed
    echo -e "${GREEN}✓${NC} 依赖安装完成"
else
    echo -e "${GREEN}✓${NC} 依赖已安装"
fi

# Check platform status
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  检查平台状态"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend 运行中 (http://localhost:8000)"
else
    echo -e "${RED}❌ Backend 未运行${NC}"
    echo -e "${YELLOW}请在另一个终端运行:${NC} cd .. && pnpm dev"
    exit 1
fi

# Check blockchain
if curl -s -X POST -H "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
    http://localhost:8545 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Blockchain 运行中 (http://localhost:8545)"
else
    echo -e "${RED}❌ Blockchain 未运行${NC}"
    echo -e "${YELLOW}请在另一个终端运行:${NC} cd ../apps/contracts && pnpm hardhat node"
    exit 1
fi

# Check MongoDB
if pgrep -x mongod > /dev/null; then
    echo -e "${GREEN}✓${NC} MongoDB 运行中"
else
    echo -e "${YELLOW}⚠️  MongoDB 可能未运行${NC}"
fi

echo ""
echo -e "${GREEN}✅ 所有服务运行正常${NC}"
echo ""

# Menu
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  选择操作"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  1) 设置演示数据 (首次运行)"
echo "  2) 运行完整演示"
echo "  3) 运行快速演示 (跳过等待)"
echo "  4) 检查系统状态"
echo "  5) 清理并重置"
echo "  0) 退出"
echo ""
read -p "请选择 [1-5]: " choice

case $choice in
    1)
        echo ""
        echo -e "${CYAN}📋 设置演示数据...${NC}"
        echo ""
        python scenarios/setup_demo_data.py
        ;;
    2)
        echo ""
        echo -e "${CYAN}🚀 运行完整演示...${NC}"
        echo ""
        python scenarios/demo_todo_app.py
        ;;
    3)
        echo ""
        echo -e "${CYAN}⚡ 运行快速演示...${NC}"
        echo ""
        python scenarios/demo_todo_app.py --fast
        ;;
    4)
        echo ""
        echo -e "${CYAN}📊 检查系统状态...${NC}"
        echo ""
        python scenarios/demo_todo_app.py --status
        ;;
    5)
        echo ""
        echo -e "${YELLOW}⚠️  清理数据...${NC}"
        echo ""
        read -p "确认清理所有数据? (y/N): " confirm
        if [ "$confirm" = "y" ]; then
            mongosh a2a_ecosystem --eval "db.dropDatabase()" 2>/dev/null || echo "MongoDB 清理失败"
            echo -e "${GREEN}✓${NC} 数据已清理"
        fi
        ;;
    0)
        echo ""
        echo -e "${GREEN}👋 再见！${NC}"
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ 完成！${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

