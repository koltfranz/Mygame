"""
Demography - 人口动态

Handles population dynamics:
- Fertility rates (生育率)
- Mortality rates (死亡率)
- Population structure
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PopulationMetrics:
    """人口指标"""
    total_population: int
    birth_rate: float
    death_rate: float
    growth_rate: float
    total_fertility_rate: float
    infant_mortality_rate: float


class FertilityCalculator:
    """
    生育率计算器 - Calculates fertility based on class position and conditions.

    Following the Marxist demographic transition model:
    - Proletarian fertility: High when subsistence is low
    - Bourgeois fertility: Lower, more controlled
    """

    @staticmethod
    def calculate_fertility_rate(agent, class_position: str, crisis_level: float = 0.0) -> float:
        """
        计算生育率 - Calculate fertility rate.

        RED LINE: Fertility is NOT determined by "preferences" or "culture".
        It is determined by material conditions and class position.
        """
        base_fertility = 4.0  # Maximum children per woman

        if class_position == "worker":
            # Workers have higher fertility when:
            # - Subsistence satisfaction is low
            # - Unemployment is high (no need to invest in children's education)
            if agent.subsistence_satisfaction < 0.6:
                return base_fertility * 1.2
            elif agent.subsistence_satisfaction < 0.8:
                return base_fertility * 0.9
            else:
                return base_fertility * (1.0 - 0.3 * agent.education_invested / 10.0)

        elif class_position == "capitalist":
            # Capitalists have lower fertility (higher investment per child)
            return 3.0

        elif class_position in ["serf", "slave"]:
            # Exploited classes have high fertility (children = labor power)
            return base_fertility

        else:
            # Foragers and tribe members
            return base_fertility * 0.8

        return base_fertility


class MortalityCalculator:
    """
    死亡率计算器 - Calculates mortality based on conditions.
    """

    @staticmethod
    def calculate_mortality_rate(agent, class_position: str,
                                  healthcare_access: float = 0.5) -> float:
        """
        计算死亡率 - Calculate mortality rate.

        Mortality is higher for lower classes due to:
        - Worse nutrition
        - Worse healthcare
        - More dangerous working conditions
        """
        base_mortality = 0.02  # Base rate per step

        # Class determines mortality
        class_mortality = {
            "capitalist": 0.01,
            "lord": 0.015,
            "worker": 0.03,
            "serf": 0.035,
            "slave": 0.05,
            "forager": 0.04,
            "tribe_member": 0.03,
        }

        mortality = class_mortality.get(class_position, base_mortality)

        # Subsistence affects mortality
        if agent.subsistence_satisfaction < 0.5:
            mortality *= 2.0
        elif agent.subsistence_satisfaction < 0.3:
            mortality *= 3.0

        # Healthcare access reduces mortality
        mortality *= (1.0 - healthcare_access * 0.5)

        return mortality


class DemographyEngine:
    """
    人口引擎 - Manages population dynamics.
    """

    def __init__(self):
        self.population_history: List[int] = []

    def calculate_population_change(self, agents: List, model) -> Tuple[int, int]:
        """
        计算人口变化 - Calculate population change.

        Returns (births, deaths)
        """
        births = 0
        deaths = 0

        # Estimate women of childbearing age (simplified: 40% of population)
        fertile_agents = [a for a in agents if hasattr(a, 'subsistence_satisfaction')]

        for agent in fertile_agents[:len(fertile_agents)//2]:  # Approximate women
            class_pos = model.social_graph.infer_class_position(agent.unique_id)

            # Calculate fertility
            fertility = FertilityCalculator.calculate_fertility_rate(
                agent, class_pos,
                model.reproduction_engine.crisis_indicators.get('department_imbalance', 0.0)
            )

            # Stochastic birth (simplified)
            if agent.subsistence_satisfaction > 0.6 and model.random.random() < fertility / 50.0:
                births += 1

            # Calculate mortality
            mortality = MortalityCalculator.calculate_mortality_rate(
                agent, class_pos, 0.5
            )

            if agent.subsistence_satisfaction <= 0:
                deaths += 1
            elif model.random.random() < mortality:
                deaths += 1

        return births, deaths

    def get_population_metrics(self, agents: List, births: int, deaths: int) -> PopulationMetrics:
        """获取人口指标"""
        total_pop = len(agents)

        return PopulationMetrics(
            total_population=total_pop,
            birth_rate=births / max(total_pop, 1),
            death_rate=deaths / max(total_pop, 1),
            growth_rate=(births - deaths) / max(total_pop, 1),
            total_fertility_rate=4.0,  # Simplified
            infant_mortality_rate=0.1,  # Simplified
        )