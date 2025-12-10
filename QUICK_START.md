# 快速啟動指南

## ✅ 後端測試已通過

所有後端功能測試都已通過！

```
✅ 依賴模組 - 已安裝
✅ ExchangeRate 類 - 正常
✅ AI_Agent 類 - 正常
✅ 匯率查詢 - 成功 (USD: 買入 30.795, 賣出 31.465)
✅ IPC Server - 正常
```

## 啟動步驟

### 方法一：使用開發模式（推薦）

1. **終端 1 - 啟動 Vite 開發伺服器**
   ```bash
   cd frontend
   pnpm run dev
   ```
   等待看到 "Local: http://localhost:5173"

2. **終端 2 - 啟動 Electron**
   ```bash
   cd frontend
   pnpm run electron:dev
   ```

### 方法二：構建並運行

```bash
cd frontend
pnpm run build
pnpm run electron:start
```

## 使用銀行員功能

1. 啟動應用後，你會看到計算機界面
2. 點擊綠色的「**銀行員匯率模式**」按鈕（帶有 💲 圖標）
3. 右側面板會展開，顯示：
   - 貨幣選擇下拉選單
   - 當前匯率資訊
   - 台幣金額輸入框
   - 計算按鈕
4. 選擇貨幣，系統會自動查詢最新匯率
5. 輸入台幣金額
6. 點擊「計算換匯金額」查看結果

## 檢查 Python 進程

打開 Electron DevTools (View -> Toggle Developer Tools)，你應該看到：

```
Starting Python backend: /path/to/backend/ipc_server.py
Backend exists: true
Python process spawned with PID: 12345
Warning: Calculator modules not available: No module named 'core'
Bank Agent initialized successfully
Python backend started successfully
```

⚠️ "Calculator modules not available" 是正常的警告，不影響銀行員功能。

## 故障排除

### 問題：Python process not available

**解決方案：**
1. 確保 Python 3 已安裝：
   ```bash
   which python3
   python3 --version
   ```

2. 確保依賴已安裝：
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. 測試後端：
   ```bash
   python3 test_backend.py
   ```

### 問題：匯率查詢失敗

**解決方案：**
1. 設置 FinMind API key（可選，無 key 也可以使用但可能有限制）：
   ```bash
   # 在項目根目錄創建 .env 文件
   echo "FINMINDTRADE_API_KEY=your_key_here" > .env
   ```

2. 註冊 API key: https://finmindtrade.com/analysis/#/membership/register

### 問題：前端無法連接到後端

**解決方案：**
1. 檢查 DevTools Console 是否有錯誤
2. 確保重新編譯了前端：
   ```bash
   cd frontend
   rm -rf dist-electron
   pnpm run dev
   ```

3. 檢查 Python 進程是否正在運行：
   ```bash
   ps aux | grep ipc_server.py
   ```

## 支援的功能

### ✅ 已實現
- [x] 查詢即時匯率（8 種貨幣）
- [x] 計算換匯金額
- [x] 顯示銀行買入/賣出價
- [x] 檢查換匯限額警告
- [x] 查詢銀行規則
- [x] 美觀的 UI 界面

### 📊 支援的貨幣
- USD 美金 ($)
- EUR 歐元 (€)
- JPY 日圓 (¥)
- CNY 人民幣 (¥)
- GBP 英鎊 (£)
- AUD 澳洲 (A$)
- HKD 港幣 (HK$)
- SGD 新加坡 (S$)

## 技術架構

```
Frontend (Electron + React)
    ↕ IPC Communication
Backend (Python)
    ↕ HTTP API
FinMind API (台灣銀行匯率資料)
```

## 開發提示

### 查看即時日誌

**Electron 主進程日誌：**
- 在終端 2 可以看到 Python 的 stderr 輸出

**渲染進程日誌：**
- 打開 DevTools Console (Cmd+Option+I on Mac)

**Python 進程日誌：**
- 檢查 Python stderr 輸出
- 添加 `print()` 語句到 Python 代碼

### 熱重載

**前端代碼：**
- React 組件會自動熱重載
- TypeScript 檔案會自動編譯

**後端代碼：**
- 修改 Python 代碼後需要重啟 Electron
- 或者手動重啟 Python 進程

## 常用命令

```bash
# 測試後端
python3 test_backend.py

# 重新安裝依賴
cd backend && pip install -r requirements.txt
cd frontend && pnpm install

# 清理並重建
cd frontend
rm -rf node_modules dist dist-electron
pnpm install
pnpm run build

# 查看 Python 進程
ps aux | grep ipc_server.py

# 殺死殘留的 Python 進程
pkill -f ipc_server.py
```

## 下一步

一切正常後，你可以：
1. 測試不同貨幣的匯率查詢
2. 嘗試不同金額的換匯計算
3. 查看超過限額時的警告訊息
4. 自定義銀行規則（修改 backend/agent/agent.py）

## 需要幫助？

如果遇到問題：
1. 先運行 `python3 test_backend.py` 確認後端正常
2. 檢查 Electron DevTools Console
3. 查看 Python stderr 輸出
4. 確認網路連接正常

祝使用愉快！🎉
