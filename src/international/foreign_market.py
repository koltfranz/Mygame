"""
Foreign Market - 外部市场

Represents the external market for international exchange.
"""

from typing import Dict, List, Tuple


class ForeignMarket:
    """
    外部市场 - Foreign market.

    International value is determined by taking the lower SNLT
    between domestic and foreign production.
    """

    def __init__(self):
        self.external_snlt: Dict[str, float] = {}  # Commodity type -> SNLT in foreign market
        self.trade_partners: List[int] = []  # Agent IDs of foreign traders
        self.trade_barriers: float = 0.0  # 0.0 = free trade, 1.0 = complete barrier

    def get_external_snlt(self, commodity_type: str) -> float:
        """获取外部SNLT"""
        return self.external_snlt.get(commodity_type, 20.0)  # Default higher than domestic

    def set_external_snlt(self, commodity_type: str, snlt: float):
        """设置外部SNLT"""
        self.external_snlt[commodity_type] = snlt

    def international_exchange(self, domestic_commodity, domestic_snlt: float) -> Tuple[float, float]:
        """
        国际交换 - International exchange.

        Returns (realized_value, super_profit)

        Super-profit occurs when domestic SNLT < foreign SNLT.
        """
        foreign_snlt = self.get_external_snlt(domestic_commodity.physical_props.get('name', 'unknown'))

        # Value is determined by the LOWER SNLT (the socially necessary one)
        realized_value = min(domestic_snlt, foreign_snlt)

        # Super-profit if domestic is more productive
        super_profit = 0.0
        if domestic_snlt < foreign_snlt:
            super_profit = foreign_snlt - domestic_snlt

        return realized_value, super_profit

    def apply_trade_barriers(self, domestic_value: float) -> float:
        """应用贸易壁垒"""
        return domestic_value * (1.0 - self.trade_barriers * 0.5)


class ForeignMarketSimulator:
    """
    外部市场模拟器 - Simulates multiple foreign markets.

    Used when there are multiple trading partners with different SNLT.
    """

    def __init__(self):
        self.markets: List[ForeignMarket] = []

    def add_market(self, market: ForeignMarket):
        """添加市场"""
        self.markets.append(market)

    def get_best_exchange(self, commodity_type: str, domestic_snlt: float) -> Tuple[float, int]:
        """
        获取最佳交换 - Get best exchange opportunity.

        Returns (best_value, market_index)
        """
        best_value = domestic_snlt
        best_market = -1

        for i, market in enumerate(self.markets):
            foreign_snlt = market.get_external_snlt(commodity_type)
            value = min(domestic_snlt, foreign_snlt)

            if value > best_value:
                best_value = value
                best_market = i

        return best_value, best_market