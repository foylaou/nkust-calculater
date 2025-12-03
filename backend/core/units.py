from decimal import Decimal
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class UnitDefinition:
    """單位定義"""
    name: str  # 單位名稱
    category: str  # 類別 (面積、長度、重量...)
    to_base: Decimal  # 轉換到基礎單位的乘數


class UnitConverter:
    """
    單位轉換器 - 處理台灣常用單位
    """

    def __init__(self):
        self.units: Dict[str, UnitDefinition] = {}
        self._register_default_units()

    def _register_default_units(self):
        # ====== 面積單位 ======
        # 基礎單位: 平方公尺 (m²)

        # 公制
        self.register("平方公尺", "面積", Decimal("1"))
        self.register("m²", "面積", Decimal("1"))
        self.register("公頃", "面積", Decimal("10000"))  # 1公頃 = 10000 m²
        self.register("甲", "面積", Decimal("9699.17"))  # 台灣: 1甲 ≈ 9699.17 m²
        self.register("分", "面積", Decimal("969.917"))  # 1分 = 0.1甲
        self.register("畝", "面積", Decimal("666.67"))  # 中國: 1畝 ≈ 666.67 m²
        self.register("坪", "面積", Decimal("3.30579"))  # 1坪 ≈ 3.306 m²
        self.register("平方公里", "面積", Decimal("1000000"))
        self.register("km²", "面積", Decimal("1000000"))

        # ====== 貨幣相關 (如需要) ======
        # 可以之後擴充匯率轉換

    def register(self, name: str, category: str, to_base: Decimal):
        """註冊新單位"""
        self.units[name] = UnitDefinition(name, category, to_base)

    def convert(self, value: Decimal, from_unit: str, to_unit: str) -> Decimal:
        """
        單位轉換
        例: convert(1, "公頃", "畝") -> 15 畝
        """
        if from_unit not in self.units:
            raise ValueError(f"未知單位: {from_unit}")
        if to_unit not in self.units:
            raise ValueError(f"未知單位: {to_unit}")

        from_def = self.units[from_unit]
        to_def = self.units[to_unit]

        if from_def.category != to_def.category:
            raise ValueError(f"無法轉換不同類別: {from_def.category} → {to_def.category}")

        # 先轉到基礎單位，再轉到目標單位
        base_value = value * from_def.to_base
        result = base_value / to_def.to_base

        return result.quantize(Decimal("0.0001"))  # 保留4位小數