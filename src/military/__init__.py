"""
Military Module - 军事模块

Includes:
- Army (军队)
- Defense industry (国防工业)
- War events (战争事件)
"""

from .army import Army, MilitaryUnit
from .war_event import WarEvent, WarEngine

__all__ = ['Army', 'MilitaryUnit', 'WarEvent', 'WarEngine']