"""
State Apparatus - 国家机器

Represents the repressive state apparatus:
- Repression capacity
- Fiscal capacity
- Administrative capacity
"""

from typing import Dict, List


class StateApparatus:
    """
    国家机器 - State apparatus.

    The state is not a "thing" but a relationship of domination.
    It maintains class rule through both repression and consent.
    """

    def __init__(self):
        self.repression_capacity = 0.5  # 0.0 to 1.0
        self.fiscal_capacity = 0.5
        self.administrative_capacity = 0.3

        # Class character of the state
        self.ruling_class = "none"
        self.state_form = "tribal"  # tribal -> slave -> feudal -> bourgeois -> socialist

        # Current mode of production
        self.modes_supported = ["primitive_communal"]

    def apply_repression(self, target_population: float) -> float:
        """
        应用镇压 - Apply repression.

        Returns the level of control exercised.
        """
        if self.repression_capacity < 0.3:
            return 0.0

        # Effectiveness depends on administrative capacity
        effectiveness = self.repression_capacity * self.administrative_capacity
        return effectiveness * target_population

    def collect_tribute(self, population: float) -> float:
        """
        收取贡赋 - Collect tribute/taxes.

        Returns total collected.
        """
        # Fiscal capacity determines how efficiently tribute is collected
        return population * self.fiscal_capacity * 0.1

    def check_state_form_transition(self, mode_of_production: str) -> str:
        """检查国家形式是否需要转换"""
        form_map = {
            "primitive_communal": "tribal",
            "slave_society": "slave_holding",
            "feudalism": "feudal",
            "capitalism": "bourgeois",
            "socialism": "workers",
        }
        new_form = form_map.get(mode_of_production, self.state_form)

        if new_form != self.state_form:
            self.state_form = new_form
            self._update_capacities()

        return self.state_form

    def _update_capacities(self):
        """更新国家能力"""
        capacity_map = {
            "tribal": (0.2, 0.2, 0.1),
            "slave_holding": (0.5, 0.4, 0.3),
            "feudal": (0.4, 0.5, 0.4),
            "bourgeois": (0.6, 0.7, 0.6),
            "workers": (0.3, 0.6, 0.7),
        }
        capacities = capacity_map.get(self.state_form, (0.5, 0.5, 0.5))
        self.repression_capacity, self.fiscal_capacity, self.administrative_capacity = capacities