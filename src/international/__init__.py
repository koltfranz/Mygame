"""
International Module - 国际模块

Includes:
- Foreign market (外部市场)
- Colony (殖民地)
- Trade router (贸易路由)
"""

from .foreign_market import ForeignMarket
from .colony import Colony
from .trade_router import TradeRouter

__all__ = ['ForeignMarket', 'Colony', 'TradeRouter']