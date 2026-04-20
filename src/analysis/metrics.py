"""
Metrics - 指标计算

Provides various metrics for analysis.
"""

from typing import Dict, List
import numpy as np


class MetricsCalculator:
    """
    指标计算器 - Various economic and social metrics.
    """

    @staticmethod
    def calculate_gini_coefficient(values: List[float]) -> float:
        """计算基尼系数"""
        if not values:
            return 0.0

        sorted_vals = sorted(values)
        n = len(values)
        cum_sum = sum(sorted_vals)

        if cum_sum == 0:
            return 0.0

        gini = (2 * sum((i+1) * v for i, v in enumerate(sorted_vals))) / (n * cum_sum) - (n + 1) / n

        return max(0.0, min(1.0, gini))

    @staticmethod
    def calculate_rate_of_surplus_value(surplus: float, variable_capital: float) -> float:
        """计算剩余价值率 s/v"""
        if variable_capital <= 0:
            return 0.0
        return surplus / variable_capital

    @staticmethod
    def calculate_organic_composition(constant_capital: float, variable_capital: float) -> float:
        """计算资本有机构成 c/v"""
        if variable_capital <= 0:
            return 0.0
        return constant_capital / variable_capital

    @staticmethod
    def calculate_profit_rate(surplus: float, constant_capital: float, variable_capital: float) -> float:
        """计算利润率 p' = s/(c+v)"""
        total_capital = constant_capital + variable_capital
        if total_capital <= 0:
            return 0.0
        return surplus / total_capital

    @staticmethod
    def calculateindustrial_reserve_army_rate(unemployed: int, employed: int) -> float:
        """计算产业后备军率"""
        total_labor = unemployed + employed
        if total_labor == 0:
            return 0.0
        return unemployed / total_labor

    @staticmethod
    def calculate_department_imbalance(i_vm: float, ii_c: float) -> float:
        """计算部类偏离度"""
        if ii_c == 0:
            return 0.0
        return abs(i_vm - ii_c) / ii_c

    @staticmethod
    def calculate_exploitation_rate(surplus_labor: float, necessary_labor: float) -> float:
        """计算剥削率"""
        if necessary_labor <= 0:
            return 0.0
        return surplus_labor / necessary_labor

    @staticmethod
    def get_all_metrics(model) -> Dict:
        """获取所有指标"""
        metrics = {}

        # Population metrics
        if hasattr(model, '_agent_lookup'):
            population = len(model._agent_lookup)
            metrics['population'] = population

            # Subsistence satisfaction
            if population > 0:
                avg_subsistence = sum(a.subsistence_satisfaction for a in model._agent_lookup.values()) / population
                metrics['avg_subsistence_satisfaction'] = avg_subsistence

                # Gini coefficient for subsistence
                subsistence_values = [a.subsistence_satisfaction for a in model._agent_lookup.values()]
                metrics['subsistence_gini'] = MetricsCalculator.calculate_gini_coefficient(subsistence_values)

        # Crisis indicators
        if hasattr(model, 'reproduction_engine'):
            crisis = model.reproduction_engine.crisis_indicators
            metrics.update(crisis)

        return metrics