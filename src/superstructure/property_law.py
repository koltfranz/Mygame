"""
Property Law - 所有权法

Handles property rights, expropriation, and inheritance rules
for different modes of production.
"""

from dataclasses import dataclass


@dataclass
class PropertyLaw:
    """所有权法 - Property law subsystem."""

    protection_level: float = 0.1  # How strongly property rights are protected
    expropriation_allowed: bool = True  # Can property be forcibly taken?
    inheritance_allowed: bool = True
    private_property_recognition: float = 0.5  # 0.0 = none, 1.0 = absolute

    def __post_init__(self):
        if self.protection_level < 0.0:
            self.protection_level = 0.0
        if self.protection_level > 1.0:
            self.protection_level = 1.0

    def can_expropriate(self, target_class: str,expropriator_class: str) -> bool:
        """判断是否可以强制剥夺某阶级的财产"""
        if not self.expropriation_allowed:
            return False

        class_hierarchy = {
            "capitalist": 5,
            "lord": 4,
            "slave_owner": 3,
            "artisan": 2,
            "worker": 2,
            "serf": 1,
            "slave": 0,
            "forager": 0
        }

        target_rank = class_hierarchy.get(target_class, 0)
        expropriator_rank = class_hierarchy.get(expropriator_class, 0)

        # 上层阶级可以剥夺下层
        return expropriator_rank > target_rank

    def calculate_compensation(self, property_value: float, mode: str) -> float:
        """计算征收补偿"""
        if mode == "socialist":
            return property_value * 0.8
        elif mode == "capitalist":
            return property_value * 1.0  # Full compensation
        elif mode == "feudal":
            return property_value * 0.3
        elif mode == "slave":
            return 0.0
        return property_value * 0.5
