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
        """计算社会分化度

        综合考虑:
        1. 生存资料满足率差异
        2. 商品库存差异
        3. 技能水平差异
        """
        if len(model._agent_lookup) < 2:
            return 0.0

        agents = list(model._agent_lookup.values())

        # 1. 生存资料满足率方差
        subsistence_levels = [a.subsistence_satisfaction for a in agents]
        subs_avg = sum(subsistence_levels) / len(subsistence_levels)
        subs_variance = sum((x - subs_avg) ** 2 for x in subsistence_levels) / len(subsistence_levels)

        # 2. 库存差异（基尼系数风格）
        inventories = [len(a.commodity_inventory) for a in agents]
        inv_avg = sum(inventories) / len(inventories) if inventories else 0
        if inv_avg > 0:
            inv_variance = sum((x - inv_avg) ** 2 for x in inventories) / len(inventories)
            inv_variance = min(1.0, inv_variance / (inv_avg ** 2 + 0.1))  # 标准化
        else:
            inv_variance = 0

        # 3. 技能水平差异
        skill_levels = [a.skill_level for a in agents]
        skill_avg = sum(skill_levels) / len(skill_levels)
        skill_variance = sum((x - skill_avg) ** 2 for x in skill_levels) / len(skill_levels)

        # 综合分化度
        combined = subs_variance * 0.5 + inv_variance * 0.3 + skill_variance * 0.2
        return min(1.0, combined * 10)  # 放大差异

    def _calculate_density(self, model) -> float:
        """计算人口密度"""
        num_agents = len(model._agent_lookup)
        max_capacity = 200  # Arbitrary max for normalized density
        return min(1.0, num_agents / max_capacity)

    def get_current_mode(self) -> ModeOfProduction:
        """获取当前生产方式"""
        return self.current_mode