"""
Mode of Production - 生产方式与状态机

Handles transition between different modes of production:
- Primitive communal (原始共产)
- Slave society (奴隶社会)
- Feudalism (封建社会)
- Capitalism (资本主义)
- Socialism (社会主义)
"""

from enum import Enum
from typing import Dict, Set


class ModeOfProduction(Enum):
    """生产方式枚举"""
    PRIMITIVE_COMMUNAL = "primitive_communal"
    SLAVE_SOCIETY = "slave_society"
    FEUDALISM = "feudalism"
    CAPITALISM = "capitalism"
    SOCIALISM = "socialism"


class TransitionEngine:
    """
    多元决定跃迁引擎 - Multi-determined transition engine.

    Evaluates whether conditions are met for mode of production transition.
    Based on Althusser's structural causality theory.
    """

    def __init__(self):
        self.current_mode = ModeOfProduction.PRIMITIVE_COMMUNAL
        self.transition_indicators: Dict[str, float] = {}

    def evaluate_transition(self, model) -> ModeOfProduction:
        """
        评估是否满足跃迁条件 - Evaluate if transition conditions are met.

        Returns current mode if no transition, otherwise returns new mode.
        """
        if self.current_mode == ModeOfProduction.PRIMITIVE_COMMUNAL:
            return self._check_primitive_transition(model)
        elif self.current_mode == ModeOfProduction.SLAVE_SOCIETY:
            return self._check_slave_transition(model)
        elif self.current_mode == ModeOfProduction.FEUDALISM:
            return self._check_feudal_transition(model)
        elif self.current_mode == ModeOfProduction.CAPITALISM:
            return self._check_capitalist_transition(model)
        return self.current_mode

    def _check_primitive_transition(self, model) -> ModeOfProduction:
        """检查原始社会跃迁条件"""
        # Transition to slave society requires:
        # 1. Surplus production > 0
        # 2. Social stratification (unequal distribution)
        # 3. Population density increase

        surplus_ratio = self._calculate_surplus_ratio(model)
        stratification = self._calculate_stratification(model)
        density = self._calculate_density(model)

        if surplus_ratio > 0.2 and stratification > 0.5 and density > 0.3:
            return ModeOfProduction.SLAVE_SOCIETY
        return ModeOfProduction.PRIMITIVE_COMMUNAL

    def _check_slave_transition(self, model) -> ModeOfProduction:
        """检查奴隶社会跃迁条件"""
        # Transition to feudalism requires:
        # 1. Slave resistance high (productivity low)
        # 2. Emergence of serf-like relations
        return self.current_mode

    def _check_feudal_transition(self, model) -> ModeOfProduction:
        """检查封建社会跃迁条件"""
        return self.current_mode

    def _check_capitalist_transition(self, model) -> ModeOfProduction:
        """检查资本主义跃迁条件"""
        return self.current_mode

    def _calculate_surplus_ratio(self, model) -> float:
        """计算剩余生产率"""
        total_produced = sum(
            len(a.commodity_inventory) for a in model._agent_lookup.values()
        )
        total_consumed = sum(
            1 for a in model._agent_lookup.values() if a.subsistence_satisfaction > 0.9
        )
        if total_consumed == 0:
            return 0.0
        return (total_produced - total_consumed) / total_consumed

    def _calculate_stratification(self, model) -> float:
        """计算社会分化度"""
        if len(model._agent_lookup) < 2:
            return 0.0

        subsistence_levels = [
            a.subsistence_satisfaction for a in model._agent_lookup.values()
        ]
        avg = sum(subsistence_levels) / len(subsistence_levels)
        variance = sum((x - avg) ** 2 for x in subsistence_levels) / len(subsistence_levels)
        return min(1.0, variance)

    def _calculate_density(self, model) -> float:
        """计算人口密度"""
        num_agents = len(model._agent_lookup)
        max_capacity = 200  # Arbitrary max for normalized density
        return min(1.0, num_agents / max_capacity)

    def get_current_mode(self) -> ModeOfProduction:
        """获取当前生产方式"""
        return self.current_mode