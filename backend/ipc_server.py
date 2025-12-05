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


class IPCServer:


    def __init__(self):
        self.engine = CalculatorEngine()
        self.units = UnitConverter()
        self.commercial = CommercialCalculator()
        self.toolkit = AgentToolkit(self.engine, self.units, self.commercial)


        if not os.getenv("ANTHROPIC_API_KEY"):
            sys.stderr.write("Warning: ANTHROPIC_API_KEY not set. AI Agent will not work.\n")
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
