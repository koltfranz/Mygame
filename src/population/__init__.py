"""
Population Module - 人口动态

Includes:
- Demography (人口统计)
- Class reproduction (阶级再生产)
- Migration (移民)
"""

from .demography import DemographyEngine, FertilityCalculator, MortalityCalculator
from .migration import MigrationEngine

__all__ = ['DemographyEngine', 'FertilityCalculator', 'MortalityCalculator', 'MigrationEngine']