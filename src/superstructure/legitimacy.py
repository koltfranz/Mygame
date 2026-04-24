"""
Legitimacy - 合法性计算与危机判定

Calculates the legitimacy of the current political order
and determines crisis conditions.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Legitimacy:
    """
    合法性计算器 - Legitimacy calculator.

    Legitimacy is not based on "consent" but on the structural
    capacity of the mode of production to reproduce itself.
    """

    score: float = 0.5  # 0.0 = crisis, 1.0 = fully legitimate
    crisis_threshold: float = 0.3
    crisis_active: bool = False

    def calculate(self, model) -> float:
        """
        计算当前政权合法性

        基于:
        1. 统治阶级对被统治阶级的物质条件满足程度
        2. 法律形式平等指数
        3. 危机程度
        4. 意识形态霸权强度
        """
        from src.engine.reproduction import ReproductionEngine

        crisis_indicators = model.reproduction_engine.crisis_indicators

        # 利润率下降降低合法性
        rate_of_profit = crisis_indicators.get('rate_of_profit', 0.2)
        profit_rate_factor = min(1.0, rate_of_profit / 0.2)

        # 部类失衡降低合法性
        imbalance = crisis_indicators.get('department_imbalance', 0.0)
        balance_factor = 1.0 - imbalance

        # 生存资料满足率
        avg_subsistence = model.get_average_subsistence()
        subsistence_factor = avg_subsistence

        # 阶级意识提高时合法性下降
        class_consciousness = 0.3  # Placeholder

        # 综合计算
        raw_score = (
            profit_rate_factor * 0.3 +
            balance_factor * 0.3 +
            subsistence_factor * 0.2 +
            (1.0 - class_consciousness) * 0.2
        )

        self.score = max(0.0, min(1.0, raw_score))
        self.crisis_active = self.score < self.crisis_threshold

        return self.score

    def is_in_crisis(self) -> bool:
        """判断是否处于合法性危机"""
        return self.crisis_active or self.score < self.crisis_threshold

    def get_crisis_description(self) -> str:
        """获取危机状态描述"""
        if self.score > 0.7:
            return "政权稳固"
        elif self.score > 0.5:
            return "政权稳定"
        elif self.score > 0.3:
            return "政权面临压力"
        else:
            return "合法性危机"
