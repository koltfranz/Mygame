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
    """

    def __init__(self, social_graph):
        self.social_graph = social_graph
        self.exchange_history: List[Tuple[int, int, str, float]] = []  # (from, to, commodity, ratio)
        self.value_form_stage = "barter"  # barter -> expanded -> universal -> money
        self.universal_equivalent: Optional[str] = None
        self.exchange_ratios: Dict[str, Dict[str, float]] = {}  # commodity1 -> commodity2 -> ratio

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
        """
        unique_commodities = set(c for _, _, c, _ in self.exchange_history)
        exchange_pairs = len(self.exchange_history)

        if len(unique_commodities) == 1 and exchange_pairs > 20:
            self.value_form_stage = "money"
            self.universal_equivalent = list(unique_commodities)[0]
        elif len(unique_commodities) > 5 and exchange_pairs > 10:
            self.value_form_stage = "universal"
            # Most frequently exchanged commodity becomes general equivalent
            self._elect_universal_equivalent()
        elif len(unique_commodities) > 2:
            self.value_form_stage = "expanded"
        else:
            self.value_form_stage = "barter"

        return self.value_form_stage

    def _elect_universal_equivalent(self):
        """选举一般等价物"""
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