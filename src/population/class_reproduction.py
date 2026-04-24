"""
Class Reproduction - 代际阶级传递

Handles the intergenerational transmission of class position
and the reproduction of class structure across generations.
"""

from typing import Dict, List, Tuple
import random


class ClassReproductionEngine:
    """
    代际阶级传递引擎 - Class reproduction engine.

    Class position is not determined by "family background" but by
    the reproduction of production relations across generations.

    Key mechanisms:
    1. Inheritance of property relations (not "genes")
    2. Transmission of skills within class fractions
    3. Structural limits on mobility
    4. Crisis-driven class restructuring
    """

    def __init__(self):
        self.mobility_rates: Dict[str, float] = {
            "primitive": 0.3,   # High mobility in egalitarian societies
            "slave": 0.05,       # Very low - slaves rarely become free
            "feudal": 0.1,      # Low - serfs rarely become lords
            "capitalist": 0.15,  # Low-moderate - workers rarely become capitalists
            "socialist": 0.2,   # Moderate - more equal opportunity
        }

    def calculate_offspring_class(
        self,
        parent_class: str,
        mode: str,
        crisis_level: float = 0.0
    ) -> str:
        """
        计算子代的阶级位置

        阶级位置由以下因素决定:
        1. 生产关系继承（不是财富继承）
        2. 教育/培训机会
        3. 危机对阶级结构的冲击
        """
        if mode == "primitive":
            # 原始社会：基于血缘但高度流动
            return self._primitive_inheritance(parent_class)

        elif mode == "slave":
            return self._slave_inheritance(parent_class, crisis_level)

        elif mode == "feudal":
            return self._feudal_inheritance(parent_class, crisis_level)

        elif mode == "capitalist":
            return self._capitalist_inheritance(parent_class, crisis_level)

        elif mode == "socialist":
            return self._socialist_inheritance(parent_class)

        return "worker"  # Default

    def _primitive_inheritance(self, parent_class: str) -> str:
        """原始社会：基于血缘和能力的混合"""
        if parent_class in ["forager", "band_member"]:
            return random.choices(
                ["forager", "hunter", "gatherer"],
                weights=[0.4, 0.3, 0.3]
            )[0]
        return "forager"

    def _slave_inheritance(self, parent_class: str, crisis_level: float) -> str:
        """奴隶社会：奴隶子女几乎不可能成为自由人"""
        if parent_class == "slave":
            # 极低概率变为自由人（通过逃亡、起义、解放）
            if random.random() < 0.02 + crisis_level * 0.1:
                return "free_laborer"
            return "slave"

        elif parent_class == "slave_owner":
            # 奴隶主子女可能降为自由农民（通过破产）
            if random.random() < 0.1:
                return random.choice(["free_artisan", "free_farmer"])
            return "slave_owner"

        return "free_laborer"

    def _feudal_inheritance(self, parent_class: str, crisis_level: float) -> str:
        """封建社会：农奴向领主转变的概率很低"""
        if parent_class == "serf":
            # 农奴通过努力可能成为自由农民（货币地租时期）
            mobility_chance = 0.05 + crisis_level * 0.05
            if random.random() < mobility_chance:
                return random.choice(["free_farmer", "artisan"])
            return "serf"

        elif parent_class == "lord":
            # 领主可能因破产成为商人或农民
            if random.random() < 0.05 + crisis_level * 0.1:
                return random.choice(["merchant", "free_farmer"])
            return "lord"

        elif parent_class == "artisan":
            # 工匠可能上升为商人或下降为工人
            if random.random() < 0.15:
                return "merchant"
            return "artisan"

        return "serf"

    def _capitalist_inheritance(self, parent_class: str, crisis_level: float) -> str:
        """资本主义社会：代际流动性较低但存在"""
        if parent_class == "worker":
            # 工人子女可能通过教育成为工匠、小资本家
            if random.random() < 0.08 + crisis_level * 0.05:
                return random.choice(["artisan", "small_capitalist"])
            return "worker"

        elif parent_class == "capitalist":
            # 资本家子女可能破产成为工人或保持资本家
            if random.random() < 0.15 + crisis_level * 0.2:
                return random.choice(["worker", "artisan"])
            return "capitalist"

        elif parent_class == "landlord":
            # 地主可能转化为资本家或失去土地
            if random.random() < 0.1 + crisis_level * 0.15:
                return random.choice(["capitalist", "worker"])
            return "landlord"

        return "worker"

    def _socialist_inheritance(self, parent_class: str) -> str:
        """社会主义社会：更平等的代际传递"""
        if parent_class == "worker":
            # 工人的子女有更多机会成为技术人员或管理者
            return random.choices(
                ["worker", "technician", "administrator"],
                weights=[0.5, 0.3, 0.2]
            )[0]

        elif parent_class == "administrator":
            return random.choices(
                ["administrator", "technician", "worker"],
                weights=[0.4, 0.4, 0.2]
            )[0]

        return "worker"

    def calculate_class_structure_change(
        self,
        current_structure: Dict[str, int],
        mode: str,
        crisis_level: float
    ) -> Dict[str, int]:
        """
        计算阶级结构变化

        危机会导致阶级结构重组：
        - 危机期间小资产阶级破产
        - 危机期间工人状况恶化
        - 危机后可能出现新的阶级组合
        """
        new_structure = current_structure.copy()

        if mode == "capitalist" and crisis_level > 0.3:
            # 危机期间小资产阶级破产加速
            if "artisan" in new_structure:
                new_structure["artisan"] = int(new_structure["artisan"] * 0.9)
            if "small_capitalist" in new_structure:
                new_structure["small_capitalist"] = int(new_structure["small_capitalist"] * 0.85)

            # 产业后备军扩大
            if "worker" in new_structure:
                new_structure["reserve_army"] = new_structure.get("reserve_army", 0) + int(
                    len([a for a in current_structure.values() if isinstance(a, int)]) * crisis_level * 0.1
                )

        elif mode == "feudal" and crisis_level > 0.4:
            # 高度危机可能导致农奴起义并获得自由
            if "serf" in new_structure and "lord" in new_structure:
                freed_count = int(new_structure["serf"] * crisis_level * 0.1)
                new_structure["serf"] -= freed_count
                new_structure["free_farmer"] = new_structure.get("free_farmer", 0) + freed_count

        elif mode == "slave" and crisis_level > 0.5:
            # 严重危机可能触发奴隶起义
            if "slave" in new_structure and "slave_owner" in new_structure:
                freed_count = int(new_structure["slave"] * crisis_level * 0.2)
                new_structure["slave"] -= freed_count
                new_structure["free_laborer"] = new_structure.get("free_laborer", 0) + freed_count

        return new_structure

    def get_mobility_rate(self, mode: str) -> float:
        """获取某生产方式的代际流动性"""
        return self.mobility_rates.get(mode, 0.1)
