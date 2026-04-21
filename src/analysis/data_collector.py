"""
DataCollector - 数据收集器 for CapitalSimulator

Collects metrics each step for analysis.
"""

from typing import Dict
import numpy as np


class DataCollector:
    """
    数据收集器 - Collects and stores model data over time.

    Records:
    - Total population
    - Class distribution (inferred from social graph)
    - Average subsistence satisfaction
    - Social relation metrics
    - Crisis indicators
    - Economic indicators (profit rate, organic composition, etc.)
    """

    def __init__(self, model):
        self.model = model
        self.history: list = []

    def collect(self):
        """收集当前状态数据"""
        step_data = {
            'step': int(self.model.time),
            'total_population': self.model.get_population_count(),
            'average_subsistence': self.model.get_average_subsistence(),
            'social_stage': self.model.social_stage.value,
            **self.model.social_graph.calculate_graph_metrics(),
        }

        # Add class distribution
        step_data['class_distribution'] = self._count_classes()

        # Add transition indicators
        step_data['transition_indicators'] = self._collect_transition_indicators()

        # Add economic metrics
        step_data['economic_metrics'] = self._collect_economic_metrics()

        self.history.append(step_data)

    def _count_classes(self) -> Dict[str, int]:
        """统计各阶级人数"""
        counts = {
            'forager': 0,
            'tribe_member': 0,
            'worker': 0,
            'capitalist': 0,
            'slave': 0,
            'slave_owner': 0,
            'serf': 0,
            'lord': 0,
        }

        for agent in self.model._agent_lookup.values():
            class_pos = self.model.social_graph.infer_class_position(agent.unique_id)
            if class_pos in counts:
                counts[class_pos] += 1

        return counts

    def get_history(self) -> list:
        """获取历史数据"""
        return self.history

    def get_latest(self) -> Dict:
        """获取最新数据"""
        if self.history:
            return self.history[-1]
        return {}

    def _collect_transition_indicators(self) -> Dict[str, float]:
        """收集跃迁指标"""
        te = self.model.transition_engine
        return {
            'surplus_ratio': te._calculate_surplus_ratio(self.model),
            'stratification': te._calculate_stratification(self.model),
            'density': te._calculate_density(self.model),
        }

    def _collect_economic_metrics(self) -> Dict[str, float]:
        """收集经济指标"""
        metrics = {}

        # 计算阶级库存分布
        inventories = [len(a.commodity_inventory) for a in self.model._agent_lookup.values()]
        if inventories:
            metrics['avg_inventory'] = sum(inventories) / len(inventories)
            metrics['max_inventory'] = max(inventories)
            metrics['min_inventory'] = min(inventories)

        # 计算劳动能力分布
        labor_levels = [a.labor_power_capacity for a in self.model._agent_lookup.values()]
        if labor_levels:
            metrics['avg_labor_capacity'] = sum(labor_levels) / len(labor_levels)

        # 技能水平分布
        skill_levels = [a.skill_level for a in self.model._agent_lookup.values()]
        if skill_levels:
            metrics['avg_skill_level'] = sum(skill_levels) / len(skill_levels)

        return metrics
