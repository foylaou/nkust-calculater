from typing import Any, Callable
from dataclasses import dataclass
from decimal import Decimal
import json


@dataclass
class Tool:
    """Agent 可使用的工具定義"""
    name: str
    description: str
    parameters: dict  # JSON Schema
    function: Callable


class AgentToolkit:
    """
    Agent 工具集 - 定義 LLM 可呼叫的函數
    """

    def __init__(self, calculator_engine, unit_converter, commercial_calc):
        self.engine = calculator_engine
        self.units = unit_converter
        self.commercial = commercial_calc
        self.tools = self._register_tools()

    def _register_tools(self) -> list[Tool]:
        return [
            Tool(
                name="calculate_basic",
                description="執行基本數學運算 (加減乘除)",
                parameters={
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "數學表達式，如 '200 * 0.75'"
                        }
                    },
                    "required": ["expression"]
                },
                function=self._basic_calculate
            ),
            Tool(
                name="convert_unit",
                description="單位轉換，支援面積單位如公頃、畝、坪、甲等",
                parameters={
                    "type": "object",
                    "properties": {
                        "value": {"type": "number", "description": "數值"},
                        "from_unit": {"type": "string", "description": "原始單位"},
                        "to_unit": {"type": "string", "description": "目標單位"}
                    },
                    "required": ["value", "from_unit", "to_unit"]
                },
                function=self._convert_unit
            ),
            Tool(
                name="calculate_price",
                description="商業價格計算，包含折扣和稅金。折扣用整數表示(75=75折)，稅率用百分比(5=5%)",
                parameters={
                    "type": "object",
                    "properties": {
                        "original_price": {"type": "number", "description": "原始價格"},
                        "discount_percent": {"type": "number", "description": "折扣，75表示75折(付75%)"},
                        "tax_percent": {"type": "number", "description": "稅率百分比，5表示5%"}
                    },
                    "required": ["original_price"]
                },
                function=self._calculate_price
            ),
            Tool(
                name="calculate_land_value",
                description="計算土地價值，根據面積和單價",
                parameters={
                    "type": "object",
                    "properties": {
                        "area": {"type": "number", "description": "面積數值"},
                        "area_unit": {"type": "string", "description": "面積單位"},
                        "price_per_unit": {"type": "number", "description": "每單位價格"},
                        "price_unit": {"type": "string", "description": "價格對應的單位"}
                    },
                    "required": ["area", "area_unit", "price_per_unit", "price_unit"]
                },
                function=self._calculate_land_value
            )
        ]

    def _basic_calculate(self, expression: str) -> dict:
        """安全的數學表達式計算"""
        # 使用 Python 的 eval 但限制只能做數學運算
        allowed_chars = set("0123456789+-*/.(). ")
        if not all(c in allowed_chars for c in expression):
            return {"error": "不安全的表達式"}

        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return {"result": float(result), "expression": expression}
        except Exception as e:
            return {"error": str(e)}

    def _convert_unit(self, value: float, from_unit: str, to_unit: str) -> dict:
        try:
            result = self.units.convert(Decimal(str(value)), from_unit, to_unit)
            return {
                "result": float(result),
                "from": f"{value} {from_unit}",
                "to": f"{result} {to_unit}"
            }
        except ValueError as e:
            return {"error": str(e)}

    def _calculate_price(self, original_price: float,
                         discount_percent: float = None,
                         tax_percent: float = None) -> dict:
        breakdown = self.commercial.calculate_price(
            Decimal(str(original_price)),
            discount_percent=discount_percent,
            tax_percent=tax_percent
        )
        return breakdown.to_dict()

    def _calculate_land_value(self, area: float, area_unit: str,
                              price_per_unit: float, price_unit: str) -> dict:
        """計算土地總價值"""
        try:
            # 將面積轉換到價格對應的單位
            converted_area = self.units.convert(
                Decimal(str(area)), area_unit, price_unit
            )
            total_value = converted_area * Decimal(str(price_per_unit))

            return {
                "original_area": f"{area} {area_unit}",
                "converted_area": f"{converted_area} {price_unit}",
                "price_per_unit": f"${price_per_unit:,.0f} / {price_unit}",
                "total_value": f"${float(total_value):,.0f}"
            }
        except ValueError as e:
            return {"error": str(e)}

    def get_tools_schema(self) -> list[dict]:
        """取得 OpenAI/Anthropic function calling 格式的工具定義"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in self.tools
        ]

    def execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """執行工具"""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.function(**arguments)
        raise ValueError(f"Unknown tool: {tool_name}")