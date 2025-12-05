# Backend - Python 後端

智慧商用計算機的後端服務，提供計算引擎、AI Agent 和 API 服務。

## 目錄結構

```
backend/
├── README.md               # 本文件
├── requirements.txt        # Python 依賴
├── .env.example           # 環境變數範本
├── main.py                # FastAPI 入口 (開發/測試用)
├── ipc_server.py          # IPC 伺服器 (生產用，與 Electron 通訊)
├── core/                  # 核心計算模組
│   ├── __init__.py
│   ├── engine.py          # 計算機引擎 (四則運算)
│   ├── units.py           # 單位轉換模組
│   └── commercial.py      # 商業計算 (折扣、稅金)
├── agent/                 # AI Agent 模組
│   ├── __init__.py
│   ├── tools.py           # Agent 可呼叫的工具定義
│   ├── llm_client.py      # Anthropic API 整合
│   └── parser.py          # 自然語言解析 (可選)
├── api/                   # API 路由 (FastAPI)
│   ├── __init__.py
│   └── routes.py
└── tests/                 # 測試
    ├── test_engine.py
    ├── test_units.py
    └── test_commercial.py
```

## 安裝

```bash
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows

# 安裝依賴
pip install -r requirements.txt
```

## 環境變數設定

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

```env
# Anthropic API Key (必要)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# 開發模式 (可選)
DEBUG=true

# API Port (僅 FastAPI 開發模式使用)
PORT=8000
```

## 執行方式

### 方式一：FastAPI 開發伺服器（開發/測試用）

```bash
# 啟動開發伺服器
python -m uvicorn main:app --reload --port 8000

# 或直接執行
python main.py
```

API 文件：http://localhost:8000/docs

### 方式二：IPC 模式（生產用，與 Electron 整合）

```bash
# 直接執行（由 Electron spawn）
python ipc_server.py
```

IPC 模式不開放網路連線，僅透過 stdin/stdout 與 Electron 通訊。

## 模組說明

### Core - 核心計算

#### engine.py - 計算機引擎

```python
from core.engine import CalculatorEngine

engine = CalculatorEngine()
engine.press_digit("5")
engine.press_operator("+")
engine.press_digit("3")
engine.press_equals()
print(engine.display)  # "8"
```

#### units.py - 單位轉換

```python
from decimal import Decimal
from core.units import UnitConverter

converter = UnitConverter()

# 公頃 → 畝
result = converter.convert(Decimal("1"), "公頃", "畝")
print(result)  # 15.0000

# 坪 → 平方公尺
result = converter.convert(Decimal("30"), "坪", "平方公尺")
print(result)  # 99.1737
```

**支援的面積單位：**

| 單位 | 說明 | 換算 (平方公尺) |
|------|------|-----------------|
| 平方公尺, m² | 基礎單位 | 1 |
| 公頃 | 公制 | 10,000 |
| 平方公里, km² | 公制 | 1,000,000 |
| 甲 | 台灣傳統 | 9,699.17 |
| 分 | 台灣傳統 (0.1甲) | 969.917 |
| 畝 | 中國傳統 | 666.67 |
| 坪 | 台灣/日本 | 3.30579 |

#### commercial.py - 商業計算

```python
from decimal import Decimal
from core.commercial import CommercialCalculator

calc = CommercialCalculator()

# $200 打 75 折，加 5% 稅
result = calc.calculate_price(
    Decimal("200"),
    discount_percent=75,  # 75折 = 付 75%
    tax_percent=5         # 5% 稅
)

print(result.to_dict())
# {
#     "original_price": "200",
#     "discount_rate": "75.0%",
#     "discounted_price": "150.00",
#     "tax_rate": "5.0%",
#     "tax_amount": "7.50",
#     "final_price": "157.50"
# }
```

### Agent - AI 智慧代理

#### tools.py - 工具定義

定義 LLM 可呼叫的函數（Function Calling）：

| 工具名稱 | 功能 |
|----------|------|
| `calculate_basic` | 基本數學運算 |
| `convert_unit` | 單位轉換 |
| `calculate_price` | 價格計算（折扣+稅金）|
| `calculate_land_value` | 土地價值計算 |

#### llm_client.py - LLM 整合

