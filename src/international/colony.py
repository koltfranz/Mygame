"""
Colony - 殖民地

Models colonial extraction:
- Precious metal extraction (贵金属掠夺)
- Plantation slavery (种植园奴隶制)
- Settler colonialism (移民殖民地)
- Commodity dumping (商品倾销)
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ColonialExtractionMetrics:
    """殖民榨取指标"""
    precious_metals_extracted: float
    plantation_output: float
    raw_materials_extracted: float
    commodities_dumped: float
    resistance_intensity: float


class Colony:
    """
    殖民地 - Colony model.

    Colonial extraction is a form of unequal exchange where
    raw materials flow one direction and manufactured goods flow another.
    """

    def __init__(self, mother_country_id: int):
        self.mother_country_id = mother_country_id
        self.colony_type = "plantation"  # plantation, mining, settler, dumping

        self.extraction_rate = 0.3  # What proportion of surplus is extracted
        self.resistance_intensity = 0.0  # Grows over time

        self.history: List[Dict] = []

    def extract_surplus(self, colony_agents: List, model) -> Dict[str, float]:
        """
        榨取剩余 - Extract surplus from colony.

        Returns extraction results.
        """
        total_surplus = 0.0
        precious_metals = 0.0
        raw_materials = 0.0

        for agent in colony_agents:
            # Surplus is extracted based on extraction rate
            agent_surplus = len(agent.commodity_inventory) * 0.5 * self.extraction_rate

            # Transfer surplus to mother country
            if model.get_agent(self.mother_country_id):
                mother = model.get_agent(self.mother_country_id)
                for _ in range(int(agent_surplus)):
                    if agent.commodity_inventory:
                        matter = agent.commodity_inventory.pop()
                        mother.add_commodity(matter)

            total_surplus += agent_surplus

        # Update resistance
        self.resistance_intensity = min(1.0, self.resistance_intensity + 0.05)

        result = {
            'total_surplus': total_surplus,
            'precious_metals': precious_metals,
            'raw_materials': raw_materials,
            'resistance': self.resistance_intensity,
        }

        self.history.append(result)
        return result

    def check_independence_movement(self) -> bool:
        """
        检查独立运动 - Check for independence movement.

        Triggers when:
        1. Extraction has been ongoing for long
        2. Resistance intensity is high
        3. Mother country is in crisis
        """
        if len(self.history) < 20:
            return False

        # Calculate trend
        recent_resistance = sum(h['resistance'] for h in self.history[-10:]) / 10
        past_resistance = sum(h['resistance'] for h in self.history[:10]) / 10

        # Independence if resistance has grown significantly
        return (recent_resistance - past_resistance) > 0.5 and self.resistance_intensity > 0.7


class ColonialSystem:
    """
    殖民系统 - Colonial system manager.

    Manages multiple colonies and colonial relationships.
    """

    def __init__(self):
        self.colonies: List[Colony] = []
        self.colonial_powers: List[int] = []  # Agent IDs of colonial powers

    def establish_colony(self, mother_country_id: int, colony_type: str = "plantation") -> Colony:
        """建立殖民地"""
        colony = Colony(mother_country_id)
        colony.colony_type = colony_type
        self.colonies.append(colony)

        if mother_country_id not in self.colonial_powers:
            self.colonial_powers.append(mother_country_id)

        return colony

    def get_total_extraction(self) -> Dict[str, float]:
        """获取总榨取量"""
        totals = {
            'total_surplus': 0.0,
            'precious_metals': 0.0,
            'raw_materials': 0.0,
        }

        for colony in self.colonies:
            if colony.history:
                last = colony.history[-1]
                totals['total_surplus'] += last['total_surplus']
                totals['precious_metals'] += last['precious_metals']
                totals['raw_materials'] += last['raw_materials']

        return totals