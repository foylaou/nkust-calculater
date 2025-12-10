# 台灣銀行匯率查詢工具

## 功能說明

這是一個封裝好的台灣銀行匯率爬蟲工具，使用 FinMind API 查詢台灣銀行的外匯匯率資料。

## 支援的幣別

| 代碼 | 幣別 | 代碼 | 幣別 | 代碼 | 幣別 |
|------|------|------|------|------|------|
| USD | 美金 | EUR | 歐元 | JPY | 日圓 |
| CNY | 人民幣 | GBP | 英鎊 | AUD | 澳洲 |
| CAD | 加拿大 | CHF | 瑞士法郎 | HKD | 港幣 |
| SGD | 新加坡幣 | KRW | 韓元 | THB | 泰幣 |
| SEK | 瑞典幣 | NZD | 紐元 | MYR | 馬來幣 |
| IDR | 印尼幣 | PHP | 菲國比索 | VND | 越南盾 |
| ZAR | 南非幣 | | | | |

## 回傳資料格式

```
    date       currency  cash_buy  cash_sell  spot_buy  spot_sell
0   2024-01-02   USD      32.470    33.005    32.595    32.695
1   2024-01-03   USD      32.295    32.830    32.595    32.695
```

欄位說明：
- `date`: 日期
- `currency`: 貨幣代碼
- `cash_buy`: 現金買入價（銀行買入現金的價格）
- `cash_sell`: 現金賣出價（銀行賣出現金的價格）
- `spot_buy`: 即期買入價（銀行買入即期的價格）
- `spot_sell`: 即期賣出價（銀行賣出即期的價格）

## 使用方式

### 1. 使用環境變數（推薦）

建議將 API token 設定在 `.env` 檔案中：

```bash
# .env 檔案
API_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

```python
from tool.ExchangeRate import TaiwanExchangeRate

# 自動從環境變數讀取 token
exchanger = TaiwanExchangeRate()

# 查詢特定日期範圍的匯率
df = exchanger.fetch_data("USD", "2024-01-01", "2024-01-10")
print(df.head())
```

### 2. 直接傳入 Token

```python
from tool.ExchangeRate import TaiwanExchangeRate

# 直接傳入 token
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
exchanger = TaiwanExchangeRate(token=token)

# 查詢匯率
df = exchanger.fetch_data("USD", "2024-01-01", "2024-01-10")
```

### 3. 取得 API Token

註冊網址: https://finmindtrade.com/analysis/#/membership/register

登入後在個人頁面取得 API token，格式為 JWT token。

### 4. 取得最新匯率

```python
exchanger = TaiwanExchangeRate()

# 取得美金最新匯率
latest = exchanger.get_latest_rate("USD")

if latest:
    print(f"日期: {latest['date']}")
    print(f"貨幣: {latest['currency']}")
    print(f"現金買入: {latest['cash_buy']}")
    print(f"現金賣出: {latest['cash_sell']}")
    print(f"即期買入: {latest['spot_buy']}")
    print(f"即期賣出: {latest['spot_sell']}")
```

### 5. 取得歷史匯率

```python
exchanger = TaiwanExchangeRate()

# 取得過去 30 天的美金匯率
df = exchanger.get_historical_rates("USD", days=30)
print(df.head())
```

### 6. 同時查詢多種貨幣

```python
exchanger = TaiwanExchangeRate()

# 查詢美金、歐元、日圓的匯率
rates = exchanger.get_multiple_currencies(
    ["USD", "EUR", "JPY"],
    "2024-01-01",
    "2024-01-10"
)

for currency, df in rates.items():
    print(f"\n{currency}:")
    print(df.head())
```

## 方法說明

### `__init__(token: Optional[str] = None)`
初始化匯率查詢工具
- `token`: FinMind API token（可選）

### `fetch_data(currency: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame`
查詢台灣銀行匯率資料
- `currency`: 貨幣代碼（如: USD, EUR, JPY）
- `start_date`: 開始日期（格式: YYYY-MM-DD），預設為今天
- `end_date`: 結束日期（格式: YYYY-MM-DD），預設為今天
- 回傳: pandas DataFrame

### `get_latest_rate(currency: str) -> Optional[dict]`
取得指定貨幣的最新匯率
- `currency`: 貨幣代碼
- 回傳: 字典格式的匯率資料，若無資料則回傳 None

### `get_historical_rates(currency: str, days: int = 30) -> pd.DataFrame`
取得指定貨幣的歷史匯率資料
- `currency`: 貨幣代碼
- `days`: 往前追溯的天數，預設為 30 天
- 回傳: pandas DataFrame

### `get_multiple_currencies(currencies: list, start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict`
同時查詢多種貨幣的匯率
- `currencies`: 貨幣代碼列表
- `start_date`: 開始日期
- `end_date`: 結束日期
- 回傳: 以貨幣代碼為 key，DataFrame 為 value 的字典

## 錯誤處理

程式包含完整的錯誤處理機制：
- 網路請求失敗時會返回空的 DataFrame
- API 錯誤時會顯示提示訊息
- 無資料時會返回包含正確欄位的空 DataFrame

## API 版本說明

本工具使用 **FinMind API v4**，token 透過 HTTP Header 的 `Authorization: Bearer {token}` 方式傳遞。

## 注意事項

1. **必須使用 API token** 才能正常查詢資料
2. Token 可透過參數傳入或設定在環境變數 `API_KEY` 中
3. 建議使用 `.env` 檔案管理 token，避免將 token 直接寫在程式碼中
4. 匯率資料可能有延遲，非即時更新
5. 日期格式必須為 YYYY-MM-DD
6. API 提供台灣銀行的官方匯率資料

## 測試結果範例

```
==================================================
測試 1: 取得 USD 指定日期範圍的匯率
==================================================
         date currency  cash_buy  cash_sell  spot_buy  spot_sell
0  2024-01-02      USD    30.465     31.135    30.815     30.915
1  2024-01-03      USD    30.610     31.280    30.960     31.060
2  2024-01-04      USD    30.595     31.265    30.945     31.045
3  2024-01-05      USD    30.610     31.280    30.960     31.060
4  2024-01-08      USD    30.595     31.265    30.945     31.045
```
