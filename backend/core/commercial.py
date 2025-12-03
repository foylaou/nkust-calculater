from decimal import Decimal
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class TaxType(Enum):
    INCLUSIVE = "inclusive"  # 含稅價
    EXCLUSIVE = "exclusive"  # 未稅價


@dataclass
class PriceBreakdown:
    """價格明細"""
    original_price: Decimal  # 原價
    discount_rate: Optional[Decimal] = None  # 折扣率 (0.75 = 75折)
    discounted_price: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None  # 稅率 (0.05 = 5%)
    tax_amount: Optional[Decimal] = None
    final_price: Decimal = Decimal("0")

    def to_dict(self):
        return {
            "original_price": str(self.original_price),
            "discount_rate": f"{float(self.discount_rate) * 100}%" if self.discount_rate else None,
            "discounted_price": str(self.discounted_price) if self.discounted_price else None,
            "tax_rate": f"{float(self.tax_rate) * 100}%" if self.tax_rate else None,
            "tax_amount": str(self.tax_amount) if self.tax_amount else None,
            "final_price": str(self.final_price),
        }


class CommercialCalculator:
    """商業計算功能"""

    @staticmethod
    def apply_discount(price: Decimal, discount: Decimal) -> Decimal:
        """
        套用折扣
        discount: 0.75 表示 75折 (付 75%)
        """
        return price * discount

    @staticmethod
    def apply_tax(price: Decimal, tax_rate: Decimal,
                  tax_type: TaxType = TaxType.EXCLUSIVE) -> tuple[Decimal, Decimal]:
        """
        計算稅金
        回傳: (含稅價, 稅額)
        """
        if tax_type == TaxType.EXCLUSIVE:
            # 未稅價加稅
            tax_amount = price * tax_rate
            final = price + tax_amount
        else:
            # 從含稅價反推
            tax_amount = price - (price / (1 + tax_rate))
            final = price

        return final, tax_amount

    @classmethod
    def calculate_price(cls,
                        original: Decimal,
                        discount_percent: Optional[float] = None,  # 75 = 75折
                        tax_percent: Optional[float] = None  # 5 = 5%
                        ) -> PriceBreakdown:
        """
        完整價格計算

        例: calculate_price(200, discount_percent=75, tax_percent=5)
        $200 打 75 折後加 5% 稅
        """
        breakdown = PriceBreakdown(original_price=original)
        current_price = original

        # 套用折扣
        if discount_percent is not None:
            discount_rate = Decimal(str(discount_percent)) / 100
            breakdown.discount_rate = discount_rate
            current_price = cls.apply_discount(current_price, discount_rate)
            breakdown.discounted_price = current_price

        # 加稅
        if tax_percent is not None:
            tax_rate = Decimal(str(tax_percent)) / 100
            breakdown.tax_rate = tax_rate
            current_price, tax_amount = cls.apply_tax(current_price, tax_rate)
            breakdown.tax_amount = tax_amount

        breakdown.final_price = current_price.quantize(Decimal("0.01"))
        return breakdown