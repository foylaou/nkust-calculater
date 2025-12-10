#!/usr/bin/env python3


import sys
import json
import os


sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from agent.agent import AI_Agent
import requests

class IPCServer:

    def validate_api_key(api_key: str) -> bool:
        """
        透過一個測試請求來驗證 API 金鑰的有效性。

        Args:
            api_key: 從使用者那裡取得的 API 金鑰。

        Returns:
            True 如果金鑰有效，否則 False。
        """
        # **請將此 URL 換成您要使用的真實 API 的驗證端點**
        # 範例：一個查詢帳戶狀態的端點
        validation_url = "https://api.hypothetical-service.com/v1/account/status"

        # API 金鑰通常放在 HTTP 標頭 (Header) 中
        # **請根據您的 API 文件修改標頭的格式** (例如可能是 'X-Api-Key')
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        print(f"正在驗證 API 金鑰...")

        try:
            # 發送一個 GET 請求，並設定超時以防應用程式卡住
            response = requests.get(validation_url, headers=headers, timeout=10)

            # 檢查回應狀態碼
            if response.status_code == 200:
                print("API 金鑰驗證成功！")
                return True
            elif response.status_code in [401, 403]:
                print(f"API 金鑰無效或沒有權限 (狀態碼: {response.status_code})")
                return False
            else:
                print(f"API 金鑰驗證失敗，伺服器回應: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            # 處理網路連線錯誤
            print(f"驗證 API 金鑰時發生網路錯誤: {e}")
            return False

    def __init__(self):
        # Initialize Bank Agent (Exchange Rate) - always available
        try:
            self.bank_agent = AI_Agent()
            sys.stderr.write("Bank Agent initialized successfully\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"Error: Failed to initialize Bank Agent: {e}\n")
            sys.stderr.flush()
            self.bank_agent = None

    def handle_request(self, request: dict) -> dict:

        action = request.get("action")

        try:
            # Exchange Rate - Get Rate
            if action == "exchange_rate":
                currency = request.get("currency")
                if not currency:
                    return {"success": False, "error": "Missing currency"}

                rate_type = request.get("rate_type", "cash_sell")
                result = self.bank_agent.get_exchange_rate(currency, rate_type)
                return result

            # Exchange Rate - Calculate Exchange
            elif action == "calculate_exchange":
                currency = request.get("currency")
                twd_amount = request.get("twd_amount")
                is_buying = request.get("is_buying", True)

                if not currency or twd_amount is None:
                    return {"success": False, "error": "Missing currency or twd_amount"}

                result = self.bank_agent.calculate_exchange(currency, float(twd_amount), is_buying)
                return result

            # Exchange Rate - Get Multiple Rates
            elif action == "get_multiple_rates":
                currencies = request.get("currencies")
                if not currencies:
                    return {"success": False, "error": "Missing currencies"}

                result = self.bank_agent.get_multiple_rates(currencies)
                return result

            # Exchange Rate - Get Bank Rules
            elif action == "get_bank_rules":
                currency = request.get("currency")
                result = self.bank_agent.get_bank_rules(currency)
                return result

            # Exchange Rate - Get Role Info
            elif action == "bank_agent_info":
                result = self.bank_agent.roles()
                return {"success": True, "info": result}

            # AI Chat - Process natural language query
            elif action == "ai_chat":
                query = request.get("query")
                if not query:
                    return {"success": False, "error": "Missing query"}

                result = self.bank_agent.process_query(query)
                return result

            # Unknown action
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def run(self):
        """;�� - �� stdin &�e stdout"""
        sys.stderr.write("IPC Server started\n")
        sys.stderr.flush()

        while True:
            try:

                line = sys.stdin.readline()
                if not line:

                    sys.stderr.write("EOF received, shutting down\n")
                    sys.stderr.flush()
                    break

                line = line.strip()
                if not line:
                    continue


                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    response = {"success": False, "error": f"Invalid JSON: {str(e)}"}
                    self._send_response(response)
                    continue


                response = self.handle_request(request)


                self._send_response(response)

            except KeyboardInterrupt:
                sys.stderr.write("Interrupted\n")
                sys.stderr.flush()
                break
            except Exception as e:
                sys.stderr.write(f"Error: {str(e)}\n")
                sys.stderr.flush()
                response = {"success": False, "error": str(e)}
                self._send_response(response)

    def _send_response(self, response: dict):

        try:
            json_str = json.dumps(response, ensure_ascii=False)
            sys.stdout.write(json_str + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Failed to send response: {str(e)}\n")
            sys.stderr.flush()


def main():


    from dotenv import load_dotenv
    load_dotenv()

    server = IPCServer()
    server.run()


if __name__ == "__main__":
    main()
