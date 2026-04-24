"""
Sector - 部门类 (技术知识、工具质量、技能要求计算)

Per the development outline:
- tech_knowledge evolves through production volume and R&D investment
- tool_quality reflects mean SNLT of machines in use
- calc_skill_requirement is dynamic, NOT a fixed constant (Red Line 6)
"""

from typing import List, Optional
import numpy as np


class Sector:
    """
    生产部门 - Sector for organizing production.

    Tracks:
    - tech_knowledge (技术知识)
    - tool_quality (工具质量)
    - avg_worker_skill (平均劳动技能)
    - accumulated output for learning curve
    """

    def __init__(self, name: str, commodity_type: str, initial_config: dict = None):
        self.name = name
        self.commodity_type = commodity_type

        config = initial_config or {}
        self.tech_knowledge = config.get('tech_knowledge', 1.0)
        self.tool_quality = config.get('tool_quality', 1.0)
        self.avg_worker_skill = config.get('avg_worker_skill', 1.0)
        self.accumulated_output = 0.0

    def step(self, production_volume: float, r_and_d_investment: float,
             machines_in_use: List = None):
        """
        部门步进进化 - Step evolution of sector knowledge.

        Per outline spec:
        tech_knowledge += production_volume * LEARNING_RATE + r_and_d_investment * R_AND_D_EFFICIENCY
        tool_quality = mean SNLT of machines in use
        """
        from src.model.ontology import Matter

        # Tech knowledge evolves through learning by doing and R&D
        learning_rate = 0.001
        r_and_d_efficiency = 0.05
        self.tech_knowledge += production_volume * learning_rate + r_and_d_investment * r_and_d_efficiency

        # Tool quality reflects mean SNLT of machines in use
        if machines_in_use:
            machine_values = []
            for m in machines_in_use:
                if hasattr(m, 'individual_labor_embodied'):
                    machine_values.append(m.individual_labor_embodied)
            if machine_values:
                self.tool_quality = np.mean(machine_values)

        # Track accumulated output for learning curve effects
        self.accumulated_output += production_volume

        # Smooth update avg worker skill (simplified: slow mean reversion)
        # In real simulation, this is driven by workforce composition changes
        self.avg_worker_skill = max(1.0, self.avg_worker_skill * 0.99 + 0.01 * self.tech_knowledge)

    def calc_skill_requirement(self) -> float:
        """
        动态计算技能要求 - Calculate skill requirement dynamically.

        RED LINE 6: NOT a preset constant.
        Formula from outline:
        raw = tech_knowledge / (1 + tool_quality)
        return max(1.0, 0.7 * raw + 0.3 * avg_worker_skill)

        Better tools LOWER the skill requirement (tool substitutes for skill).
        Higher tech knowledge RAISES the skill requirement.
        """
        raw = self.tech_knowledge / (1.0 + self.tool_quality)
        requirement = 0.7 * raw + 0.3 * self.avg_worker_skill
        return max(1.0, requirement)

    def get_production_price(self, sector_snlt: float) -> float:
        """
        计算生产价格 - Calculate production price.

        Production price = cost_price * (1 + average_rate_of_profit)
        Used for跨部门交换 (cross-sector exchange).
        """
        # Simplified: just SNLT for now, production price transformation
        # is handled by ReproductionEngine
        return sector_snlt

    def to_dict(self) -> dict:
        """序列化到字典"""
        return {
            'name': self.name,
            'commodity_type': self.commodity_type,
            'tech_knowledge': self.tech_knowledge,
            'tool_quality': self.tool_quality,
            'avg_worker_skill': self.avg_worker_skill,
            'accumulated_output': self.accumulated_output,
        }