```python
from agent.llm_client import SmartCalculatorAgent
from agent.tools import AgentToolkit

toolkit = AgentToolkit(engine, units, commercial)
agent = SmartCalculatorAgent(toolkit)

# 自然語言查詢
response = agent.process_query("$200的商品打75折加上5%的稅是多少？")
print(response)
# "200元商品打75折後為150元，加上5%稅金(7.50元)，最終價格為 $157.50"
```

## API 端點（FastAPI 模式）

| Method | Endpoint | 說明 |
|--------|----------|------|
| POST | `/api/calc/action` | 計算機操作 |
| GET | `/api/calc/display` | 取得顯示內容 |
| POST | `/api/agent/query` | AI Agent 查詢 |
| WebSocket | `/ws/agent` | 即時 AI 對話 |

### 範例請求

```bash
# 計算機操作
curl -X POST http://localhost:8000/api/calc/action \
  -H "Content-Type: application/json" \
  -d '{"action": "digit", "value": "5"}'

# AI Agent 查詢
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "$200的商品打75折加上5%的稅"}'
```

## IPC 協議（Electron 整合模式）

### 請求格式

```json
{
    "action": "agent",
    "query": "$200的商品打75折加上5%的稅"
}
```

### 回應格式

```json
{
    "success": true,
    "response": "最終價格為 $157.50"
}
```

### 支援的 Action

| Action | 說明 | 參數 |
|--------|------|------|
| `calc_digit` | 輸入數字 | `value`: "0"-"9", "." |
| `calc_operator` | 輸入運算子 | `operator`: "+", "-", "*", "/" |
| `calc_equals` | 計算結果 | - |
| `calc_clear` | 清除 | - |
| `agent` | AI 查詢 | `query`: 自然語言字串 |

## 測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/test_units.py -v

# 測試覆蓋率
pytest --cov=core --cov=agent
```

## 打包

使用 PyInstaller 打包成獨立執行檔：

```bash
pip install pyinstaller

# 打包 IPC 伺服器
pyinstaller --onefile ipc_server.py \
    --name calculator-backend \
    --hidden-import=anthropic

# 產出位置
# - Linux/macOS: dist/calculator-backend
# - Windows: dist/calculator-backend.exe
```

### 打包注意事項

1. **Hidden Imports**：某些套件需要手動指定
   ```bash
   --hidden-import=anthropic
   --hidden-import=uvicorn
   ```

2. **資料檔案**：如有額外資料檔
   ```bash
   --add-data="data/:data/"
   ```

3. **檔案大小**：打包後約 50-100 MB（含 Python 解譯器）

## 開發注意事項

### ⚠️ 重要

1. **Decimal 精度**
   ```python
   # ✅ 正確
   Decimal("0.1")
   
   # ❌ 錯誤 - 浮點數精度問題
   Decimal(0.1)
   ```

2. **API Key 安全**
   ```python
   # ✅ 從環境變數讀取
   api_key = os.getenv("ANTHROPIC_API_KEY")
   
   # ❌ 絕對不要寫死
   api_key = "sk-ant-xxxxx"
   ```

3. **IPC 編碼**
   ```python
   # 確保 JSON 正確處理中文
   json.dumps(data, ensure_ascii=False)
   ```

4. **例外處理**
   ```python
   # IPC 模式必須捕捉所有例外，避免程序崩潰
   try:
       result = process_request(data)
   except Exception as e:
       result = {"error": str(e)}
   ```

### 程式碼風格

- 遵循 PEP 8
- 使用 Type Hints
- 使用 Black 格式化
- 使用 isort 排序 imports

```bash
# 格式化
black .
isort .

# 檢查
flake8 .
mypy .
```

## 依賴說明

| 套件 | 用途 |
|------|------|
| fastapi | Web 框架（開發模式）|
| uvicorn | ASGI 伺服器 |
| anthropic | Claude API SDK |
| python-dotenv | 環境變數管理 |
| pydantic | 資料驗證 |

## Troubleshooting

<details>
<summary>ImportError: No module named 'anthropic'</summary>

```bash
pip install anthropic
```
</details>

<details>
<summary>Decimal 計算結果有很多小數位</summary>

使用 `quantize` 控制精度：
```python
result = (Decimal("100") / Decimal("3")).quantize(Decimal("0.01"))
```
</details>

<details>
<summary>IPC 沒有回應</summary>

確認 stdout 有 flush：
```python
print(json.dumps(response), flush=True)
```
</details>