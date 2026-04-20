"""
Labor Value Calculator - 劳动价值计算引擎

Calculates:
- SNLT (Social Necessary Labor Time) - 社会必要劳动时间
- Individual labor time embodied
- Complex labor reduction to simple labor
"""

from typing import Dict, List, Optional
from collections import defaultdict
import numpy as np


class SNLTCalculator:
    """
    社会必要劳动时间计算器 - Social Necessary Labor Time Calculator.

    Value is NOT a static attribute - it is a post-hoc ghost ratio
    calculated based on reproduction conditions.
    """

    # Global SNLT registry by commodity type
    _global_snlt: Dict[str, float] = defaultdict(lambda: 10.0)  # Default 10 hours
    _total_produced: Dict[str, float] = defaultdict(float)
    _total_labor: Dict[str, float] = defaultdict(float)
    _sectors: Dict[str, str] = {}

    @classmethod
    def get_snlt(cls, commodity_type: str) -> float:
        """获取某商品的SNLT"""
        return cls._global_snlt.get(commodity_type, 10.0)

    @classmethod
    def set_snlt(cls, commodity_type: str, snlt: float):
        """设置某商品的SNLT"""
        cls._global_snlt[commodity_type] = snlt

    @classmethod
    def update_snlt(cls, commodity_type: str, individual_labor: float, quantity: float = 1.0):
        """
        更新SNLT - Update SNLT based on new production.

        SNLT is a weighted average that shifts as technology improves.
        """
        cls._total_produced[commodity_type] += quantity
        cls._total_labor[commodity_type] += individual_labor * quantity

        if cls._total_produced[commodity_type] > 0:
            # Calculate new SNLT as weighted average
            new_snlt = cls._total_labor[commodity_type] / cls._total_produced[commodity_type]

            # SNLT is sticky - doesn't adjust instantly (path dependency)
            old_snlt = cls._global_snlt[commodity_type]
            cls._global_snlt[commodity_type] = 0.9 * old_snlt + 0.1 * new_snlt

    @classmethod
    def calc_value(cls, commodity_type: str, quantity: float = 1.0) -> float:
        """
        计算价值 - Calculate value (post-hoc ghost ratio).

        value = SNLT × quantity
        """
        snlt = cls.get_snlt(commodity_type)
        return snlt * quantity

    @classmethod
    def calculate_labor_power_value(cls, agent) -> float:
        """
        计算劳动力价值 - Calculate labor-power value.

        labor_power_value = cost of necessary consumption + cost of training
        """
        # Necessary consumption cost (subsistence goods)
        necessary_consumption = 8.0  # Hours of labor per day for subsistence

        # Training cost amortization (spread over working life)
        if agent is not None and hasattr(agent, 'education_invested'):
            training_cost = agent.education_invested / 10000.0
        else:
            training_cost = 0.0

        # Total labor-power value per day
        return necessary_consumption + training_cost

    @classmethod
    def calculate_complex_labor_multiplier(cls, skill_level: float) -> float:
        """
        计算复杂劳动倍加系数 - Calculate complex labor multiplier.

        RED LINE: This is NOT a preset constant!
        It emerges from skill difference competition.
        """
        # Simple labor baseline: skill_level = 1.0
        # Complex labor: skill_level > 1.0

        # Multiplier is proportional to skill difference
        # But ONLY determined post-hoc through market competition
        if skill_level <= 1.0:
            return 1.0

        # Logarithmic scaling to prevent extreme values
        # 2.0 skill -> ~1.5x, 3.0 skill -> ~2.0x, etc.
        multiplier = 1.0 + np.log(skill_level)
        return min(multiplier, 4.0)  # Cap at 4x

    @classmethod
    def get_sector(cls, commodity_type: str) -> str:
        """获取商品所属部类"""
        return cls._sectors.get(commodity_type, "SECTOR_II")

    @classmethod
    def set_sector(cls, commodity_type: str, sector: str):
        """设置商品部类"""
        cls._sectors[commodity_type] = sector

    @classmethod
    def reset(cls):
        """重置计算器 - For testing"""
        cls._global_snlt.clear()
        cls._total_produced.clear()
        cls._total_labor.clear()
        cls._sectors.clear()