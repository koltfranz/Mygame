"""
Value Form Analysis - 价值形式分析工具

For analyzing value form topology and emergence patterns.
"""

import networkx as nx
from typing import Dict, List, Tuple
import numpy as np


class ValueFormAnalyzer:
    """
    价值形式分析器 - Analyzes value form emergence and topology.

    Tracks:
    - Network centrality of commodities
    - Value form stage transitions
    - Exchange ratio evolution
    """

    def __init__(self):
        self.commodity_nodes: Dict[str, Dict] = {}
        self.exchange_edges: List[Tuple[str, str, float]] = []

    def add_exchange(self, commodity_a: str, commodity_b: str, quantity_a: float, quantity_b: float):
        """记录交换"""
        self.exchange_edges.append((commodity_a, commodity_b, quantity_b / max(quantity_a, 0.1)))

        # Update commodity nodes
        if commodity_a not in self.commodity_nodes:
            self.commodity_nodes[commodity_a] = {'exchange_count': 0, 'total_out': 0}
        if commodity_b not in self.commodity_nodes:
            self.commodity_nodes[commodity_b] = {'exchange_count': 0, 'total_in': 0}

        self.commodity_nodes[commodity_a]['exchange_count'] += 1
        self.commodity_nodes[commodity_a]['total_out'] += quantity_a
        self.commodity_nodes[commodity_b]['total_in'] += quantity_b

    def calculate_commodity_centrality(self) -> Dict[str, float]:
        """
        计算商品中心性 - Calculate commodity centrality in exchange network.

        Higher centrality = more likely to become universal equivalent.
        """
        if not self.exchange_edges:
            return {}

        # Build network
        G = nx.Graph()
        for a, b, ratio in self.exchange_edges:
            if G.has_edge(a, b):
                G[a][b]['weight'] += ratio
            else:
                G.add_edge(a, b, weight=ratio)

        if len(G.nodes) == 0:
            return {}

        # Calculate degree centrality weighted by exchange volume
        centrality = {}
        for node in G.nodes:
            degree = G.degree(node, weight='weight')
            centrality[node] = degree / max(sum(G.degree(n, weight='weight') for n in G.nodes), 0.1)

        return centrality

    def detect_money_commodity(self) -> Tuple[bool, str]:
        """
        检测货币商品 - Detect if a commodity has emerged as money.

        Conditions:
        1. Highest centrality
        2. Appears in >50% of exchanges
        3. Acts as numeraire in ratios
        """
        centrality = self.calculate_commodity_centrality()

        if not centrality:
            return False, ""

        # Find highest centrality commodity
        money_candidate = max(centrality, key=centrality.get)

        # Check if it appears in >50% of exchanges
        if not self.exchange_edges:
            return False, ""

        money_appearances = sum(1 for a, b, _ in self.exchange_edges if a == money_candidate or b == money_candidate)
        appearance_ratio = money_appearances / len(self.exchange_edges)

        if appearance_ratio > 0.5 and centrality[money_candidate] > 0.3:
            return True, money_candidate

        return False, ""

    def get_value_form_metrics(self) -> Dict:
        """获取价值形式指标"""
        centrality = self.calculate_commodity_centrality()
        is_money, money_commodity = self.detect_money_commodity()

        return {
            'unique_commodities': len(self.commodity_nodes),
            'total_exchanges': len(self.exchange_edges),
            'commodity_centrality': centrality,
            'is_money_emerged': is_money,
            'money_commodity': money_commodity if is_money else None,
            'avg_exchange_ratio': np.mean([r for _, _, r in self.exchange_edges]) if self.exchange_edges else 1.0,
        }