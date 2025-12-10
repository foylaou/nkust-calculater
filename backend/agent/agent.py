from dotenv import load_dotenv
import os
from google import genai
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tool.ExchangeRate import TaiwanExchangeRate


class AI_Agent:
    load_dotenv()

    def __init__(self, api_key=None, api_secret=None):
        """
        初始化 AI Agent - 銀行員角色

        Args:
            api_key: Gemini API key (可選，會從環境變數讀取)
            api_secret: API secret (可選)
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.ai_type = "gemini"

        # 初始化 Gemini 客戶端 (僅在有 API key 時初始化)
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client: {e}")
                self.client = None
        else:
            # 沒有 API key 時不初始化 AI client (匯率功能不需要)
            self.client = None

        # 初始化匯率查詢工具
        self.exchange_rate = TaiwanExchangeRate()

        # 銀行員角色設定
        self.role = "銀行員"
        self.bank_rules = {
            "USD": {"max_amount": 50000, "name": "美金"},
            "EUR": {"max_amount": 30000, "name": "歐元"},
            "JPY": {"max_amount": 5000000, "name": "日圓"},
            "CNY": {"max_amount": 200000, "name": "人民幣"},
            "GBP": {"max_amount": 20000, "name": "英鎊"},
            "AUD": {"max_amount": 30000, "name": "澳洲"},
            "HKD": {"max_amount": 200000, "name": "港幣"},
            "SGD": {"max_amount": 30000, "name": "新加坡"},
        }

    def get_exchange_rate(self, currency: str, rate_type: str = "cash_sell"):
        """
        取得指定貨幣的匯率

        Args:
            currency: 貨幣代碼 (如: USD, EUR, JPY)
            rate_type: 匯率類型 (cash_buy, cash_sell, spot_buy, spot_sell)

        Returns:
            dict: 包含匯率資訊的字典
        """
        try:
            rate = self.exchange_rate.get_latest_rate(currency)

            if not rate:
                return {
                    "success": False,
                    "error": f"無法取得 {currency} 的匯率資訊",
                    "currency": currency
                }

            return {
                "success": True,
                "currency": currency,
                "date": rate.get("date"),
                "cash_buy": float(rate.get("cash_buy", 0)),
                "cash_sell": float(rate.get("cash_sell", 0)),
                "spot_buy": float(rate.get("spot_buy", 0)),
                "spot_sell": float(rate.get("spot_sell", 0)),
                "selected_rate": float(rate.get(rate_type, 0)),
                "rate_type": rate_type
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "currency": currency
            }

    def calculate_exchange(self, currency: str, twd_amount: float, is_buying: bool = True):
        """
        計算換匯金額

        Args:
            currency: 貨幣代碼
            twd_amount: 台幣金額
            is_buying: True 表示買入外幣(用台幣換外幣), False 表示賣出外幣(用外幣換台幣)

        Returns:
            dict: 計算結果
        """
        try:
            # 買入外幣用銀行的賣出價，賣出外幣用銀行的買入價
            rate_type = "cash_sell" if is_buying else "cash_buy"
            rate_info = self.get_exchange_rate(currency, rate_type)

            if not rate_info["success"]:
                return rate_info

            rate = rate_info["selected_rate"]

            # 計算外幣金額
            if is_buying:
                foreign_amount = twd_amount / rate
                action = "買入"
            else:
                foreign_amount = twd_amount * rate
                action = "賣出"

            # 檢查是否超過限額
            rule = self.bank_rules.get(currency, {})
            max_amount = rule.get("max_amount", float('inf'))

            warning = None
            if is_buying and foreign_amount > max_amount:
                warning = f"注意：{action}金額 {foreign_amount:.2f} {currency} 超過單日限額 {max_amount} {currency}"

            return {
                "success": True,
                "currency": currency,
                "twd_amount": twd_amount,
                "foreign_amount": round(foreign_amount, 2),
                "rate": rate,
                "rate_type": rate_type,
                "action": action,
                "date": rate_info["date"],
                "warning": warning
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_multiple_rates(self, currencies: list):
        """
        取得多種貨幣的匯率

        Args:
            currencies: 貨幣代碼列表

        Returns:
            dict: 匯率資訊字典
        """
        results = {}
        for currency in currencies:
            results[currency] = self.get_exchange_rate(currency)

        return {
            "success": True,
            "rates": results,
            "timestamp": self.exchange_rate.get_now().isoformat()
        }

    def get_bank_rules(self, currency: str = None):
        """
        取得銀行換匯規則

        Args:
            currency: 貨幣代碼 (可選，不提供則返回所有規則)

        Returns:
            dict: 換匯規則
        """
        if currency:
            return {
                "success": True,
                "currency": currency,
                "rules": self.bank_rules.get(currency, {"error": "不支援的貨幣"})
            }

        return {
            "success": True,
            "all_rules": self.bank_rules
        }

    def roles(self):
        """
        返回銀行員角色資訊和換匯規則

        Returns:
            dict: 角色資訊
        """
        return {
            "role": self.role,
            "description": "專業的銀行外匯櫃員，提供匯率查詢和換匯服務",
            "supported_currencies": list(TaiwanExchangeRate.SUPPORTED_CURRENCIES.keys()),
            "bank_rules": self.bank_rules,
            "services": [
                "即時匯率查詢",
                "換匯金額計算",
                "多幣別匯率比較",
                "換匯規則諮詢"
            ]
        }

    def process_query(self, query: str):
        """
        處理用戶查詢 (使用 AI 理解自然語言)

        Args:
            query: 用戶查詢內容

        Returns:
            dict: 查詢結果
        """
        try:
            # 如果沒有 Gemini client，使用簡單的關鍵字匹配
            if not self.client:
                return self._simple_query_processing(query)

            # 使用 Gemini AI 理解用戶意圖
            return self._ai_query_processing(query)

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "抱歉，處理您的問題時發生錯誤。"
            }

    def _simple_query_processing(self, query: str):
        """簡單的關鍵字匹配處理"""
        query_lower = query.lower()
        import re

        # 匯率查詢
        if "匯率" in query or "rate" in query_lower:
            for currency in TaiwanExchangeRate.SUPPORTED_CURRENCIES.keys():
                if currency.lower() in query_lower or TaiwanExchangeRate.SUPPORTED_CURRENCIES[currency] in query:
                    return self.get_exchange_rate(currency)

        # 換匯計算 - 改進版，支援更多格式
        if "換" in query or "兌換" in query or "exchange" in query_lower:
            # 查找貨幣（增加常見別名）
            currency_aliases = {
                'JPY': ['日圓', '日幣', '日元'],
                'USD': ['美金', '美元', '美刀'],
                'EUR': ['歐元'],
                'CNY': ['人民幣', '人民币', '陸幣'],
                'GBP': ['英鎊', '英镑'],
                'HKD': ['港幣', '港币', '港元'],
                'AUD': ['澳洲', '澳幣', '澳元'],
                'SGD': ['新加坡', '新幣', '星幣'],
            }

            found_currency = None
            for currency, name in TaiwanExchangeRate.SUPPORTED_CURRENCIES.items():
                # 檢查標準名稱
                if currency.lower() in query_lower or name in query:
                    found_currency = currency
                    break
                # 檢查別名
                if currency in currency_aliases:
                    for alias in currency_aliases[currency]:
                        if alias in query:
                            found_currency = currency
                            break
                if found_currency:
                    break

            if not found_currency:
                return {
                    "success": True,
                    "message": "請指定要換的貨幣\n例如：「10000台幣換美金」或「我要換15萬日圓」"
                }

            # 判斷用戶的意圖並提取數字
            # 1. 如果明確提到"台幣"在數字前後 → 用台幣換外幣（正向）
            # 2. 如果數字+萬+外幣名稱（如"15萬日圓"、"100萬美金"）→ 想得到該外幣（反向）
            # 3. 如果數字+外幣名稱（如"15日圓"、"100美金"）→ 想得到該外幣（反向）
            # 4. 如果提到"多少"、"可以換" → 用台幣換外幣（正向）

            has_twd_keyword = '台幣' in query or 'TWD' in query or 'NT' in query
            currency_name = TaiwanExchangeRate.SUPPORTED_CURRENCIES[found_currency]

            # 構建所有可能的貨幣名稱列表
            if found_currency in currency_aliases:
                all_currency_names = [currency_name] + currency_aliases[found_currency]
            else:
                all_currency_names = [currency_name]

            # 檢查是否有"數字+萬+貨幣名稱"的模式（如"15萬日幣"）
            has_wan_currency_pattern = False
            wan_match = None
            for name in all_currency_names:
                pattern = rf'(\d+(?:\.\d+)?)\s*萬\s*{re.escape(name)}'
                match = re.search(pattern, query)
                if match:
                    wan_match = match
                    has_wan_currency_pattern = True
                    break

            # 檢查是否有"數字+貨幣名稱"的模式（如"15日圓"、"100美金"）
            has_direct_currency_pattern = False
            direct_match = None
            if not has_wan_currency_pattern:
                for name in all_currency_names:
                    pattern = rf'(\d+(?:\.\d+)?)\s*{re.escape(name)}'
                    match = re.search(pattern, query)
                    if match:
                        direct_match = match
                        has_direct_currency_pattern = True
                        break

            # 提取金額
            if wan_match:
                # "15萬日幣" → 150000
                amount = float(wan_match.group(1)) * 10000
            elif direct_match:
                # "15日幣" → 15
                amount = float(direct_match.group(1))
            elif re.search(r'(\d+(?:\.\d+)?)\s*萬', query):
                # "15萬台幣" → 150000
                match = re.search(r'(\d+(?:\.\d+)?)\s*萬', query)
                amount = float(match.group(1)) * 10000
            else:
                # 提取連續數字
                numbers = re.findall(r'\d+(?:\.\d+)?', query)
                if numbers:
                    amount = float(numbers[0])
                else:
                    return {
                        "success": True,
                        "message": f"請提供金額\n例如：「10000台幣換{currency_name}」"
                    }

            # 判斷是正向（台幣→外幣）還是反向（外幣→台幣）計算
            # 反向條件（優先）：數字緊鄰外幣名稱（表示想要那麼多外幣）
            # 正向條件：明確提到台幣 OR 有"可以換"/"能換"/"多少"等關鍵字

            is_reverse = (has_wan_currency_pattern or has_direct_currency_pattern) and not has_twd_keyword
            is_forward = has_twd_keyword or '可以換' in query or '能換' in query or '多少' in query

            if is_forward and not is_reverse:
                # 正向：用台幣換外幣
                result = self.calculate_exchange(found_currency, amount, True)
                if result["success"]:
                    return {
                        "success": True,
                        "type": "calculation",
                        "data": result,
                        "message": f"💱 換匯計算結果\n\n"
                                 f"台幣金額：NT$ {result['twd_amount']:,.0f}\n"
                                 f"可換得：{result['foreign_amount']:,.2f} {found_currency}\n"
                                 f"使用匯率（現金賣出）：{result['rate']}\n"
                                 f"日期：{result['date']}\n"
                                 f"{('⚠️ ' + result['warning']) if result.get('warning') else ''}"
                    }
                return result
            else:
                # 反向：想得到X外幣，需要多少台幣
                # 獲取匯率
                rate_info = self.get_exchange_rate(found_currency, 'cash_sell')
                if rate_info["success"]:
                    rate = rate_info["cash_sell"]
                    twd_needed = amount * rate

                    return {
                        "success": True,
                        "type": "reverse_calculation",
                        "data": {
                            "foreign_amount": amount,
                            "currency": found_currency,
                            "twd_needed": twd_needed,
                            "rate": rate,
                            "date": rate_info["date"]
                        },
                        "message": f"💱 換匯計算結果\n\n"
                                 f"想換得：{amount:,.2f} {found_currency}\n"
                                 f"需要台幣：NT$ {twd_needed:,.2f}\n"
                                 f"使用匯率（現金賣出）：{rate}\n"
                                 f"日期：{rate_info['date']}"
                    }
                else:
                    return rate_info

        # 規則查詢
        if "規則" in query or "限額" in query or "rule" in query_lower:
            return self.get_bank_rules()

        # 默認返回角色資訊
        return {
            "success": True,
            "message": "您好！我是銀行外匯櫃員助手。\n\n您可以問我：\n• 「美金匯率多少？」\n• 「10000台幣可以換多少日圓？」\n• 「我要換15萬日圓」\n• 「換匯有什麼限額？」"
        }

    def _ai_query_processing(self, query: str):
        """使用 Gemini AI 處理自然語言查詢"""
        try:
            # 構建系統提示
            system_prompt = f"""你是一位專業的銀行外匯櫃員助手。

