"""
Contract Law - 契约法

Handles contract recognition, enforcement, and types of contracts
recognized in different modes of production.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ContractLaw:
    """契约法 - Contract law subsystem."""

    enforcement_level: float = 0.1  # How well contracts are enforced
    recognized_contracts: List[str] = field(default_factory=lambda: ["informal"])
    contract_freedom: float = 0.5  # 0.0 = restricted, 1.0 = complete freedom

    def __post_init__(self):
        if self.enforcement_level < 0.0:
            self.enforcement_level = 0.0
        if self.enforcement_level > 1.0:
            self.enforcement_level = 1.0

    def is_contract_recognized(self, contract_type: str) -> bool:
        """检查某种契约类型是否被法律承认"""
        return contract_type in self.recognized_contracts

    def calculate_enforcement_probability(self, contract_type: str, plaintiff_class: str, defendant_class: str) -> float:
        """计算契约执行概率"""
        if not self.is_contract_recognized(contract_type):
            return 0.0

        base_probability = self.enforcement_level

        # Class bias affects enforcement
        class_enforcement = {
            "capitalist": 0.9,
            "lord": 0.8,
            "slave_owner": 0.7,
            "artisan": 0.6,
            "worker": 0.5,
            "serf": 0.4,
            "slave": 0.1,
        }

        plaintiff_factor = class_enforcement.get(plaintiff_class, 0.5)
        defendant_factor = class_enforcement.get(defendant_class, 0.5)

        # Average of both parties' class enforcement factors
        class_factor = (plaintiff_factor + defendant_factor) / 2.0

        return base_probability * class_factor

    def get_default_contracts_for_mode(self, mode: str) -> List[str]:
        """获取某生产方式下默认承认的契约类型"""
        mode_contracts = {
            "primitive": ["informal", "gift"],
            "slave": ["sale_of_slave", "debt_bondage"],
            "feudal": ["land_lease", "labor_service", "debt", "apprenticeship"],
            "capitalist": ["wage_labor", "sale", "lease", "credit", "insurance"],
            "socialist": ["labor_assignment", "housing", "consumption"]
        }
        return mode_contracts.get(mode, ["informal"])
