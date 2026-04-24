"""
Legal Reform - 法律改革触发判定

Handles the triggering of legal reforms based on:
- Class struggle intensity
- Crisis indicators
- Ideological shifts
- International pressure

RED LINE: Legal reforms are NOT driven by "enlightenment" or "progress."
They are driven by class conflict and structural crises.
"""

from typing import Dict, List, Tuple


class LegalReformEngine:
    """
    法律改革引擎 - Legal reform trigger engine.

    Legal reforms are triggered when:
    1. Class struggle reaches threshold (strike, rent resistance)
    2. Crisis indicators show systemic imbalance
    3. Hegemony is weakening
    4. Revolutionary tension is high
    """

    def __init__(self):
        self.reform_history: List[Dict] = []
        self.reform_cooldown: int = 0

    def check_reform_triggers(self, model) -> List[str]:
        """
        检查改革触发条件 - Check for legal reform triggers.

        Returns list of triggered reform types.
        """
        triggered = []

        # Decrease cooldown
        if self.reform_cooldown > 0:
            self.reform_cooldown -= 1
            return triggered

        crisis = model.reproduction_engine.crisis_indicators

        # 1. Labor law reform triggered by worker struggle
        if hasattr(model, 'class_struggle_engine'):
            struggle = model.class_struggle_engine
            strike_activity = getattr(struggle, 'strike_activity', 0.0)
            if strike_activity > 0.5 and self.reform_cooldown == 0:
                triggered.append("labor_hour_reduction")
                triggered.append("minimum_wage_increase")

        # 2. Property law reform triggered by crisis
        rate_of_profit = crisis.get('rate_of_profit', 0.2)
        if rate_of_profit < 0.05 and self.reform_cooldown == 0:
            triggered.append("property_rights_reform")

        # 3. Personal law reform (suffrage expansion, etc.)
        legitimacy = getattr(model, 'legitimacy', 0.5)
        if hasattr(model, 'legitimacy'):
            if legitimacy < 0.3 and self.reform_cooldown == 0:
                triggered.append("suffrage_expansion")

        # 4. Political regime reform
        revolutionary_tension = getattr(model, 'revolutionary_tension', 0.0)
        if revolutionary_tension > 0.7 and self.reform_cooldown == 0:
            triggered.append("regime_transition")

        if triggered:
            self.reform_history.append({
                'step': model.time,
                'reforms': triggered,
                'crisis_state': crisis,
            })
            self.reform_cooldown = 10  # Steps before next reform

        return triggered

    def apply_reform(self, reform_type: str, legal_system) -> str:
        """
        应用法律改革 - Apply a legal reform.

        Returns description of the reform applied.
        """
        from src.superstructure.labor_law import LaborLaw

        if reform_type == "labor_hour_reduction":
            if legal_system.labor_law.max_work_hours:
                legal_system.labor_law.max_work_hours = max(
                    8, legal_system.labor_law.max_work_hours - 1
                )
            return f"工时减少至{legal_system.labor_law.max_work_hours}小时"

        elif reform_type == "minimum_wage_increase":
            if legal_system.labor_law.min_wage:
                legal_system.labor_law.min_wage *= 1.1
            return f"最低工资提高至{legal_system.labor_law.min_wage:.1f}"

        elif reform_type == "suffrage_expansion":
            legal_system.personal_law.assembly_freedom = min(
                1.0, legal_system.personal_law.assembly_freedom + 0.1
            )
            return "选举权扩大"

        elif reform_type == "property_rights_reform":
            legal_system.property_law.protection_level = max(
                0.0, legal_system.property_law.protection_level - 0.1
            )
            return "产权限制加强"

        elif reform_type == "regime_transition":
            legal_system.class_bias = max(0.0, legal_system.class_bias - 0.1)
            return "政体改革"

        return "未知改革"

    def get_reform_history(self) -> List[Dict]:
        """获取改革历史"""
        return self.reform_history
