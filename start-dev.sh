#!/bin/bash
# Smart Commercial Calculator - 開發環境啟動腳本 (Linux/macOS)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"  # 脚本在项目根目录，不在 scripts/ 下

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  智慧商用計算機 - 開發環境啟動${NC}"
echo -e "${CYAN}========================================${NC}"

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}錯誤: 找不到 python3${NC}"
    exit 1
fi

# 檢查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}錯誤: 找不到 node${NC}"
    exit 1
fi

# 檢查後端虛擬環境
BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$BACKEND_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}建立 Python 虛擬環境...${NC}"
    python3 -m venv "$VENV_DIR"
fi

# 啟動後端
echo -e "${GREEN}啟動後端服務...${NC}"
source "$VENV_DIR/bin/activate"
cd "$BACKEND_DIR"

# 檢查依賴

found=0
# 迴圈會遍歷所有匹配的路徑
for file in "$VENV_DIR/lib/python"*/site-packages/fastapi*
do
    # 檢查匹配到的結果是否確實是一個文件或目錄
    if [ -e "$file" ]; then
        found=1
        break # 找到第一個就足夠了，跳出迴圈
    fi
done

if [ "$found" -eq 0 ]; then
    echo -e "${YELLOW}安裝後端依賴...${NC}"
    pip install -r requirements.txt
fi

# 啟動 uvicorn (背景執行)
python -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}後端 PID: $BACKEND_PID${NC}"

# 等待後端啟動
echo -e "${YELLOW}等待後端啟動...${NC}"
sleep 3

# 檢查後端是否成功啟動
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}後端啟動失敗${NC}"
    exit 1
fi

# 啟動前端
echo -e "${GREEN}啟動前端應用...${NC}"
cd "$PROJECT_ROOT/frontend"

# 檢查依賴
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}安裝前端依賴...${NC}"
    npm install
fi

# 啟動 Electron
npm run electron:dev

# 清理
echo -e "${YELLOW}關閉後端服務...${NC}"
kill $BACKEND_PID 2>/dev/null || true

echo -e "${GREEN}已關閉所有服務${NC}"