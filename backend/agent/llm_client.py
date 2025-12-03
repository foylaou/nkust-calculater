import os
from anthropic import Anthropic
from typing import Generator
import json


class SmartCalculatorAgent:
    """
    智慧計算機 Agent - 使用 Claude 理解自然語言
    """

    def __init__(self, toolkit):
        self.client = Anthropic()  # 從環境變數讀取 API key
        self.toolkit = toolkit
        self.model = "claude-sonnet-4-20250514"

        self.system_prompt = """你是一個智慧型商用計算機助手。
            你可以處理:
            1. 基本數學運算
            2. 商業計算 (折扣、稅金、成本分析)
            3. 單位轉換 (特別是台灣常用的土地單位: 公頃、甲、分、畝、坪)
            
            台灣土地單位說明:
            - 1 公頃 = 10000 平方公尺
            - 1 甲 ≈ 2934 坪 ≈ 0.97 公頃
            - 1 分 = 0.1 甲
            - 1 畝 ≈ 666.67 平方公尺 (中國單位)
            - 1 坪 ≈ 3.306 平方公尺
            
            折扣表達方式:
            - "75折" = 付原價的 75% (discount_percent=75)
            - "打8折" = 付原價的 80%
            
            當用戶提出問題時，使用提供的工具進行計算，並清楚解釋計算過程和結果。"""

    def process_query(self, user_input: str) -> str:
        """
        處理用戶的自然語言輸入
        """
        messages = [{"role": "user", "content": user_input}]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.system_prompt,
            tools=self.toolkit.get_tools_schema(),
            messages=messages
        )

        # 處理工具呼叫迴圈
        while response.stop_reason == "tool_use":
            # 找出工具呼叫
            tool_use_block = next(
                block for block in response.content
                if block.type == "tool_use"
            )

            tool_name = tool_use_block.name
            tool_input = tool_use_block.input

            # 執行工具
            tool_result = self.toolkit.execute_tool(tool_name, tool_input)

            # 將結果加入對話
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                }]
            })

            # 繼續對話
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                tools=self.toolkit.get_tools_schema(),
                messages=messages
            )

        # 提取最終文字回應
        final_text = next(
            (block.text for block in response.content if hasattr(block, "text")),
            "無法處理您的請求"
        )

        return final_text