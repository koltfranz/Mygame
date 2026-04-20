"""
Legal System - 法律体系

Includes:
- Property law (所有权法)
- Contract law (契约法)
- Labor law (劳动法)
- Personal law (人身法)
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class LegalFormMetrics:
    """法律形式指标"""
    property_rights_protection: float  # 产权保护强度 (0.0-1.0)
    contract_enforcement: float  # 契约执行力度
    labor_rights_protection: float  # 劳动权利保护
    personal_rights_protection: float  # 人身权利保护
    formal_equality_index: float  # 法律形式平等指数


class LegalSystem:
    """
    法律体系 - Legal system.

    The law is not neutral - it reflects and maintains class rule.
    Legal form treats unequal parties as formally equal.
    """

    def __init__(self):
        self.current_mode = "primitive"  # primitive -> slave -> feudal -> capitalist -> socialist

        # Legal protections (vary by mode of production)
        self.property_law = PropertyLaw()
        self.contract_law = ContractLaw()
        self.labor_law = LaborLaw()

        # Class bias in legal system
        self.class_bias = 0.0  # 0.0 = neutral, positive = favors ruling class

    def update_for_mode(self, mode: str):
        """更新法律体系以适应生产方式"""
        self.current_mode = mode
        self._update_laws()

    def _update_laws(self):
        """根据模式更新法律"""
        if self.current_mode == "primitive":
            self.property_law.protection_level = 0.1
            self.contract_law.enforcement_level = 0.1
            self.labor_law.max_work_hours = None
            self.class_bias = 0.0
        elif self.current_mode == "slave":
            self.property_law.protection_level = 0.3
            self.contract_law.enforcement_level = 0.2
            self.labor_law.max_work_hours = None
            self.class_bias = 0.7  # Strong bias toward slave owners
        elif self.current_mode == "feudal":
            self.property_law.protection_level = 0.4
            self.contract_law.enforcement_level = 0.3
            self.labor_law.max_work_hours = None
            self.class_bias = 0.6
        elif self.current_mode == "capitalist":
            self.property_law.protection_level = 0.8
            self.contract_law.enforcement_level = 0.7
            self.labor_law.max_work_hours = 12
            self.labor_law.min_wage = 8.0
            self.class_bias = 0.4  # Formal equality masks real inequality
        elif self.current_mode == "socialist":
            self.property_law.protection_level = 0.6
            self.contract_law.enforcement_level = 0.8
            self.labor_law.max_work_hours = 8
            self.labor_law.min_wage = 12.0
            self.class_bias = 0.1

    def apply_class_bias(self, case_type: str, plaintiff_class: str, defendant_class: str) -> float:
        """
        应用阶级偏见 - Apply class bias to legal decisions.

        Returns bias factor (1.0 = no bias, >1.0 = favors plaintiff if higher class).
        """
        if self.class_bias == 0.0:
            return 1.0

        class_rank = {
            "capitalist": 5, "lord": 4, "slave_owner": 3,
            "worker": 2, "serf": 1, "slave": 0, "forager": 0
        }

        plaintiff_rank = class_rank.get(plaintiff_class, 0)
        defendant_rank = class_rank.get(defendant_class, 0)

        # Bias favors higher-ranked class
        if plaintiff_rank > defendant_rank:
            return 1.0 + self.class_bias * (plaintiff_rank - defendant_rank) / 5.0
        elif plaintiff_rank < defendant_rank:
            return 1.0 - self.class_bias * (defendant_rank - plaintiff_rank) / 5.0
        return 1.0

    def calculate_legal_form_metrics(self) -> LegalFormMetrics:
        """计算法律形式指标"""
        return LegalFormMetrics(
            property_rights_protection=self.property_law.protection_level,
            contract_enforcement=self.contract_law.enforcement_level,
            labor_rights_protection=self.labor_law.protection_level if hasattr(self.labor_law, 'protection_level') else 0.0,
            personal_rights_protection=0.5 + 0.3 * (1.0 - self.class_bias),
            formal_equality_index=1.0 - self.class_bias * 0.5
        )


class PropertyLaw:
    """所有权法"""

    def __init__(self):
        self.protection_level = 0.1  # How strongly property rights are protected
        self.expropriation_allowed = True  # Can property be forcibly taken?
        self.inheritance_allowed = True


class ContractLaw:
    """契约法"""

    def __init__(self):
        self.enforcement_level = 0.1  # How well contracts are enforced
        self.contracts_recognized = ["informal"]  # Types of contracts recognized


class LaborLaw:
    """劳动法"""

    def __init__(self):
        self.max_work_hours = None  # None = no limit
        self.min_wage = None  # None = no minimum wage
        self.protection_level = 0.0
        self.child_labor_allowed = True