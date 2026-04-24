"""
Personal Law - 人身法

Handles personal rights, freedom of movement, marriage rights,
and other personal liberties in different modes of production.
"""

from dataclasses import dataclass


@dataclass
class PersonalLaw:
    """人身法 - Personal law subsystem."""

    personhood_recognition: float = 0.5  # 0.0 = none, 1.0 = full
    movement_freedom: float = 1.0  # 0.0 = restricted, 1.0 = complete
    marriage_freedom: float = 0.5  # 0.0 = arranged/restricted, 1.0 = free choice
    torture_legal: float = 0.0  # 0.0 = illegal, 1.0 = legal
    assembly_freedom: float = 0.3

    def can_marry_freely(self, class_type: str) -> bool:
        """检查某阶级是否可以自由婚姻"""
        if class_type in ["slave"]:
            return False
        return self.marriage_freedom > 0.5

    def can_travel(self, class_type: str, mode: str) -> bool:
        """检查某阶级是否可以自由旅行"""
        if mode == "slave" and class_type == "slave":
            return False
        if mode == "feudal" and class_type == "serf":
            return self.movement_freedom > 0.7
        return self.movement_freedom > 0.5

    def has_legal_personhood(self, class_type: str) -> bool:
        """检查某阶级是否被承认有法律人格"""
        if class_type in ["slave"]:
            return self.personhood_recognition < 0.3
        return self.personhood_recognition > 0.5

    def can_assemble(self, class_type: str) -> bool:
        """检查某阶级是否有集会自由"""
        if class_type in ["slave"]:
            return self.assembly_freedom > 0.8
        return self.assembly_freedom > 0.3
