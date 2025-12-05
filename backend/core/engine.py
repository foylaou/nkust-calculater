from decimal import Decimal, InvalidOperation
from typing import Optional
from enum import Enum


class Operation(Enum):
    """K�P^�"""
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"


class CalculatorEngine:


    def __init__(self):
        self.display = "0"
        self.current_value = Decimal("0")
        self.stored_value: Optional[Decimal] = None
        self.operation: Optional[Operation] = None
        self.new_number = True
        self.error = False

    def press_digit(self, digit: str):

        if self.error:
            self.clear()

        if self.new_number:
            if digit == ".":
                self.display = "0."
            else:
                self.display = digit
            self.new_number = False
        else:

            if digit == "." and "." in self.display:
                return


            if self.display == "0" and digit != ".":
                self.display = digit
            else:
                self.display += digit


        try:
            self.current_value = Decimal(self.display)
        except InvalidOperation:
            self.display = "Error"
            self.error = True

    def press_operator(self, operator: str):

        if self.error:
            self.clear()
            return

        try:
            self.current_value = Decimal(self.display)
        except InvalidOperation:
            self.display = "Error"
            self.error = True
            return

        if self.stored_value is not None and self.operation is not None and not self.new_number:
            self._calculate()

        # 2XvMx<�K�P
        self.stored_value = self.current_value
        try:
            self.operation = Operation(operator)
        except ValueError:
            self.display = "Error"
            self.error = True
            return

        self.new_number = True

    def press_equals(self):

        if self.error:
            self.clear()
            return

        if self.stored_value is None or self.operation is None:
            return

        try:
            self.current_value = Decimal(self.display)
        except InvalidOperation:
            self.display = "Error"
            self.error = True
            return

        self._calculate()
        self.stored_value = None
        self.operation = None
        self.new_number = True

    def _calculate(self):

        if self.stored_value is None or self.operation is None:
            return

        try:
            if self.operation == Operation.ADD:
                result = self.stored_value + self.current_value
            elif self.operation == Operation.SUBTRACT:
                result = self.stored_value - self.current_value
            elif self.operation == Operation.MULTIPLY:
                result = self.stored_value * self.current_value
            elif self.operation == Operation.DIVIDE:
                if self.current_value == 0:
                    self.display = "Error: Division by zero"
                    self.error = True
                    return
                result = self.stored_value / self.current_value
            else:
                return


            self.current_value = result
            self.display = self._format_result(result)

        except (InvalidOperation, Exception) as e:
            self.display = "Error"
            self.error = True

    def _format_result(self, value: Decimal) -> str:

        if value == value.to_integral_value():
            return str(value.to_integral_value())


        formatted = str(value.quantize(Decimal("0.00000001")))

        if "." in formatted:
            formatted = formatted.rstrip("0").rstrip(".")

        return formatted

    def clear(self):

        self.display = "0"
        self.current_value = Decimal("0")
        self.stored_value = None
        self.operation = None
        self.new_number = True
        self.error = False

    def clear_entry(self):

        self.display = "0"
        self.current_value = Decimal("0")
        self.new_number = True
        self.error = False

    def backspace(self):

        if self.error or self.new_number:
            return

        if len(self.display) > 1:
            self.display = self.display[:-1]
        else:
            self.display = "0"
            self.new_number = True

        try:
            self.current_value = Decimal(self.display)
        except InvalidOperation:
            self.display = "0"
            self.current_value = Decimal("0")
