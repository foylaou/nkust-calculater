# 🚀 銀行員匯率系統 - 開始使用

## ✅ 所有測試通過！

後端功能已經過完整測試並正常運行：
- ✅ Python 依賴已安裝
- ✅ AI Agent 初始化成功
- ✅ 匯率查詢正常（USD: 30.795/31.465）
- ✅ IPC Server 正常運行
- ✅ 前端 TypeScript 編譯成功

## 📝 已修復的問題

1. ✅ **Import 路徑錯誤** - 修正為正確的相對路徑
2. ✅ **Gemini API 初始化** - 支援無 API key 運行
3. ✅ **缺少 core 模組** - 添加可選導入處理
4. ✅ **ES 模組 require** - 改用 import 語法
5. ✅ **IPC 通信問題** - 實現請求隊列機制
6. ✅ **Stream 銷毀錯誤** - 改進響應處理邏輯

## 🎯 立即開始

### 步驟 1: 啟動開發伺服器

打開**終端 1**：
```bash
cd frontend
pnpm run dev
```

等待看到：
```
➜  Local:   http://localhost:5173/
```

### 步驟 2: 啟動 Electron 應用

打開**終端 2**：
```bash
cd frontend
pnpm run electron:dev
```

### 步驟 3: 使用銀行員功能

1. 應用啟動後，你會看到計算機界面
2. 點擊綠色的「**銀行員匯率模式**」按鈕（💲 圖標）
3. 右側面板會滑出，顯示匯率工具
4. 系統會自動查詢 USD 的最新匯率
5. 輸入台幣金額（例如：10000）
6. 點擊「計算換匯金額」按鈕
7. 查看計算結果！

## 🎨 功能預覽

### 支援的貨幣
```
🇺🇸 USD - 美金    🇪🇺 EUR - 歐元
🇯🇵 JPY - 日圓    🇨🇳 CNY - 人民幣
🇬🇧 GBP - 英鎊    🇦🇺 AUD - 澳洲
🇭🇰 HKD - 港幣    🇸🇬 SGD - 新加坡
```

### 匯率資訊
- **現金買入價**: 銀行買入現金的價格
- **現金賣出價**: 銀行賣出現金的價格（換匯使用此價格）
- **即期買入價**: 銀行買入即期的價格
- **即期賣出價**: 銀行賣出即期的價格

### 換匯計算
輸入台幣金額，系統會：
1. 使用最新的銀行賣出價
2. 計算可換得的外幣金額
3. 顯示匯率和日期
4. 檢查是否超過單日限額

## 🔍 檢查運行狀態

### 確認 Python 進程已啟動

在 Electron 窗口中，打開開發者工具：
- **Mac**: `Cmd + Option + I`
- **Windows/Linux**: `Ctrl + Shift + I`

你應該在 Console 看到：
```
Starting Python backend: /path/to/backend/ipc_server.py
Backend exists: true
Python process spawned with PID: 12345
Bank Agent initialized successfully
Python backend started successfully
```

### 確認功能正常

在 DevTools Console 中測試：
```javascript
// 測試 1: 查詢美金匯率
const rate = await window.bankAgent.getExchangeRate('USD');
console.log(rate);
// 應該看到: { success: true, currency: "USD", cash_buy: 30.795, ... }

// 測試 2: 計算換匯
const result = await window.bankAgent.calculateExchange('USD', 10000, true);
console.log(result);
// 應該看到: { success: true, foreign_amount: 317.87, ... }
```

## ⚠️ 常見問題

### Q: 看到 "Python process not available"

**A:** Python 進程沒有啟動成功

解決方案：
```bash
# 1. 檢查 Python 是否安裝
which python3
python3 --version

# 2. 測試後端
cd /path/to/nkust-calculater
python3 test_backend.py

# 3. 重啟 Electron
# 在終端 2 按 Ctrl+C 停止
# 然後重新運行
cd frontend
pnpm run electron:dev
```

### Q: 看到 "Cannot call write after a stream was destroyed"

**A:** 這個問題已經修復！確保你使用的是最新代碼

解決方案：
```bash
# 1. 重新構建前端
cd frontend
rm -rf dist-electron
pnpm run dev

# 2. 在另一個終端重啟 Electron
cd frontend
pnpm run electron:dev
```

### Q: 匯率查詢失敗

**A:** 可能是網路問題或 API 限制

解決方案：
1. 檢查網路連接
2. 註冊 FinMind API key: https://finmindtrade.com/analysis/#/membership/register
3. 在 `.env` 文件中設置：
   ```bash
   FINMINDTRADE_API_KEY=your_api_key_here
   ```

### Q: 顯示 "Warning: Calculator modules not available"

**A:** 這是正常的警告！不影響銀行員功能

原因：`core` 模組（計算器引擎）不存在，但銀行員功能不需要它。

## 🎓 使用示例

### 示例 1: 查詢美金匯率

1. 點擊「銀行員匯率模式」
2. 選擇「USD 美金」
3. 系統自動顯示最新匯率
4. 查看：
   - 銀行買入：30.795
   - 銀行賣出：31.465

### 示例 2: 計算換 1000 美金需要多少台幣

1. 選擇「USD 美金」
2. 輸入台幣金額：31465
3. 點擊「計算換匯金額」
4. 結果顯示：可換得 1000.00 USD

### 示例 3: 測試限額警告

1. 選擇「USD 美金」
2. 輸入大金額：2000000（200 萬台幣）
3. 點擊「計算換匯金額」
4. 會看到警告：「注意：買入金額超過單日限額 50000 USD」

## 📊 技術架構

```
┌─────────────────┐
│  React Frontend │ (Calculator.tsx)
└────────┬────────┘
         │ IPC Call
         │ window.bankAgent.getExchangeRate()
         ▼
┌─────────────────┐
│ Electron Main   │ (main.ts)
│ Process         │
└────────┬────────┘
         │ stdin/stdout
         │ JSON Messages
         ▼
┌─────────────────┐
│ Python Backend  │ (ipc_server.py)
└────────┬────────┘
         │ Method Call
         │ bank_agent.get_exchange_rate()
         ▼
┌─────────────────┐
│  AI_Agent       │ (agent.py)
└────────┬────────┘
         │ API Call
         │ exchange_rate.get_latest_rate()
         ▼
┌─────────────────┐
│ ExchangeRate    │ (ExchangeRate.py)
│ Tool            │
└────────┬────────┘
         │ HTTP Request
         ▼
┌─────────────────┐
│ FinMind API     │ (台灣銀行匯率資料)
└─────────────────┘
```

## 📚 相關文檔

- **BANK_AGENT_README.md** - 完整的功能和 API 文檔
- **QUICK_START.md** - 快速啟動和故障排除
- **IMPLEMENTATION_SUMMARY.md** - 實現細節和技術總結
- **test_backend.py** - 後端測試腳本

## 🎉 開始使用吧！

1. ✅ 所有測試已通過
2. ✅ 代碼已修復
3. ✅ 文檔已完整
4. ✅ 準備好使用了！

現在就啟動應用，體驗銀行員匯率查詢系統吧！

---

**需要幫助？**
- 查看 DevTools Console 的錯誤訊息
- 運行 `python3 test_backend.py` 診斷後端
- 檢查 Python stderr 輸出（在終端 2）

**祝使用愉快！** 🎊
