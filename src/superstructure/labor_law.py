"""
Labor Law - 劳动法

Handles labor regulations including work hours, minimum wages,
child labor, and worker organization rights.
"""

from dataclasses import dataclass


@dataclass
class LaborLaw:
    """劳动法 - Labor law subsystem."""

    max_work_hours: float | None = None  # None = no limit
    min_wage: float | None = None  # None = no minimum
    protection_level: float = 0.0
    child_labor_allowed: bool = True
    child_labor_age: int = 10
    strike_right: float = 0.0  # 0.0 = forbidden, 1.0 = unrestricted
    union_right: float = 0.0  # 0.0 = forbidden, 1.0 = unrestricted

    def get_max_hours_for_class(self, class_type: str) -> float | None:
        """获取某阶级最大工作时长"""
        if class_type in ["slave"]:
            return None  # No limit for slaves
        return self.max_work_hours

    def get_min_wage_for_class(self, class_type: str) -> float | None:
        """获取某阶级最低工资"""
        if class_type in ["slave", "serf"]:
            return None  # No minimum wage for unfree labor
        return self.min_wage

    def can_strike(self, class_type: str) -> bool:
        """检查某阶级是否有罢工权"""
        if class_type in ["slave", "serf"]:
            return False
        return self.strike_right > 0.5

    def can_unionize(self, class_type: str) -> bool:
        """检查某阶级是否有组织工会权"""
        if class_type in ["slave", "serf"]:
            return False
        return self.union_right > 0.5

    def is_child_labor(self, age: int) -> bool:
        """判断是否构成童工"""
        if not self.child_labor_allowed:
            return age < 18
        return age < self.child_labor_age