支援的貨幣：{', '.join([f"{code}({name})" for code, name in TaiwanExchangeRate.SUPPORTED_CURRENCIES.items()])}

你的任務是理解用戶的問題並返回 JSON 格式的回應：

1. 如果用戶詢問匯率，返回：
{{"action": "get_rate", "currency": "貨幣代碼"}}

2. 如果用戶想換匯，返回：
{{"action": "calculate", "currency": "貨幣代碼", "amount": 台幣金額}}

3. 如果用戶詢問限額或規則，返回：
{{"action": "get_rules", "currency": "貨幣代碼或null"}}

4. 如果用戶詢問匯率趨勢或建議，返回：
{{"action": "advice", "currency": "貨幣代碼", "context": "用戶問題摘要"}}

5. 如果無法理解，返回：
{{"action": "clarify", "message": "需要用戶澄清的問題"}}

只返回 JSON，不要其他文字。"""

            # 調用 Gemini API
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=f"{system_prompt}\n\n用戶問題：{query}"
            )

            # 解析 AI 回應
            import json
            ai_response = response.text.strip()

            # 移除可能的 markdown 代碼塊標記
            if ai_response.startswith('```'):
                ai_response = ai_response.split('```')[1]
                if ai_response.startswith('json'):
                    ai_response = ai_response[4:]
                ai_response = ai_response.strip()

            action_data = json.loads(ai_response)

            # 根據 AI 的理解執行相應操作
            return self._execute_action(action_data, query)

        except Exception as e:
            print(f"AI processing error: {e}")
            # 降級到簡單處理
            return self._simple_query_processing(query)

    def _execute_action(self, action_data: dict, original_query: str):
        """根據 AI 解析的動作執行相應操作"""
        action = action_data.get("action")

        if action == "get_rate":
            currency = action_data.get("currency", "").upper()
            if currency in TaiwanExchangeRate.SUPPORTED_CURRENCIES:
                result = self.get_exchange_rate(currency)
                if result["success"]:
                    return {
                        "success": True,
                        "type": "rate_info",
                        "data": result,
                        "message": f"📊 {TaiwanExchangeRate.SUPPORTED_CURRENCIES[currency]}（{currency}）最新匯率\n\n"
                                 f"💰 現金買入：{result['cash_buy']} TWD\n"
                                 f"💵 現金賣出：{result['cash_sell']} TWD\n"
                                 f"📅 日期：{result['date']}\n\n"
                                 f"提示：買入外幣使用「賣出價」"
                    }
                return result

        elif action == "calculate":
            currency = action_data.get("currency", "").upper()
            amount = action_data.get("amount")

            if currency in TaiwanExchangeRate.SUPPORTED_CURRENCIES and amount:
                result = self.calculate_exchange(currency, float(amount), True)
                if result["success"]:
                    warning_msg = f"\n\n⚠️ {result['warning']}" if result.get('warning') else ""
                    return {
                        "success": True,
                        "type": "calculation",
                        "data": result,
                        "message": f"💱 換匯計算結果\n\n"
                                 f"台幣金額：NT$ {result['twd_amount']:,.0f}\n"
                                 f"可換得：{result['foreign_amount']:,.2f} {currency}\n"
                                 f"使用匯率：{result['rate']}\n"
                                 f"日期：{result['date']}{warning_msg}"
                    }
                return result

        elif action == "get_rules":
            currency = action_data.get("currency")
            result = self.get_bank_rules(currency.upper() if currency else None)

            if result["success"]:
                if currency:
                    rules = result.get("rules", {})
                    return {
                        "success": True,
                        "type": "rules",
                        "data": result,
                        "message": f"📋 {rules.get('name')} 換匯規則\n\n"
                                 f"單日限額：{rules.get('max_amount'):,.0f} {currency.upper()}\n\n"
                                 f"提示：超過限額需要事先預約"
                    }
                else:
                    return {
                        "success": True,
                        "type": "rules",
                        "data": result,
                        "message": "📋 銀行換匯規則\n\n各幣別單日限額：\n" +
                                 "\n".join([f"• {info['name']}：{info['max_amount']:,.0f} {curr}"
                                          for curr, info in self.bank_rules.items()])
                    }
            return result

        elif action == "advice":
            currency = action_data.get("currency", "").upper()
            context = action_data.get("context", "")

            if currency in TaiwanExchangeRate.SUPPORTED_CURRENCIES:
                # 獲取歷史匯率
                historical = self.exchange_rate.get_historical_rates(currency, days=7)
                current = self.get_exchange_rate(currency)

                if current["success"] and not historical.empty:
                    # 計算趨勢
                    recent_avg = historical['cash_sell'].tail(3).mean()
                    current_rate = current['cash_sell']
                    trend = "上升" if current_rate > recent_avg else "下降" if current_rate < recent_avg else "持平"

                    return {
                        "success": True,
                        "type": "advice",
                        "data": {
                            "currency": currency,
                            "current_rate": current_rate,
                            "trend": trend,
                            "historical": historical.to_dict()
                        },
                        "message": f"💡 {TaiwanExchangeRate.SUPPORTED_CURRENCIES[currency]} 匯率分析\n\n"
                                 f"目前匯率：{current_rate}\n"
                                 f"近期趨勢：{trend}\n"
                                 f"3日平均：{recent_avg:.3f}\n\n"
                                 f"{'📈 匯率較高，可考慮觀望' if trend == '上升' else '📉 匯率較低，適合換匯' if trend == '下降' else '➡️ 匯率平穩'}"
                    }

        elif action == "clarify":
            return {
                "success": True,
                "type": "clarify",
                "message": action_data.get("message", "我不太理解您的問題。\n\n您可以試試：\n• 「美金匯率多少？」\n• 「10000台幣換日圓」")
            }

        # 默認回應
        return {
            "success": True,
            "message": "抱歉，我無法理解您的問題。請試試：\n• 「美金匯率多少？」\n• 「10000台幣換日圓」\n• 「日幣限額多少？」"
        }





