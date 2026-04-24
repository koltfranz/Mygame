"""
DataCollector - 数据收集器 for CapitalSimulator

Collects metrics each step for analysis.
"""

from typing import Dict, List
import numpy as np
import networkx as nx


class DataCollector:
    """
    数据收集器 - Collects and stores model data over time.

    Records:
    - Total population (总人口)
    - Class distribution (阶级分布)
    - Average subsistence satisfaction (平均生存资料满足率)
    - Social relation metrics (社会关系指标)
    - Crisis indicators (危机指标)
    - Economic indicators (经济指标): 利润率、剩余价值率、资本有机构成、产业后备军率
    - Population dynamics (人口动态): 出生率、死亡率、增长率
    - Political indicators (政治指标): 政体类型、合法性、镇压能力、财政汲取能力
    - Cultural indicators (文化指标): 意识形态霸权、阶级意识
    - Network metrics (网络指标): 图密度、中心性、一般等价物集中度、物象化指数
    """

    def __init__(self, model):
        self.model = model
        self.history: list = []
        self._previous_population: int = 0
        self._births_total: int = 0
        self._deaths_total: int = 0

    def collect(self):
        """收集当前状态数据"""
        current_pop = self.model.get_population_count()

        # Calculate population dynamics
        pop_change = current_pop - self._previous_population
        self._births_total += max(0, pop_change)
        self._deaths_total += max(0, -pop_change)

        step_data = {
            'step': int(self.model.time),
            'total_population': current_pop,
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

        # Add population dynamics
        step_data['population_dynamics'] = self._collect_population_dynamics(current_pop)

        # Add political indicators
        step_data['political_indicators'] = self._collect_political_indicators()

        # Add cultural indicators
        step_data['cultural_indicators'] = self._collect_cultural_indicators()

        # Add network metrics
        step_data['network_metrics'] = self._collect_network_metrics()

        # Update previous population
        self._previous_population = current_pop

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

        # 从危机引擎获取经济指标
        if hasattr(self.model, 'reproduction_engine'):
            crisis = self.model.reproduction_engine.crisis_indicators
            metrics['rate_of_surplus_value'] = crisis.get('rate_of_surplus_value', 0.0)
            metrics['organic_composition'] = crisis.get('organic_composition', 0.0)
            metrics['rate_of_profit'] = crisis.get('rate_of_profit', 0.0)
            metrics['department_imbalance'] = crisis.get('department_imbalance', 0.0)

        return metrics

    def _collect_population_dynamics(self, current_pop: int) -> Dict[str, float]:
        """收集人口动态指标"""
        metrics = {}

        # 出生率、死亡率、增长率
        if current_pop > 0:
            metrics['birth_rate'] = self._births_total / (current_pop * max(1, len(self.history) + 1))
            metrics['death_rate'] = self._deaths_total / (current_pop * max(1, len(self.history) + 1))
            metrics['growth_rate'] = (self._births_total - self._deaths_total) / current_pop
        else:
            metrics['birth_rate'] = 0.0
            metrics['death_rate'] = 0.0
            metrics['growth_rate'] = 0.0

        # 总和生育率（简化估算）
        metrics['total_fertility_rate'] = 4.0 if current_pop > 10 else 0.0

        # 婴儿死亡率（简化估算）
        metrics['infant_mortality_rate'] = 0.1 if current_pop > 10 else 0.0

        # 净迁移量（模拟中假设为0，因为是封闭系统）
        metrics['net_migration'] = 0.0

        return metrics

    def _collect_political_indicators(self) -> Dict[str, float]:
        """收集政治指标"""
        metrics = {}

        # 政治体制信息
        if hasattr(self.model, 'political_regime'):
            pr = self.model.political_regime
            metrics['regime_type'] = pr.regime_type
            metrics['suffrage_level'] = pr.suffrage_level
        else:
            metrics['regime_type'] = 'unknown'
            metrics['suffrage_level'] = 0.0

        # 国家机器指标
        if hasattr(self.model, 'state_apparatus'):
            sa = self.model.state_apparatus
            metrics['state_repression_capacity'] = sa.repression_capacity
            metrics['fiscal_capacity'] = sa.fiscal_capacity
            metrics['state_form'] = sa.state_form
            metrics['ruling_class'] = sa.ruling_class
        else:
            metrics['state_repression_capacity'] = 0.0
            metrics['fiscal_capacity'] = 0.0
            metrics['state_form'] = 'none'
            metrics['ruling_class'] = 'none'

        # 法律形式平等指数
        regime = metrics.get('regime_type', 'unknown')
        metrics['legal_formal_equality'] = self._get_legal_equality(regime)

        # 产权保护强度
        metrics['property_rights_protection'] = self._get_property_rights(regime)

        return metrics

    def _collect_cultural_indicators(self) -> Dict[str, float]:
        """收集文化指标"""
        metrics = {}

        # 意识形态指标
        if hasattr(self.model, 'ideology_manager'):
            im = self.model.ideology_manager
            metrics['hegemony_strength'] = im.hegemony_strength
            metrics['legitimacy'] = im.legitimacy
            metrics['ideology_content'] = im.ideology_content
            metrics['avg_class_consciousness'] = sum(im.class_consciousness_by_class.values()) / len(im.class_consciousness_by_class)
        else:
            metrics['hegemony_strength'] = 0.5
            metrics['legitimacy'] = 0.5
            metrics['ideology_content'] = 'unknown'
            metrics['avg_class_consciousness'] = 0.2

        return metrics

    def _collect_network_metrics(self) -> Dict[str, float]:
        """收集网络指标"""
        metrics = {}

        if not hasattr(self.model, 'social_graph'):
            return metrics

        graph = self.model.social_graph.graph
        edge_counts = self.model.social_graph.get_edge_count_by_type()

        # 图密度
        if len(graph.nodes) > 0:
            metrics['graph_density'] = nx.density(graph)
        else:
            metrics['graph_density'] = 0.0

        # 边类型统计
        metrics['edge_counts'] = edge_counts

        # 地缘关系比例
        total_edges = sum(edge_counts.values())
        if total_edges > 0:
            metrics['residence_ratio'] = edge_counts.get('residence', 0) / total_edges
            metrics['kinship_ratio'] = (edge_counts.get('kinship', 0) + edge_counts.get('clan', 0)) / total_edges
        else:
            metrics['residence_ratio'] = 0.0
            metrics['kinship_ratio'] = 0.0

        # 一般等价物集中度
        if len(graph.nodes) > 0:
            in_degrees = [graph.in_degree(n) for n in graph.nodes]
            max_in = max(in_degrees) if in_degrees else 0
            total_in = sum(in_degrees) if in_degrees else 0
            metrics['general_equivalent_concentration'] = max_in / total_in if total_in > 0 else 0.0
        else:
            metrics['general_equivalent_concentration'] = 0.0

        # 物象化指数
        num_nodes = len(graph.nodes)
        num_edges = graph.number_of_edges()
        if num_nodes > 0:
            metrics['fetishism_index'] = min(1.0, num_edges / (num_nodes * (num_nodes - 1) + 1))
        else:
            metrics['fetishism_index'] = 0.0

        return metrics

    def _get_legal_equality(self, regime: str) -> float:
        """计算法律形式平等指数"""
        equality_map = {
            "tribal": 0.8,
            "workers_democracy": 0.9,
            "bourgeois_democracy": 0.7,
            "feudal_monarchy": 0.3,
            "slave_monarchy": 0.1,
            "primitive_horde": 0.9,
            "band": 0.85,
            "tribe": 0.8,
            "chiefdom": 0.4,
            "early_state": 0.35,
        }
        return equality_map.get(regime, 0.5)

    def _get_property_rights(self, regime: str) -> float:
        """计算产权保护强度"""
        protection_map = {
            "bourgeois_democracy": 0.9,
            "workers_democracy": 0.6,
            "feudal_monarchy": 0.4,
            "slave_monarchy": 0.2,
            "tribal": 0.7,
            "primitive_horde": 0.8,
            "band": 0.75,
            "tribe": 0.7,
            "chiefdom": 0.5,
            "early_state": 0.45,
        }
        return protection_map.get(regime, 0.5)
