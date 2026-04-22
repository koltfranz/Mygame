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
        if not values or len(values) < 2:
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
    def calculate_industrial_reserve_army_rate(unemployed: int, employed: int) -> float:
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
    def calculate_population_growth_rate(births: int, deaths: int, total_pop: int) -> float:
        """计算人口增长率"""
        if total_pop == 0:
            return 0.0
        return (births - deaths) / total_pop

    @staticmethod
    def calculate_trade_balance(exports: float, imports: float) -> float:
        """计算贸易差额"""
        return exports - imports

    @staticmethod
    def calculate_military_expenditure_ratio(military_spending: float, surplus_value: float) -> float:
        """计算军费占剩余价值比率"""
        if surplus_value <= 0:
            return 0.0
        return military_spending / surplus_value

    @staticmethod
    def calculate_colonial_net_extraction(extraction: float, costs: float) -> float:
        """计算殖民地净收益"""
        return extraction - costs

    @staticmethod
    def calculate_legal_formal_equality(regime_type: str) -> float:
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
        return equality_map.get(regime_type, 0.5)

    @staticmethod
    def calculate_property_rights_protection(regime_type: str) -> float:
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
        return protection_map.get(regime_type, 0.5)

    @staticmethod
    def calculate_state_repression_capacity(state_apparatus) -> float:
        """计算国家镇压能力"""
        if hasattr(state_apparatus, 'repression_capacity'):
            return state_apparatus.repression_capacity
        return 0.0

    @staticmethod
    def calculate_fiscal_capacity(state_apparatus) -> float:
        """计算财政汲取能力"""
        if hasattr(state_apparatus, 'fiscal_capacity'):
            return state_apparatus.fiscal_capacity
        return 0.0

    @staticmethod
    def calculate_legitimacy_score(ideology_manager) -> float:
        """计算合法性分数"""
        if hasattr(ideology_manager, 'legitimacy'):
            return ideology_manager.legitimacy
        return 0.0

    @staticmethod
    def calculate_cultural_hegemony_strength(ideology_manager) -> float:
        """计算文化霸权强度"""
        if hasattr(ideology_manager, 'hegemony_strength'):
            return ideology_manager.hegemony_strength
        return 0.0

    @staticmethod
    def calculate_repression_level(regime_type: str) -> float:
        """计算镇压水平"""
        repression_map = {
            "tribal": 0.1,
            "workers_democracy": 0.2,
            "bourgeois_democracy": 0.4,
            "feudal_monarchy": 0.6,
            "slave_monarchy": 0.8,
            "primitive_horde": 0.05,
            "band": 0.1,
            "tribe": 0.15,
            "chiefdom": 0.4,
            "early_state": 0.5,
        }
        return repression_map.get(regime_type, 0.3)

    @staticmethod
    def calculate_hereditary_power_index(stratification: float, surplus_ratio: float) -> float:
        """计算世袭权力指数"""
        if surplus_ratio <= 0:
            return 0.0
        return min(1.0, stratification * surplus_ratio / 10.0)

    @staticmethod
    def calculate_residence_ratio(edge_counts: Dict[str, int]) -> float:
        """计算地域划分比例（地缘关系占比）"""
        total_edges = sum(edge_counts.values())
        if total_edges == 0:
            return 0.0
        residence_edges = edge_counts.get('residence', 0)
        return residence_edges / total_edges

    @staticmethod
    def calculate_network_centrality(agent_id: int, graph) -> float:
        """计算节点的网络中心性（入度比率）"""
        if agent_id not in graph:
            return 0.0
        try:
            in_degree = graph.in_degree(agent_id)
            out_degree = graph.out_degree(agent_id)
            total_degree = in_degree + out_degree
            if total_degree == 0:
                return 0.0
            return in_degree / total_degree
        except Exception:
            return 0.0

    @staticmethod
    def calculate_general_equivalent_concentration(graph, relation_type: str = 'barter') -> float:
        """计算一般等价物入度垄断率"""
        if len(graph.nodes) == 0:
            return 0.0

        in_degrees = []
        for node in graph.nodes:
            in_degrees.append(graph.in_degree(node))

        if not in_degrees or max(in_degrees) == 0:
            return 0.0

        max_in_degree = max(in_degrees)
        total_in_degree = sum(in_degrees)

        if total_in_degree == 0:
            return 0.0

        return max_in_degree / total_in_degree

    @staticmethod
    def calculate_fetishism_index(graph, relation_type: str = 'barter') -> float:
        """计算物象化指数 - 商品交换关系复杂度"""
        if len(graph.nodes) == 0:
            return 0.0

        num_edges = graph.number_of_edges()
        num_nodes = len(graph.nodes)

        if num_nodes == 0:
            return 0.0

        return min(1.0, num_edges / (num_nodes * (num_nodes - 1) + 1))

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

                # Average inventory
                inventories = [len(a.commodity_inventory) for a in model._agent_lookup.values()]
                if inventories:
                    metrics['avg_inventory'] = sum(inventories) / len(inventories)
                    metrics['max_inventory'] = max(inventories)
                    metrics['min_inventory'] = min(inventories)

                # Average labor capacity
                labor_levels = [a.labor_power_capacity for a in model._agent_lookup.values()]
                if labor_levels:
                    metrics['avg_labor_capacity'] = sum(labor_levels) / len(labor_levels)

                # Average skill level
                skill_levels = [a.skill_level for a in model._agent_lookup.values()]
                if skill_levels:
                    metrics['avg_skill_level'] = sum(skill_levels) / len(skill_levels)

        # Crisis indicators
        if hasattr(model, 'reproduction_engine'):
            crisis = model.reproduction_engine.crisis_indicators
            metrics.update(crisis)

        # Social graph metrics
        if hasattr(model, 'social_graph'):
            graph = model.social_graph
            edge_counts = graph.get_edge_count_by_type()

            # Edge type counts
            metrics['edge_counts'] = edge_counts
            metrics['graph_density'] = nx.density(graph.graph) if len(graph.graph.nodes) > 0 else 0.0

            # Network centrality
            if hasattr(model, '_agent_lookup') and model._agent_lookup:
                agent_ids = list(model._agent_lookup.keys())
                if agent_ids:
                    metrics['avg_centrality'] = sum(
                        MetricsCalculator.calculate_network_centrality(aid, graph.graph)
                        for aid in agent_ids
                    ) / len(agent_ids)

            # General equivalent concentration
            metrics['general_equivalent_concentration'] = MetricsCalculator.calculate_general_equivalent_concentration(
                graph.graph
            )

            # Fetishism index
            metrics['fetishism_index'] = MetricsCalculator.calculate_fetishism_index(graph.graph)

            # Residence ratio (地缘关系比例)
            metrics['residence_ratio'] = MetricsCalculator.calculate_residence_ratio(edge_counts)
            metrics['kinship_ratio'] = 1.0 - metrics['residence_ratio']

        # Political regime metrics
        if hasattr(model, 'political_regime'):
            pr = model.political_regime
            metrics['regime_type'] = pr.regime_type
            metrics['suffrage_level'] = pr.suffrage_level
            metrics['legal_formal_equality'] = MetricsCalculator.calculate_legal_formal_equality(pr.regime_type)
            metrics['property_rights_protection'] = MetricsCalculator.calculate_property_rights_protection(pr.regime_type)
            metrics['repression_level'] = MetricsCalculator.calculate_repression_level(pr.regime_type)

        # State apparatus metrics
        if hasattr(model, 'state_apparatus'):
            sa = model.state_apparatus
            metrics['state_repression_capacity'] = MetricsCalculator.calculate_state_repression_capacity(sa)
            metrics['fiscal_capacity'] = MetricsCalculator.calculate_fiscal_capacity(sa)
            metrics['state_form'] = sa.state_form
            metrics['ruling_class'] = sa.ruling_class

        # Ideology metrics
        if hasattr(model, 'ideology_manager'):
            im = model.ideology_manager
            metrics['legitimacy_score'] = MetricsCalculator.calculate_legitimacy_score(im)
            metrics['cultural_hegemony_strength'] = MetricsCalculator.calculate_cultural_hegemony_strength(im)
            metrics['ideology_content'] = im.ideology_content
            metrics['avg_class_consciousness'] = sum(im.class_consciousness_by_class.values()) / len(im.class_consciousness_by_class)

        # Calculate derived political metrics
        metrics['political_legitimacy_index'] = metrics.get('legitimacy_score', 0.5)
        metrics['cultural_hegemony_index'] = metrics.get('cultural_hegemony_strength', 0.5)

        return metrics


# Import networkx for graph metrics
import networkx as nx