"""
Trade Router - 贸易路由

Handles:
- Trade route establishment
- Trade barrier calculation
- Balance of trade
"""

from typing import Dict, List, Tuple


class TradeRouter:
    """
    贸易路由 - Trade router.

    Trade routes emerge based on:
    1. Geographic proximity
    2. Social relation graph topology
    3. Political barriers
    """

    def __init__(self):
        self.routes: Dict[Tuple[int, int], float] = {}  # (from, to) -> impedance
        self.trade_balance: Dict[int, float] = {}  # Agent ID -> balance of trade
        self.tariffs: Dict[int, float] = {}  # Agent ID -> tariff rate

    def calculate_route_impedance(self, from_id: int, to_id: int, social_graph) -> float:
        """
        计算路线阻抗 - Calculate route impedance.

        Lower impedance = easier trade.
        """
        # Start with geographic distance (normalized)
        base_impedance = 1.0

        # Social graph distance adds impedance
        try:
            path_length = len(social_graph.graph.shortest_path(from_id, to_id))
            social_impedance = path_length * 0.5
        except:
            social_impedance = 10.0  # No path exists

        # Apply tariffs
        tariff = self.tariffs.get(to_id, 0.0)

        total_impedance = base_impedance + social_impedance + tariff

        return total_impedance

    def find_best_trade_route(self, from_id: int, commodity_type: str,
                              potential_targets: List[int], social_graph) -> Tuple[int, float]:
        """
        找到最佳贸易路线 - Find best trade route.

        Returns (best_target_id, impedance)
        """
        best_target = -1
        best_impedance = float('inf')

        for target_id in potential_targets:
            impedance = self.calculate_route_impedance(from_id, target_id, social_graph)
            if impedance < best_impedance:
                best_impedance = impedance
                best_target = target_id

        return best_target, best_impedance

    def update_trade_balance(self, agent_id: int, export_value: float, import_value: float):
        """更新贸易收支"""
        if agent_id not in self.trade_balance:
            self.trade_balance[agent_id] = 0.0

        self.trade_balance[agent_id] += export_value - import_value

    def apply_tariff(self, agent_id: int, tariff_rate: float):
        """应用关税"""
        self.tariffs[agent_id] = tariff_rate

    def get_trade_metrics(self, agent_id: int) -> Dict[str, float]:
        """获取贸易指标"""
        balance = self.trade_balance.get(agent_id, 0.0)

        return {
            'trade_balance': balance,
            'tariff_rate': self.tariffs.get(agent_id, 0.0),
            'is_surplus': balance > 0,
        }