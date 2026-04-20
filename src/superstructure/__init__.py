"""
Superstructure Module - 上层建筑模块

Includes:
- State apparatus (国家机器)
- Legal system (法律体系)
- Ideology manager (意识形态)
- Political regime (政治体制)
"""

from .state_apparatus import StateApparatus
from .legal_system import LegalSystem, PropertyLaw, ContractLaw, LaborLaw
from .ideology_manager import IdeologyManager
from .political_regime import PoliticalRegime

__all__ = [
    'StateApparatus',
    'LegalSystem', 'PropertyLaw', 'ContractLaw', 'LaborLaw',
    'IdeologyManager',
    'PoliticalRegime',
]