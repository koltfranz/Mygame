"""
Value Form Router - 价值形式路由器

Implements the emergence of value forms through exchange:
- Simple/barter value form (物物交换)
- Expanded value form (扩大价值形式)
- Universal/general value form (一般价值形式)
- Money form (货币形式)

The impedance routing network determines which commodity becomes the universal equivalent.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import networkx as nx


class ImpedanceRouter:
    """
    价值形式阻抗路由 - Value form impedance router.

    Determines exchange paths and which commodity emerges as universal equivalent.
    Based on social relation graph topology and exchange history.

    RED LINE: Universal equivalent (money) EMERGES from network topology,
    NOT from any intrinsic property of the commodity.
    Detection is based on in-degree centrality > 80%.
    """

    def __init__(self, social_graph):
        self.social_graph = social_graph
        self.exchange_history: List[Tuple[int, int, str, float]] = []  # (from, to, commodity, ratio)
        self.value_form_stage = "barter"  # barter -> expanded -> universal -> money
        self.universal_equivalent: Optional[str] = None
        self.exchange_ratios: Dict[str, Dict[str, float]] = {}  # commodity1 -> commodity2 -> ratio
        # 入度中心性跟踪 - 用于一般等价物涌现检测
        self._in_degree_history: Dict[str, List[float]] = {}  # commodity -> [centrality_values]
        self._consecutive_high_centrality: Dict[str, int] = {}  # commodity -> consecutive_steps
        self._centrality_threshold: float = 0.8  # 入度中心性 > 80% 触发货币涌现

    def record_exchange(self, from_agent: int, to_agent: int, commodity_type: str, quantity: float):
        """记录交换"""
        self.exchange_history.append((from_agent, to_agent, commodity_type, quantity))
        self._update_exchange_ratio(commodity_type)

    def _update_exchange_ratio(self, commodity_type: str):
        """更新交换比例"""
        # Calculate exchange ratio based on SNLT
        from src.engine.labor_value import SNLTCalculator

        if commodity_type not in self.exchange_ratios:
            self.exchange_ratios[commodity_type] = {}

        # Simple ratio based on labor time
        snlt = SNLTCalculator.get_snlt(commodity_type)
        for other_type in self.exchange_ratios:
            if other_type != commodity_type:
                other_snlt = SNLTCalculator.get_snlt(other_type)
                if other_snlt > 0:
                    self.exchange_ratios[commodity_type][other_type] = snlt / other_snlt
                    self.exchange_ratios[other_type][commodity_type] = other_snlt / snlt

    def calculate_exchange_path(self, from_agent: int, to_agent: int, commodity: str) -> List[int]:
        """
        计算交换路径 - Calculate optimal exchange path through the network.

        Returns list of agent IDs forming the path.
        """
        try:
            path = nx.shortest_path(self.social_graph.graph, from_agent, to_agent)
            return path
        except nx.NetworkXError:
            return [from_agent, to_agent]

    def determine_value_form_stage(self) -> str:
        """
        判定价值形式阶段 - Determine current value form stage.

        Evolution:
        1. Barter: direct exchange between two agents
        2. Expanded: multiple commodities in exchange
        3. Universal: one commodity becomes general equivalent
        4. Money: one commodity becomes universal equivalent (money commodity)

        RED LINE: Universal equivalent detection uses in-degree centrality > 80%.
        No a priori designation of "money commodity" - it EMERGES from exchange topology.
        """
        unique_commodities = set(c for _, _, c, _ in self.exchange_history)
        exchange_pairs = len(self.exchange_history)

        # 1. Calculate in-degree centrality for each commodity from exchange history
        #    A commodity's centrality = how many distinct agents hold it / total agents
        self._calculate_in_degree_centrality()

        # 2. Check for universal equivalent emergence via centrality > 80%
        for commodity, centrality in self._in_degree_history.items():
            if not centrality:
                continue
            latest_centrality = centrality[-1]
            if latest_centrality >= self._centrality_threshold:
                self._consecutive_high_centrality[commodity] = \
                    self._consecutive_high_centrality.get(commodity, 0) + 1
                # 持续高于阈值才认定为一般等价物
                if self._consecutive_high_centrality[commodity] >= 3:
                    self.value_form_stage = "money"
                    self.universal_equivalent = commodity
                    return self.value_form_stage
            else:
                self._consecutive_high_centrality[commodity] = 0

        # 3. Fallback: determine stage from exchange volume
        if len(unique_commodities) > 5 and exchange_pairs > 10:
            self.value_form_stage = "universal"
            self._elect_universal_equivalent_by_volume()
        elif len(unique_commodities) > 2:
            self.value_form_stage = "expanded"
        else:
            self.value_form_stage = "barter"

        return self.value_form_stage

    def _calculate_in_degree_centrality(self):
        """
        计算各商品类型的入度中心性。

        入度中心性 = 持有该商品的agent数量 / 所有参与交换的agent数量。
        当某商品的入度中心性 > 80%，它已成为事实上的一般等价物。
        """
        if not self.exchange_history:
            return

        agents_in_exchange = set()
        commodity_holders: Dict[str, set] = {}
        for from_agent, to_agent, c, _ in self.exchange_history:
            agents_in_exchange.add(from_agent)
            agents_in_exchange.add(to_agent)
            if c not in commodity_holders:
                commodity_holders[c] = set()
            commodity_holders[c].add(from_agent)
            commodity_holders[c].add(to_agent)

        total_agents = len(agents_in_exchange)
        if total_agents == 0:
            return

        for commodity, holders in commodity_holders.items():
            centrality = len(holders) / total_agents
            if commodity not in self._in_degree_history:
                self._in_degree_history[commodity] = []
            self._in_degree_history[commodity].append(centrality)

    def _elect_universal_equivalent_by_volume(self):
        """选举一般等价物（按交换量）"""
        commodity_counts: Dict[str, int] = {}
        for _, _, c, _ in self.exchange_history:
            commodity_counts[c] = commodity_counts.get(c, 0) + 1

        if commodity_counts:
            self.universal_equivalent = max(commodity_counts, key=commodity_counts.get)

    def get_exchange_ratio(self, commodity_a: str, commodity_b: str) -> float:
        """获取交换比例"""
        if commodity_a in self.exchange_ratios:
            if commodity_b in self.exchange_ratios[commodity_a]:
                return self.exchange_ratios[commodity_a][commodity_b]

        # Default to SNLT ratio
        from src.engine.labor_value import SNLTCalculator
        snlt_a = SNLTCalculator.get_snlt(commodity_a)
        snlt_b = SNLTCalculator.get_snlt(commodity_b)

        if snlt_b > 0:
            return snlt_a / snlt_b
        return 1.0

    def convert_to_universal_equivalent(self, commodity_type: str, quantity: float) -> Tuple[str, float]:
        """
        将商品转换为一般等价物形式 - Convert commodity to universal equivalent form.

        Returns (universal_type, converted_quantity)
        """
        if self.universal_equivalent:
            ratio = self.get_exchange_ratio(commodity_type, self.universal_equivalent)
            return (self.universal_equivalent, quantity * ratio)
        return (commodity_type, quantity)