"""
Reproduction System - 再生产系统

Handles:
- Simple reproduction (简单再生产)
- Expanded reproduction (扩大再生产)
- Crisis detection (危机检测)
- Production price transformation (生产价格转化)
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass

from src.engine.labor_value import SNLTCalculator


@dataclass
class ReproductionSchema:
    """再生产图式 - Reproduction schema for class analysis"""
    department_i_constant_capital: float
    department_i_variable_capital: float
    department_i_surplus_value: float
    department_ii_constant_capital: float
    department_ii_variable_capital: float
    department_ii_surplus_value: float


class ReproductionEngine:
    """
    再生产引擎 - Reproduction engine.

    Analyzes whether the reproduction schema is balanced:
    I(v+m) = II(c) for simple reproduction
    I(v+m) > II(c) for expanded reproduction
    I(v+m) < II(c) signals crisis

    Also handles production price transformation (利润率平均化):
    - 价值 -> 生产价格
    - 各部门利润率 -> 平均利润率
    """

    def __init__(self):
        self.crisis_indicators = {
            'rate_of_surplus_value': 0.0,
            'organic_composition': 0.0,
            'department_imbalance': 0.0,
            'rate_of_profit': 0.0,
        }
        self.average_rate_of_profit: float = 0.0
        self.production_price_enabled: bool = False

    def calculate_reproduction_schema(self, model) -> ReproductionSchema:
        """计算再生产图式 - 基于实际数据"""
        # 汇总各部类的资本
        i_constant = 0.0  # 生产资料部类 (c)
        i_variable = 0.0  # 生产资料部类 (v)
        i_surplus = 0.0   # 生产资料部类 (s)

        ii_constant = 0.0  # 消费资料部类 (c)
        ii_variable = 0.0  # 消费资料部类 (v)
        ii_surplus = 0.0   # 消费资料部类 (s)

        for agent in model._agent_lookup.values():
            # 判断部类
            if hasattr(agent, 'machines_owned') and agent.machines_owned:
                # 拥有生产资料的属于第一部类
                i_constant += self._get_constant_capital(agent)
                i_variable += self._get_variable_capital(agent)
                i_surplus += self._get_surplus_value(agent)
            else:
                # 其他属于第二部类
                ii_constant += self._get_constant_capital(agent)
                ii_variable += self._get_variable_capital(agent)
                ii_surplus += self._get_surplus_value(agent)

        return ReproductionSchema(
            department_i_constant_capital=i_constant,
            department_i_variable_capital=i_variable,
            department_i_surplus_value=i_surplus,
            department_ii_constant_capital=ii_constant,
            department_ii_variable_capital=ii_variable,
            department_ii_surplus_value=ii_surplus,
        )

    def _get_constant_capital(self, agent) -> float:
        """获取某Agent的不变资本"""
        c = 0.0
        if hasattr(agent, 'machines_owned'):
            for machine in agent.machines_owned:
                if hasattr(machine, 'individual_labor_embodied'):
                    c += machine.individual_labor_embodied
        if hasattr(agent, 'commodity_inventory'):
            for matter in agent.commodity_inventory:
                if hasattr(matter, 'individual_labor_embodied'):
                    c += matter.individual_labor_embodied * 0.3
        return c

    def _get_variable_capital(self, agent) -> float:
        """获取某Agent的可变资本"""
        v = 0.0
        if hasattr(agent, 'value_equivalent_held'):
            v += agent.value_equivalent_held
        if hasattr(agent, 'workers_employed'):
            v += len(agent.workers_employed) * 8.0
        if hasattr(agent, 'labor_power_capacity'):
            v += agent.labor_power_capacity * 3.0
        return v

    def _get_surplus_value(self, agent) -> float:
        """获取某Agent的剩余价值"""
        s = 0.0
        if hasattr(agent, 'capital_stock') and agent.capital_stock > 0:
            s += agent.capital_stock * 0.2
        if hasattr(agent, 'serfs_controlled'):
            s += len(agent.serfs_controlled) * 1.0
        if hasattr(agent, 'slaves_owned'):
            s += len(agent.slaves_owned) * 0.5
        return s

    def calculate_average_rate_of_profit(self, model) -> float:
        """计算平均利润率

        公式: p' = 总剩余价值 / (总不变资本 + 总可变资本)
        """
        schema = self.calculate_reproduction_schema(model)

        total_c = schema.department_i_constant_capital + schema.department_ii_constant_capital
        total_v = schema.department_i_variable_capital + schema.department_ii_variable_capital
        total_s = schema.department_i_surplus_value + schema.department_ii_surplus_value

        total_capital = total_c + total_v
        if total_capital > 0:
            self.average_rate_of_profit = total_s / total_capital
        else:
            self.average_rate_of_profit = 0.0

        return self.average_rate_of_profit

    def transform_to_production_price(self, value: float, c: float, v: float) -> float:
        """将价值转化为生产价格

        生产价格 = 成本价格 + 平均利润
        成本价格 = c + v
        平均利润 = 成本价格 × 平均利润率

        Args:
            value: 原始价值 (c + v + s)
            c: 不变资本
            v: 可变资本
        """
        if not self.production_price_enabled:
            return value

        cost_price = c + v
        average_surplus = cost_price * self.average_rate_of_profit
        production_price = cost_price + average_surplus

        return production_price

    def enable_production_price(self, enabled: bool = True):
        """启用/禁用生产价格转换"""
        self.production_price_enabled = enabled

    def calculate_complex_labor_multipliers(self, model) -> Dict[str, float]:
        """
        事后计算复杂劳动倍加系数 - Post-hoc complex labor multiplier calculation.

        RED LINE 6 COMPLIANCE: No a priori formula. The multiplier emerges
        from production price equalization across sectors.

        公式: multiplier_sector = (production_price_sector / SNLT_sector) /
                                   (production_price_baseline / SNLT_baseline)

        其中 baseline 是简单劳动部门（如谷物生产）。
        如果不存在生产价格（非资本主义阶段），所有 multiplier = 1.0。
        """
        if not self.production_price_enabled:
            return {}

        # 获取各部门的生产价格（通过利润率平均化后的交换比例）
        # 谷物部门作为简单劳动基准
        grain_snlt = SNLTCalculator.get_snlt('grain')
        if grain_snlt <= 0:
            return {}

        # 计算各部门相对于谷物部门（简单劳动）的倍加系数
        multipliers = {}
        for commodity_type in ['grain', 'hand_tool', 'weapon', 'shelter', 'craft_tool']:
            snlt = SNLTCalculator.get_snlt(commodity_type)
            if snlt <= 0:
                continue

            # 生产价格 = 成本价格 x (1 + 平均利润率)
            # 简化：使用 SNLT 比率作为近似，但只在生产价格启用时
            cost_price_c = self._estimate_c_for_commodity(commodity_type)
            cost_price_v = self._estimate_v_for_commodity(commodity_type)
            cost_price = cost_price_c + cost_price_v + snlt * 0.5  # 近似 s
            production_price = self.transform_to_production_price(cost_price, cost_price_c, cost_price_v)

            # 倍加系数 = (部门生产价格/部门SNLT) / (谷物生产价格/谷物SNLT)
            if snlt > 0 and grain_snlt > 0:
                ratio = (production_price / snlt) / (SNLTCalculator.get_snlt('grain') / grain_snlt)
                multipliers[commodity_type] = max(1.0, ratio)

        return multipliers

    def _estimate_c_for_commodity(self, commodity_type: str) -> float:
        """估算某商品的不变资本消耗"""
        c_map = {
            'grain': 1.0,
            'hand_tool': 3.0,
            'weapon': 2.0,
            'shelter': 5.0,
            'craft_tool': 2.0,
        }
        return c_map.get(commodity_type, 1.0)

    def _estimate_v_for_commodity(self, commodity_type: str) -> float:
        """估算某商品的可变资本消耗"""
        v_map = {
            'grain': 4.0,
            'hand_tool': 3.0,
            'weapon': 2.5,
            'shelter': 8.0,
            'craft_tool': 3.0,
        }
        return v_map.get(commodity_type, 4.0)

    def check_balance(self, schema: ReproductionSchema) -> Tuple[bool, str]:
        """
        检查再生产平衡 - Check reproduction balance.

        Returns (is_balanced, reason)
        """
        # Simple reproduction: I(v+m) should equal II(c)
        i_vm = schema.department_i_variable_capital + schema.department_i_surplus_value
        ii_c = schema.department_ii_constant_capital

        imbalance = abs(i_vm - ii_c) / max(i_vm, ii_c, 1.0)

        if imbalance < 0.05:
            return True, "Balanced"
        elif i_vm > ii_c:
            return False, "Department I surplus - expanded reproduction possible"
        else:
            return False, "Department II surplus - crisis of overproduction"

    def detect_crisis(self, model) -> Dict[str, float]:
        """
        检测危机 - Detect crisis indicators.

        Crisis cannot be caused by "insufficient demand" -
        only by利润率下降 or再生产比例失衡.
        """
        # Calculate average profit rate first
        self.calculate_average_rate_of_profit(model)

        # Calculate rate of surplus value: s/v
        total_surplus = self._calculate_total_surplus(model)
        total_variable = self._calculate_total_variable(model)

        if total_variable > 0:
            rate_of_surplus = total_surplus / total_variable
        else:
            rate_of_surplus = 0.0

        # Calculate organic composition: c/v
        total_constant = self._calculate_total_constant(model)
        if total_variable > 0:
            organic_composition = total_constant / total_variable
        else:
            organic_composition = 0.0

        # Calculate rate of profit: s/(c+v) - use average rate of profit for capitalist stage
        if model.social_stage.value == 'capitalist_state':
            rate_of_profit = self.average_rate_of_profit
        elif (total_constant + total_variable) > 0:
            rate_of_profit = total_surplus / (total_constant + total_variable)
        else:
            rate_of_profit = 0.0

        # Department imbalance
        schema = self.calculate_reproduction_schema(model)
        _, reason = self.check_balance(schema)
        imbalance_score = 1.0 if "crisis" in reason.lower() else 0.0

        self.crisis_indicators = {
            'rate_of_surplus_value': rate_of_surplus,
            'organic_composition': organic_composition,
            'rate_of_profit': rate_of_profit,
            'department_imbalance': imbalance_score,
        }

        return self.crisis_indicators

    def _calculate_total_surplus(self, model) -> float:
        """计算总剩余价值

        剩余价值 = 劳动者创造的超出劳动力价值的新价值
        简化计算：基于库存价值和劳动能力消耗估算
        """
        total_surplus = 0.0

        for agent in model._agent_lookup.values():
            # 资本家的库存（部分为剩余价值）
            if hasattr(agent, 'capital_stock') and agent.capital_stock > 0:
                total_surplus += agent.capital_stock * 0.3

            # 领主的库存
            if hasattr(agent, 'serfs_controlled'):
                surplus_from_rent = len(agent.serfs_controlled) * 2.0
                total_surplus += surplus_from_rent

            # 奴隶主的剩余价值提取
            if hasattr(agent, 'slaves_owned'):
                surplus_from_slaves = len(agent.slaves_owned) * 1.5
                total_surplus += surplus_from_slaves

            # 工人的工资余额（部分为剩余价值）
            if hasattr(agent, 'value_equivalent_held') and agent.value_equivalent_held > 10:
                total_surplus += agent.value_equivalent_held * 0.2

        return total_surplus

    def _calculate_total_variable(self, model) -> float:
        """计算总可变资本 v

        可变资本是用于购买劳动力的资本
        """
        total_variable = 0.0

        for agent in model._agent_lookup.values():
            # 工人的价值等价物持有（工资）
            if hasattr(agent, 'value_equivalent_held'):
                total_variable += agent.value_equivalent_held

            # 资本家支付的工资
            if hasattr(agent, 'workers_employed'):
                wages = len(agent.workers_employed) * 8.0
                total_variable += wages

            # 农奴的劳动能力价值（简化）
            if hasattr(agent, 'labor_power_capacity'):
                total_variable += agent.labor_power_capacity * 5.0

        return total_variable

    def _calculate_total_constant(self, model) -> float:
        """计算总不变资本 c

        不变资本是生产资料的价值，在生产过程中转移但不创造新价值
        """
        total_constant = 0.0

        for agent in model._agent_lookup.values():
            # 机器价值
            if hasattr(agent, 'machines_owned'):
                for machine in agent.machines_owned:
                    if hasattr(machine, 'individual_labor_embodied'):
                        total_constant += machine.individual_labor_embodied

            # 库存中的生产工具
            if hasattr(agent, 'commodity_inventory'):
                for matter in agent.commodity_inventory:
                    if hasattr(matter, 'individual_labor_embodied'):
                        total_constant += matter.individual_labor_embodied * 0.5

        return total_constant