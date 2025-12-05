#!/usr/bin/env python3


import sys
import json
import os


sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from core.engine import CalculatorEngine
from core.units import UnitConverter
from core.commercial import CommercialCalculator
from agent.tools import AgentToolkit
from agent.llm_client import SmartCalculatorAgent
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
        self.engine = CalculatorEngine()
        self.units = UnitConverter()
        self.commercial = CommercialCalculator()
        self.toolkit = AgentToolkit(self.engine, self.units, self.commercial)

        # Determine if either ANTHROPIC_API_KEY or OPENAI_API_KEY is set
        has_anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        has_openai_key = os.getenv("OPENAI_API_KEY")
        has_gemeni_key = os.getenv("GEMENI_API_KEY")
        if not (has_anthropic_key or has_openai_key or has_gemeni_key):
            sys.stderr.write("Warning: Neither ANTHROPIC_API_KEY, OPENAI_API_KEY, nor GEMENI_API_KEY is set. AI Agent will not work.\n")
            sys.stderr.flush()
            self.agent = None
        else:
            self.agent = SmartCalculatorAgent(self.toolkit)

    def handle_request(self, request: dict) -> dict:

        action = request.get("action")

        try:

            if action == "calc_digit":
                value = request.get("value")
                self.engine.press_digit(value)
                return {"success": True, "display": self.engine.display}

            elif action == "calc_operator":
                operator = request.get("operator")
                self.engine.press_operator(operator)
                return {"success": True, "display": self.engine.display}

            elif action == "calc_equals":
                self.engine.press_equals()
                return {"success": True, "display": self.engine.display}

            elif action == "calc_clear":
                self.engine.clear()
                return {"success": True, "display": self.engine.display}

            elif action == "calc_backspace":
                self.engine.backspace()
                return {"success": True, "display": self.engine.display}

            # AI Agent �b
            elif action == "agent":
                if not self.agent:
                    return {
                        "success": False,
                        "error": "AI Agent not available. Please set ANTHROPIC_API_KEY."
                    }

                query = request.get("query")
                if not query:
                    return {"success": False, "error": "Missing query"}

                response = self.agent.process_query(query)
                return {"success": True, "response": response}

            # *��\
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
