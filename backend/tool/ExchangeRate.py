from datetime import datetime, timedelta
from typing import Optional
import requests
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()


class TaiwanExchangeRate:
    """
    台灣銀行匯率查詢工具

    使用 FinMind API 查詢台灣銀行的外匯匯率資料
    資料來源: https://api.finmindtrade.com

    支援的幣別:
    AUD: 澳洲    CAD: 加拿大    CHF: 瑞士法郎    CNY: 人民幣
    EUR: 歐元    GBP: 英鎊      HKD: 港幣        IDR: 印尼幣
    JPY: 日圓    KRW: 韓元      MYR: 馬來幣      NZD: 紐元
    PHP: 菲國比索 SEK: 瑞典幣    SGD: 新加坡幣    THB: 泰幣
    USD: 美金    VND: 越南盾    ZAR: 南非幣
    """

    SUPPORTED_CURRENCIES = {
        'AUD': '澳洲', 'CAD': '加拿大', 'CHF': '瑞士法郎', 'CNY': '人民幣',
        'EUR': '歐元', 'GBP': '英鎊', 'HKD': '港幣', 'IDR': '印尼幣',
        'JPY': '日圓', 'KRW': '韓元', 'MYR': '馬來幣', 'NZD': '紐元',
        'PHP': '菲國比索', 'SEK': '瑞典幣', 'SGD': '新加坡幣', 'THB': '泰幣',
        'USD': '美金', 'VND': '越南盾', 'ZAR': '南非幣'
    }

    def __init__(self, token: Optional[str] = None):
        """
        初始化匯率查詢工具

        Args:
            token: FinMind API token (可選)，若無 token 則從環境變數 API_KEY 讀取
                   註冊 token: https://finmindtrade.com/analysis/#/membership/register
        """
        self.url = "https://api.finmindtrade.com/api/v4/data"
        self.dataset = "TaiwanExchangeRate"
        self.token = token or os.environ.get("FINMINDTRADE_API_KEY")

    def get_now(self) -> datetime:
        """取得目前時間"""
        return datetime.now()

    def fetch_data(self, currency: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        查詢台灣銀行匯率資料

        Args:
            currency: 貨幣代碼 (如: USD, EUR, JPY, CNY, GBP, AUD, HKD, SGD, CHF, ZAR, SEK, NZD, THB, PHP, IDR, KRW, MYR, VND, CAD)
            start_date: 開始日期 (格式: YYYY-MM-DD)，預設為今天
            end_date: 結束日期 (格式: YYYY-MM-DD)，預設為今天

        Returns:
            pd.DataFrame: 包含以下欄位的 DataFrame
                - date: 日期
                - currency: 貨幣代碼
                - cash_buy: 現金買入價
                - cash_sell: 現金賣出價
                - spot_buy: 即期買入價
                - spot_sell: 即期賣出價

        Example:
            >>> exchanger = TaiwanExchangeRate()
            >>> df = exchanger.fetch_data("USD", "2024-01-01", "2024-01-07")
            >>> print(df.head())
        """
        if not start_date:
            start_date = self.get_now().strftime("%Y-%m-%d")

        if not end_date:
            end_date = self.get_now().strftime("%Y-%m-%d")

        parameter = {
            "dataset": self.dataset,
            "data_id": currency.upper(),
            "start_date": start_date,
            "end_date": end_date
        }

        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            response = requests.get(self.url, params=parameter, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if 'data' not in data or not data['data']:
                print(f"查無 {currency} 的匯率資料")
                return pd.DataFrame(columns=['date', 'currency', 'cash_buy', 'cash_sell', 'spot_buy', 'spot_sell'])

            df = pd.DataFrame(data['data'])

            numeric_columns = ['cash_buy', 'cash_sell', 'spot_buy', 'spot_sell']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            return df

        except requests.exceptions.RequestException as e:
            print(f"請求失敗: {e}")
            print("提示: 若遇到 400 錯誤，可能需要 FinMind API token")
            print("註冊網址: https://finmindtrade.com/analysis/#/membership/register")
            return pd.DataFrame(columns=['date', 'currency', 'cash_buy', 'cash_sell', 'spot_buy', 'spot_sell'])
        except Exception as e:
            print(f"處理資料時發生錯誤: {e}")
            return pd.DataFrame(columns=['date', 'currency', 'cash_buy', 'cash_sell', 'spot_buy', 'spot_sell'])

    def get_latest_rate(self, currency: str) -> Optional[dict]:
        """
        取得指定貨幣的最新匯率

        Args:
            currency: 貨幣代碼 (如: USD, EUR, JPY)

        Returns:
            dict: 最新的匯率資料，包含 date, currency, cash_buy, cash_sell, spot_buy, spot_sell
                  如果沒有資料則返回 None

        Example:
            >>> exchanger = TaiwanExchangeRate()
            >>> rate = exchanger.get_latest_rate("USD")
            >>> if rate:
            ...     print(f"美元現金買入價: {rate['cash_buy']}")
        """
        # 查詢最近7天的數據以確保能獲取到最新資料（API可能有延遲）
        end_date = self.get_now()
        start_date = end_date - timedelta(days=7)

        df = self.fetch_data(
            currency,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )

        if df.empty:
            return None

        # 返回最新的一筆資料
        latest = df.iloc[-1].to_dict()
        return latest

    def get_historical_rates(self, currency: str, days: int = 30) -> pd.DataFrame:
        """
        取得指定貨幣的歷史匯率資料

        Args:
            currency: 貨幣代碼 (如: USD, EUR, JPY)
            days: 往前追溯的天數，預設為 30 天

        Returns:
            pd.DataFrame: 歷史匯率資料

        Example:
            >>> exchanger = TaiwanExchangeRate()
            >>> df = exchanger.get_historical_rates("USD", days=7)
            >>> print(df)
        """
        end_date = self.get_now()
        start_date = end_date - timedelta(days=days)

        return self.fetch_data(
            currency,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )

    def get_multiple_currencies(self, currencies: list, start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
        """
        同時查詢多種貨幣的匯率

        Args:
            currencies: 貨幣代碼列表 (如: ["USD", "EUR", "JPY"])
            start_date: 開始日期 (格式: YYYY-MM-DD)
            end_date: 結束日期 (格式: YYYY-MM-DD)

        Returns:
            dict: 以貨幣代碼為 key，DataFrame 為 value 的字典

        Example:
            >>> exchanger = TaiwanExchangeRate()
            >>> rates = exchanger.get_multiple_currencies(["USD", "EUR", "JPY"])
            >>> print(rates["USD"].head())
        """
        result = {}
        for currency in currencies:
            df = self.fetch_data(currency, start_date, end_date)
            if not df.empty:
                result[currency] = df
        return result


if __name__ == "__main__":
    exchanger = TaiwanExchangeRate()
    print(exchanger.token)
    print("=" * 50)
    print("測試 1: 取得 USD 指定日期範圍的匯率")
    print("=" * 50)
    df = exchanger.fetch_data("USD", "2024-01-01", "2024-01-10")
    print(df.head())

    print("\n" + "=" * 50)
    print("測試 2: 取得 USD 過去 30 天的匯率")
    print("=" * 50)
    historical = exchanger.get_historical_rates("USD", days=30)
    print(f"資料筆數: {len(historical)}")
    if not historical.empty:
        print(historical.head())
        print("\n最新資料:")
        latest = historical.iloc[-1]
        print(f"日期: {latest['date']}")
        print(f"貨幣: {latest['currency']}")
        print(f"現金買入: {latest['cash_buy']}")
        print(f"現金賣出: {latest['cash_sell']}")
        print(f"即期買入: {latest['spot_buy']}")
        print(f"即期賣出: {latest['spot_sell']}")

    print("\n" + "=" * 50)
    print("測試 3: 同時查詢多種貨幣 (USD, EUR, JPY)")
    print("=" * 50)
    multiple = exchanger.get_multiple_currencies(["USD", "EUR", "JPY"], "2024-01-01", "2024-01-05")
    for currency, df in multiple.items():
        print(f"\n{currency} ({TaiwanExchangeRate.SUPPORTED_CURRENCIES.get(currency, currency)}):")
        print(df.tail(3))
