"""
War Event - 战争事件

Models wars as:
- Crisis outlets (消耗过剩资本)
- Means of conquest (征服手段)
- Forces of destruction (毁灭力量)
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class WarEvent:
    """战争事件"""
    war_id: int
    participants: List[int]  # Agent IDs
    opposing_sides: Tuple[List[int], List[int]]
    duration: int  # In simulation steps
    intensity: float  # 0.0-1.0
    destruction_caused: float  # Value destroyed


class WarEngine:
    """
    战争引擎 - War engine.

    Wars are not "mistakes" - they are structural outcomes of
    inter-capitalist competition and crisis management.
    """

    def __init__(self):
        self.active_wars: List[WarEvent] = []
        self.war_history: List[WarEvent] = []

    def start_war(self, side_a: List[int], side_b: List[int], intensity: float = 0.5) -> WarEvent:
        """开始战争"""
        war = WarEvent(
            war_id=len(self.war_history),
            participants=side_a + side_b,
            opposing_sides=(side_a, side_b),
            duration=10,
            intensity=intensity,
            destruction_caused=0.0
        )
        self.active_wars.append(war)
        return war

    def simulate_war_step(self, model) -> Dict:
        """
        模拟战争步骤 - Simulate one step of war.

        Wars destroy capital (machines, factories, infrastructure).
        This can be an "external outlet" for crisis.
        """
        results = {
            'wars_fought': len(self.active_wars),
            'total_destruction': 0.0,
            'soldiers_killed': 0,
        }

        for war in self.active_wars[:]:
            # Calculate destruction
            destruction = war.intensity * war.duration * 10.0
            war.destruction_caused = destruction
            results['total_destruction'] += destruction

            # Casualties
            casualties = int(war.intensity * 5)
            results['soldiers_killed'] += casualties

            # Reduce war duration
            war.duration -= 1

            # End war if duration exhausted
            if war.duration <= 0:
                self.active_wars.remove(war)
                self.war_history.append(war)

        return results

    def check_war_breach(self, model, threshold: float = 0.3) -> List[Tuple[List[int], List[int]]]:
        """
        检查战争触发 - Check if conditions for war are met.

        Wars break out when:
        1. Profit rate is falling
        2. Overproduction is severe
        3. Markets are saturated
        """
        crisis = model.reproduction_engine.crisis_indicators

        # Profit rate falling creates war motivation
        if crisis.get('rate_of_profit', 0.5) < threshold:
            # Find agents with high capital (potential war parties)
            potential_aggressors = [
                a.unique_id for a in model._agent_lookup.values()
                if hasattr(a, 'capital_stock') and a.capital_stock > 50
            ]

            if len(potential_aggressors) >= 2:
                mid = len(potential_aggressors) // 2
                return [(potential_aggressors[:mid], potential_aggressors[mid:])]

        return []

    def calculate_war_profitability(self, winner_id: int, model) -> float:
        """计算战争收益"""
        winner = model.get_agent(winner_id)

        if not winner:
            return 0.0

        # War profits = seized territory + captured resources - military costs
        if hasattr(winner, 'capital_stock'):
            war_profits = len(self.active_wars) * 5.0
            return war_profits

        return 0.0