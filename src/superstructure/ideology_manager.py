"""
Ideology Manager - 意识形态管理器

Manages:
- Hegemony (霸权)
- Class consciousness (阶级意识)
- Legitimacy (合法性)
"""

from typing import Dict


class IdeologyManager:
    """
    意识形态管理器 - Ideology manager.

    Ideology is not "false consciousness" - it is the material practice
    of lived relations. The ruling class's ideas are the ruling ideas.
    """

    def __init__(self):
        self.hegemony_strength = 0.5  # 0.0 to 1.0
        self.class_consciousness_by_class: Dict[str, float] = {
            "forager": 0.1,
            "tribe_member": 0.2,
            "slave": 0.1,
            "serf": 0.2,
            "worker": 0.3,
        }
        self.legitimacy = 0.7  # Legitimacy of existing order

        # Dominant ideology content
        self.ideology_content = "communal"  # communal, slave, feudal, capitalist, socialist

    def update_hegemony(self, mode_of_production: str, crisis_level: float = 0.0):
        """
        更新霸权强度 - Update hegemony based on mode of production and crisis.

        Hegemony weakens during crises.
        """
        base_hegemony = {
            "primitive_communal": 0.3,
            "slave_society": 0.4,
            "feudalism": 0.5,
            "capitalism": 0.6,
            "socialism": 0.7,
        }

        self.hegemony_strength = base_hegemony.get(mode_of_production, 0.5)

        # Crisis weakens hegemony
        self.hegemony_strength = max(0.1, self.hegemony_strength - crisis_level * 0.5)

        # Update ideology content
        self.ideology_content = mode_of_production

    def spread_ideology(self, agent, model):
        """
        传播意识形态 - Spread ideology to agents.

        Agents absorb dominant ideology based on:
        1. Hegemony strength
        2. Class position
        3. Crisis level
        """
        class_position = model.social_graph.infer_class_position(agent.unique_id)

        # Calculate ideology absorption
        base_consciousness = self.class_consciousness_by_class.get(class_position, 0.2)

        # Crisis increases class consciousness
        crisis_factor = 1.0 + model.reproduction_engine.crisis_indicators.get('department_imbalance', 0.0)

        # Hegemony suppresses class consciousness
        hegemony_suppression = 1.0 - self.hegemony_strength * 0.5

        agent_consciousness = base_consciousness * crisis_factor * hegemony_suppression

        return min(1.0, agent_consciousness)

    def check_legitimacy_crisis(self) -> bool:
        """
        检查合法性危机 - Check for legitimacy crisis.

        Legitimacy crisis occurs when:
        1. Hegemony is weak
        2. Class consciousness is rising
        3. Crisis indicators are high
        """
        avg_consciousness = sum(self.class_consciousness_by_class.values()) / len(self.class_consciousness_by_class)

        legitimacy_crisis = (
            self.hegemony_strength < 0.3 and
            avg_consciousness > 0.4
        )

        if legitimacy_crisis:
            self.legitimacy = max(0.0, self.legitimacy - 0.1)

        return legitimacy_crisis

    def get_hegemony_metrics(self) -> Dict:
        """获取霸权指标"""
        return {
            'hegemony_strength': self.hegemony_strength,
            'legitimacy': self.legitimacy,
            'avg_class_consciousness': sum(self.class_consciousness_by_class.values()) / len(self.class_consciousness_by_class),
            'ideology_content': self.ideology_content,
        }