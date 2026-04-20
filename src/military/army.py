"""
Army - 军队

Models military forces as part of the repressive state apparatus.
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class MilitaryUnit:
    """军事单位"""
    unit_id: int
    unit_type: str  # infantry, cavalry, artillery, militia
    size: int  # Number of soldiers
    organization: float  # 0.0-1.0, affects combat effectiveness
    morale: float  # 0.0-1.0
    equipment_level: float  # 0.0-1.0


class Army:
    """
    军队 - Army model.

    Military is the core of the repressive state apparatus.
    Military spending consumes surplus-value.
    """

    def __init__(self):
        self.units: List[MilitaryUnit] = []
        self.total_size = 0
        self.military_budget = 0.0  # Surplus consumed by military
        self.upkeep_cost_per_soldier = 2.0  # Value equivalent per soldier

    def recruit_unit(self, unit_type: str, size: int, equipment_level: float = 0.5) -> MilitaryUnit:
        """招募单位"""
        unit = MilitaryUnit(
            unit_id=len(self.units),
            unit_type=unit_type,
            size=size,
            organization=0.6,
            morale=0.7,
            equipment_level=equipment_level
        )
        self.units.append(unit)
        self.total_size += size
        return unit

    def calculate_upkeep(self) -> float:
        """计算军事维护费用"""
        total_upkeep = self.total_size * self.upkeep_cost_per_soldier

        # Equipment depreciation
        for unit in self.units:
            total_upkeep += unit.size * unit.equipment_level * 0.5

        self.military_budget = total_upkeep
        return total_upkeep

    def check_desertion(self) -> List[MilitaryUnit]:
        """检查逃兵"""
        deserters = []

        for unit in self.units:
            # High casualty rate or low morale increases desertion
            if unit.morale < 0.3 or unit.organization < 0.4:
                deserters.append(unit)

        # Remove deserters
        for deserter in deserters:
            self.units.remove(deserter)
            self.total_size -= deserter.size

        return deserters

    def calculate_combat_effectiveness(self) -> float:
        """计算战斗力"""
        if not self.units:
            return 0.0

        total_power = 0.0
        for unit in self.units:
            # Combat power = size * equipment * organization * morale
            unit_power = unit.size * unit.equipment_level * unit.organization * unit.morale
            total_power += unit_power

        return total_power

    def absorb_military_industrial_complex(self, defense_industry) -> float:
        """吸收军事工业复合体产出"""
        # Military consumes defense industry output
        military_consumption = min(
            defense_industry.output_capacity * 0.8,
            self.military_budget
        )
        return military_consumption