"""
Class Struggle Engine - 阶级斗争引擎

Handles:
- Wage struggle
- Rent struggle
- Political mobilization
- Crisis and revolution
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class StruggleMetrics:
    """斗争指标"""
    strike_activity: float  # 0.0 to 1.0
    rent_resistance: float  # 农奴抵抗强度
    class_consciousness: float  # 阶级意识
    revolutionary_tension: float  # 革命张力


class ClassStruggleEngine:
    """
    阶级斗争引擎 - Class struggle engine.

    RED LINE: No "rational actor" assumptions.
    Struggle emerges from structural position in production relations.
    """

    def __init__(self):
        self.metrics = StruggleMetrics(
            strike_activity=0.0,
            rent_resistance=0.0,
            class_consciousness=0.0,
            revolutionary_tension=0.0
        )
        self.strike_history: List[int] = []
        self.rent_resistance_history: List[float] = []

    def calculate_strike_activity(self, workers: List, capitalists: List) -> float:
        """
        计算罢工活动 - Calculate strike activity level.

        Strike activity is determined by:
        1. Industrial reserve army size (unemployment)
        2. Real wage vs labor-power value
        3. Class consciousness
        """
        if not workers:
            return 0.0

        # Calculate unemployment rate
        total_labor_force = len(workers) + len(capitalists)
        unemployed_rate = 1.0 - (len(workers) / max(total_labor_force, 1))

        # Calculate average real wage
        avg_wage = sum(w.value_equivalent_held for w in workers) / max(len(workers), 1)
        avg_labor_power_value = sum(
            self._calculate_labor_power_value(w) for w in workers
        ) / max(len(workers), 1)

        wage_ratio = avg_wage / max(avg_labor_power_value, 0.1)

        # Strike activity increases when:
        # - Unemployment is low (workers have bargaining power)
        # - Wages are below labor-power value
        strike_activity = (1.0 - unemployed_rate) * (1.0 - min(wage_ratio, 1.0))

        self.metrics.strike_activity = strike_activity
        self.strike_history.append(int(strike_activity > 0.3))

        return strike_activity

    def calculate_rent_resistance(self, serfs: List, lords: List) -> float:
        """
        计算地租抵抗强度 - Calculate rent resistance.

        Resistance increases when:
        1. Surplus extraction ratio is high
        2. Serfs have accumulated some wealth
        3. Class consciousness is rising
        """
        if not serfs or not lords:
            return 0.0

        # Calculate extraction ratio
        total_surplus = sum(len(s.commodity_inventory) for s in serfs) / max(len(serfs), 1)
        total_consumed = sum(s.subsistence_satisfaction for s in serfs) / max(len(serfs), 1)

        extraction_ratio = 1.0 - (total_consumed / max(total_surplus, 1.0))

        # Serfs with some wealth resist more
        serf_wealth = sum(s.value_equivalent_held for s in serfs) / max(len(serfs), 1)
        wealth_factor = min(serf_wealth / 10.0, 1.0)

        resistance = extraction_ratio * (0.5 + 0.5 * wealth_factor)

        self.metrics.rent_resistance = resistance
        self.rent_resistance_history.append(resistance)

        return resistance

    def calculate_revolutionary_tension(self, model) -> float:
        """
        计算革命张力 - Calculate revolutionary tension.

        Revolution occurs when structural contradictions are combined with
        class consciousness. NOT when people are "dissatisfied".
        """
        # Get crisis indicators
        crisis = model.reproduction_engine.crisis_indicators

        # Calculate organic composition trend
        oc = crisis.get('organic_composition', 0.0)

        # Profit rate trend
        pr = crisis.get('profit_rate', 0.0)

        # Department imbalance
        imbalance = crisis.get('department_imbalance', 0.0)

        # Legitimacy of existing order (from ideology subsystem)
        legitimacy = 0.5  # Placeholder

        # Revolutionary tension: structural crisis + declining legitimacy
        tension = (oc / max(pr, 0.01)) * (1.0 - legitimacy) * (1.0 + imbalance)

        self.metrics.revolutionary_tension = min(1.0, tension)
        return self.metrics.revolutionary_tension

    def _calculate_labor_power_value(self, worker) -> float:
        """计算劳动力价值"""
        from src.engine.labor_value import SNLTCalculator
        return SNLTCalculator.calculate_labor_power_value(worker)

    def get_struggle_metrics(self) -> Dict:
        """获取斗争指标"""
        return {
            'strike_activity': self.metrics.strike_activity,
            'rent_resistance': self.metrics.rent_resistance,
            'class_consciousness': self.metrics.class_consciousness,
            'revolutionary_tension': self.metrics.revolutionary_tension,
        }

    def consolidate_wage_struggle(self, capitalist, model) -> float:
        """
        整合工资斗争 - 计算单个资本家的工人斗争强度

        Returns斗争参与率 (0.0 - 1.0)
        """
        workers = []
        for worker_id in capitalist.workers_employed:
            worker = model.get_agent(worker_id)
            if worker and hasattr(worker, 'value_equivalent_held'):
                workers.append(worker)

        if not workers:
            return 0.0

        # 计算工资斗争强度
        avg_wage = sum(w.value_equivalent_held for w in workers) / len(workers)
        avg_labor_power_value = sum(
            self._calculate_labor_power_value(w) for w in workers
        ) / len(workers)

        # 工资低于劳动力价值时斗争加剧
        wage_ratio = avg_wage / max(avg_labor_power_value, 0.1)
        struggle_level = max(0.0, 1.0 - wage_ratio)

        # 产业后备军规模影响斗争力度
        unemployed_count = 0
        for agent in model._agent_lookup.values():
            if hasattr(agent, 'employed_by') and agent.employed_by is None:
                if hasattr(agent, 'value_equivalent_held'):
                    unemployed_count += 1

        reserve_army_effect = unemployed_count / max(len(model._agent_lookup), 1)
        struggle_level *= (1.0 + reserve_army_effect)

        return min(1.0, struggle_level)

    def consolidate_rent_struggle(self, serf, model) -> float:
        """
        整合地租斗争 - 计算单个农奴的抗租强度

        Returns 抗租强度 (0.0 - 1.0)
        """
        if not hasattr(serf, 'lord_id') or not serf.lord_id:
            return 0.0

        lord = model.get_agent(serf.lord_id)
        if not lord:
            return 0.0

        # 剩余提取率
        if serf.commodity_inventory:
            serf_surplus = len(serf.commodity_inventory)
        else:
            serf_surplus = 0.0

        # 生存满意度反映被剥削程度
        exploitation = 1.0 - serf.subsistence_satisfaction

        # 有一定财富积累的农奴更有能力抵抗
        wealth_factor = min(serf.value_equivalent_held / 10.0, 1.0)

        resistance = exploitation * (0.5 + 0.5 * wealth_factor)

        return min(1.0, resistance)