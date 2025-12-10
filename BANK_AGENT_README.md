# 銀行員匯率查詢系統

## 功能概述

這個系統實現了一個完整的銀行員角色 AI Agent，提供即時匯率查詢和換匯計算功能。

## 架構說明

### Backend (Python)

1. **backend/agent/agent.py**
   - 實現了 `AI_Agent` 類，扮演銀行員角色
   - 調用 `ExchangeRate.py` 工具獲取台灣銀行匯率
   - 提供以下功能：
     - `get_exchange_rate()`: 查詢指定貨幣匯率
     - `calculate_exchange()`: 計算換匯金額
     - `get_multiple_rates()`: 查詢多種貨幣匯率
     - `get_bank_rules()`: 獲取銀行換匯規則
     - `roles()`: 獲取銀行員角色資訊

2. **backend/ipc_server.py**
   - 添加了以下 IPC action 處理器：
     - `exchange_rate`: 查詢匯率
     - `calculate_exchange`: 計算換匯
     - `get_multiple_rates`: 多幣別查詢
     - `get_bank_rules`: 查詢規則
     - `bank_agent_info`: 獲取 agent 資訊

### Frontend (Electron + React)

1. **frontend/electron/main.ts**
   - 實現 Python 後端進程管理
   - 啟動 Python IPC server
   - 處理前端與 Python 的通信
   - 添加了 5 個 IPC handlers

2. **frontend/electron/preload.ts**
   - 暴露 `window.bankAgent` API 給渲染進程
   - 提供 5 個方法供前端調用

3. **frontend/src/components/Calculator.tsx**
   - 新增銀行員匯率模式
   - 提供匯率查詢界面
   - 實時顯示匯率資訊
   - 計算換匯金額

4. **frontend/src/types/electron.d.ts**
   - TypeScript 類型定義
   - 確保類型安全

## 支援的貨幣

- USD: 美金 ($)
- EUR: 歐元 (€)
- JPY: 日圓 (¥)
- CNY: 人民幣 (¥)
- GBP: 英鎊 (£)
- AUD: 澳洲 (A$)
- HKD: 港幣 (HK$)
- SGD: 新加坡 (S$)

## 銀行規則

每種貨幣都有單日換匯限額：
- USD: 50,000
- EUR: 30,000
- JPY: 5,000,000
- CNY: 200,000
- GBP: 20,000
- AUD: 30,000
- HKD: 200,000
- SGD: 30,000

## 使用方法

### 1. 環境設置

確保你的 `.env` 文件包含 FinMind API 金鑰：

```bash
FINMINDTRADE_API_KEY=your_api_key_here
```

註冊 API token: https://finmindtrade.com/analysis/#/membership/register

### 2. 安裝依賴

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
pnpm install
```

### 3. 啟動應用

開發模式：

```bash
# Terminal 1 - 啟動 Vite dev server
cd frontend
pnpm run dev

# Terminal 2 - 啟動 Electron
cd frontend
pnpm run electron:dev
```

生產模式：

```bash
cd frontend
pnpm run build
pnpm run electron:start
```

### 4. 使用銀行員模式

1. 打開應用後，點擊「銀行員匯率模式」按鈕
2. 右側面板會展開，顯示匯率查詢工具
3. 選擇要查詢的貨幣
4. 系統會自動獲取最新匯率
5. 輸入台幣金額
6. 點擊「計算換匯金額」按鈕
7. 查看計算結果和警告信息

## API 使用示例

### 在 React 組件中使用

```typescript
// 查詢美金匯率
const rate = await window.bankAgent.getExchangeRate('USD', 'cash_sell');
console.log(rate);

// 計算換匯 (用 10000 台幣買美金)
const result = await window.bankAgent.calculateExchange('USD', 10000, true);
console.log(result);

// 查詢多種貨幣
const rates = await window.bankAgent.getMultipleRates(['USD', 'EUR', 'JPY']);
console.log(rates);

// 查詢銀行規則
const rules = await window.bankAgent.getBankRules('USD');
console.log(rules);

// 獲取 Agent 資訊
const info = await window.bankAgent.getAgentInfo();
console.log(info);
```

## 注意事項

1. **API 金鑰**: 必須設置 `FINMINDTRADE_API_KEY` 環境變數
2. **Python 版本**: 需要 Python 3.7+
3. **網路連接**: 需要網路連接來查詢匯率資料
4. **匯率延遲**: 匯率資料可能有延遲，非即時更新
5. **限額警告**: 超過單日限額會顯示警告，但不會阻止計算

## 故障排除

### Python 進程無法啟動

檢查 Python 路徑：
```bash
which python3
```

確保 `backend/ipc_server.py` 有執行權限：
```bash
chmod +x backend/ipc_server.py
```

### 匯率查詢失敗

1. 檢查 API 金鑰是否正確
2. 檢查網路連接
3. 查看 Electron DevTools Console 的錯誤信息

### TypeScript 類型錯誤

確保 `tsconfig.json` 包含類型定義：
```json
{
  "include": ["src/**/*", "src/types/**/*"]
}
```

## 開發建議

1. 使用 Electron DevTools 查看前端日誌
2. 查看終端輸出的 Python stderr 信息
3. 使用 `console.log` 調試 IPC 通信
4. 測試各種貨幣和金額組合

## 未來改進

- [ ] 添加歷史匯率圖表
- [ ] 支援更多貨幣
- [ ] 添加匯率走勢預測
- [ ] 實現離線模式
- [ ] 添加匯率提醒功能

## 技術棧

- **Backend**: Python 3, FinMind API, pandas
- **Frontend**: React, TypeScript, Tailwind CSS
- **Desktop**: Electron
- **IPC**: stdin/stdout JSON communication
- **Icons**: Lucide React

## 授權

MIT License
