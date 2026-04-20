"""
Migration - 移民

Handles:
- Rural to urban migration (城乡移民)
- International migration (国际移民)
- Brain drain
"""

from typing import Dict, List, Tuple


class MigrationEngine:
    """
    移民引擎 - Migration engine.

    Migration is NOT random - it follows structural incentives:
    - Wage differentials (工资差异)
    - Land availability (土地可得性)
    - Persecution (迫害)
    """

    def __init__(self):
        self.migration_history: List[Dict] = []

    def calculate_rural_urban_migration(self, agents: List, model) -> List[int]:
        """
        计算城乡移民 - Calculate rural to urban migration.

        Returns list of agent IDs who should migrate.
        """
        migrants = []

        # Find rural and urban agents
        for agent in agents:
            if hasattr(agent, 'skill_type') and agent.skill_type == 'farming':
                # Rural worker
                urban_wage = 10.0  # Expected urban wage
                rural_wage = 5.0    # Rural wage

                # If urban wage > rural wage + migration cost, migrate
                migration_cost = 2.0

                if (urban_wage - rural_wage) > migration_cost:
                    if agent.subsistence_satisfaction > 0.7:  # Only relatively healthy workers migrate
                        # Higher class consciousness increases migration propensity
                        if hasattr(agent, 'class_consciousness'):
                            migration_prob = 0.1 + 0.2 * agent.class_consciousness
                        else:
                            migration_prob = 0.1

                        if model.random.random() < migration_prob:
                            migrants.append(agent.unique_id)

        return migrants

    def calculate_international_migration(self, agents: List, model,
                                          colonial_system) -> List[int]:
        """
        计算国际移民 - Calculate international migration.

        Migration to colonies when:
        1. Mother country has surplus population
        2. Colony needs settlers
        3. Economic opportunities in colony
        """
        migrants = []

        if not colonial_system or not colonial_system.colonies:
            return migrants

        for agent in agents:
            class_pos = model.social_graph.infer_class_position(agent.unique_id)

            # Only workers and poor peasants migrate internationally
            if class_pos not in ['worker', 'serf']:
                continue

            # Check push factors (crisis in home country)
            crisis_level = model.reproduction_engine.crisis_indicators.get('department_imbalance', 0.0)

            # Check pull factors (colony opportunities)
            colony = colonial_system.colonies[0]
            colony_pull = 1.0 - colony.resistance_intensity

            if crisis_level > 0.3 or colony_pull > 0.5:
                if agent.subsistence_satisfaction < 0.6:
                    # Poor workers seek opportunities in colonies
                    if model.random.random() < 0.05:
                        migrants.append(agent.unique_id)

        return migrants

    def apply_migration(self, model, migrant_ids: List[int], destination: str = "urban"):
        """
        应用移民 - Apply migration.

        destination: "urban", "colony", or specific location
        """
        for migrant_id in migrant_ids:
            agent = model.get_agent(migrant_id)
            if not agent:
                continue

            if destination == "urban":
                # Move to urban center
                # For now, just change some attributes
                agent.skill_type = 'industrial'
            elif destination == "colony":
                # Move to colony
                # This would involve assigning to a different model/region
                pass

        self.migration_history.append({
            'destination': destination,
            'count': len(migrant_ids),
            'step': model.schedule.steps if hasattr(model, 'schedule') else 0,
        })

    def get_migration_metrics(self) -> Dict:
        """获取移民指标"""
        if not self.migration_history:
            return {'total_migrants': 0, 'by_destination': {}}

        total = len(self.migration_history)
        by_dest = {}

        for record in self.migration_history:
            dest = record['destination']
            by_dest[dest] = by_dest.get(dest, 0) + record['count']

        return {
            'total_migrants': total,
            'by_destination': by_dest,
        }