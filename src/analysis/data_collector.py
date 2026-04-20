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
            **self.model.social_graph.calculate_graph_metrics(),
        }

        # Add class distribution
        step_data['class_distribution'] = self._count_classes()

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
