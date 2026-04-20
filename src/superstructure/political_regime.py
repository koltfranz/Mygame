"""
Political Regime - 政治体制

Determines:
- Type of regime (monarchy, democracy, etc.)
- How regime type is determined by class forces
"""

from typing import List, Dict


class PoliticalRegime:
    """
    政治体制 - Political regime.

    Political form is determined by the relation of class forces,
    not by "political culture" or "individual preferences".
    """

    def __init__(self):
        self.regime_type = "tribal"  # tribal, slave_monarchy, feudal, bourgeois_democracy, workers_democracy
        self.suffrage_level = 0.1  # What % of population can vote

        # Class representation
        self.class_representation = {
            "ruling_class": 1.0,  # Proportion of political power
            "subordinate_class": 0.0,
        }

    def determine_regime(self, class_forces: Dict[str, float], mode_of_production: str) -> str:
        """
        判定政治体制 - Determine regime type based on class forces.

        class_forces: dict mapping class to relative strength (0.0-1.0)
        """
        if mode_of_production == "primitive_communal":
            self.regime_type = "tribal"
            self.suffrage_level = 1.0  # All adults in tribe
            self.class_representation = {"tribal_collective": 1.0}

        elif mode_of_production == "slave_society":
            slave_strength = class_forces.get("slave", 0.0)
            owner_strength = class_forces.get("slave_owner", 1.0)

            if owner_strength > 0.8:
                self.regime_type = "slave_monarchy"
                self.suffrage_level = 0.1  # Only slave owners
            else:
                self.regime_type = "slave_aristocracy"
            self.class_representation = {"slave_owner": 0.9, "slave": 0.1}

        elif mode_of_production == "feudalism":
            self.regime_type = "feudal_monarchy"
            self.suffrage_level = 0.2
            self.class_representation = {"lord": 0.8, "serf": 0.2}

        elif mode_of_production == "capitalism":
            self.regime_type = "bourgeois_democracy"
            self.suffrage_level = 0.5  # Property qualifications
            self.class_representation = {"capitalist": 0.7, "worker": 0.3}

        elif mode_of_production == "socialism":
            self.regime_type = "workers_democracy"
            self.suffrage_level = 1.0
            self.class_representation = {"worker": 0.9, "manager": 0.1}

        return self.regime_type

    def apply_regime_effects(self, model) -> Dict:
        """
        应用政治体制效果 - Apply effects of regime on society.

        Returns dict of regime effects.
        """
        effects = {
            'tax_rate': self._calculate_tax_rate(),
            'repression_level': self._calculate_repression(),
            'property_rights': self._calculate_property_rights(),
        }
        return effects

    def _calculate_tax_rate(self) -> float:
        """计算税率"""
        rate_map = {
            "tribal": 0.05,
            "slave_monarchy": 0.15,
            "feudal_monarchy": 0.2,
            "bourgeois_democracy": 0.25,
            "workers_democracy": 0.3,
        }
        return rate_map.get(self.regime_type, 0.1)

    def _calculate_repression(self) -> float:
        """计算镇压水平"""
        if self.regime_type in ["tribal", "workers_democracy"]:
            return 0.2
        elif self.regime_type in ["feudal_monarchy", "slave_monarchy"]:
            return 0.7
        else:
            return 0.5

    def _calculate_property_rights(self) -> float:
        """计算财产权保护"""
        if self.regime_type == "workers_democracy":
            return 0.6
        elif self.regime_type == "bourgeois_democracy":
            return 0.9
        else:
            return 0.5