"""
SocialStage - 社会演进阶段枚举与转型引擎

基于塞维斯-弗里德框架扩展版的人类社会演进模型。
- PRIMITIVE_HORDE (原始群): 10-30人，100年/步
- BAND (游群): 20-50人，100→10年/步
- TRIBE (部落): 100-500人，10→1年/步
- TRIBAL_CONFEDERACY (部落联盟): 500-2000人，1年/步
- CHIEFDOM (酋邦): 2000-10000人，1年/步
- EARLY_STATE (早期国家): 10000+，1年/步
- SLAVERY_STATE (奴隶社会): 可变
- FEUDAL_STATE (封建社会): 可变
- CAPITALIST_STATE (资本主义): 可变
- SOCIALIST_STATE (社会主义): 可变
"""

from enum import Enum
from typing import Dict, Set, Optional


class SocialStage(Enum):
    """社会演进阶段枚举"""
    PRIMITIVE_HORDE = "primitive_horde"
    BAND = "band"
    TRIBE = "tribe"
    TRIBAL_CONFEDERACY = "tribal_confederacy"
    CHIEFDOM = "chiefdom"
    EARLY_STATE = "early_state"
    SLAVERY_STATE = "slavery_state"
    FEUDAL_STATE = "feudal_state"
    CAPITALIST_STATE = "capitalist_state"
    SOCIALIST_STATE = "socialist_state"


class StageMetrics:
    """阶段指标数据类"""

    def __init__(self):
        # 人口指标
        self.population: int = 0
        self.population_growth_rate: float = 0.0

        # 生产指标
        self.surplus_ratio: float = 0.0  # 剩余产品率
        self.sedentary_ratio: float = 0.0  # 定居率

        # 技术指标
        self.fire_use: bool = False  # 火的使用
        self.language_capacity: float = 0.0  # 语言能力
        self.plant_knowledge: float = 0.0  # 植物驯化知识

        # 社会结构指标
        self.stratification: float = 0.0  # 社会分化度
        self.war_frequency: float = 0.0  # 战争频率
        self.kinship_ratio: float = 1.0  # 血缘关系比例
        self.residence_ratio: float = 0.0  # 地缘关系比例

        # 权力结构指标
        self.hereditary_index: float = 0.0  # 世袭权力指数
        self.state_capacity: float = 0.0  # 国家能力

        # 经济指标
        self.gini_coefficient: float = 0.0  # 基尼系数
        self.commodity_circulation: float = 0.0  # 商品流通量


class TransitionEngine:
    """
    多元决定跃迁引擎 - Multi-determined transition engine.

    基于阿尔都塞结构因果性理论评估阶段转型条件。
    """

    def __init__(self):
        self.current_stage = SocialStage.PRIMITIVE_HORDE
        self.transition_indicators: Dict[str, float] = {}

    def evaluate(self, model) -> SocialStage:
        """
        评估是否满足跃迁条件 - Evaluate if transition conditions are met.

        Returns current stage if no transition, otherwise returns new stage.
        """
        # 收集当前指标
        metrics = self._collect_metrics(model)

        if self.current_stage == SocialStage.PRIMITIVE_HORDE:
            new_stage = self._check_primitive_horde_transition(metrics)
        elif self.current_stage == SocialStage.BAND:
            new_stage = self._check_band_transition(metrics)
        elif self.current_stage == SocialStage.TRIBE:
            new_stage = self._check_tribe_transition(metrics)
        elif self.current_stage == SocialStage.TRIBAL_CONFEDERACY:
            new_stage = self._check_confederacy_transition(metrics)
        elif self.current_stage == SocialStage.CHIEFDOM:
            new_stage = self._check_chiefdom_transition(metrics)
        elif self.current_stage == SocialStage.EARLY_STATE:
            new_stage = self._check_early_state_transition(metrics)
        else:
            new_stage = self.current_stage

        # 更新当前阶段
        if new_stage != self.current_stage:
            self.current_stage = new_stage

        return new_stage

    def _collect_metrics(self, model) -> StageMetrics:
        """收集模型指标"""
        metrics = StageMetrics()

        # 人口
        metrics.population = len(model._agent_lookup) if hasattr(model, '_agent_lookup') else 0

        # 社会关系分析
        if hasattr(model, 'social_graph'):
            graph = model.social_graph
            edge_counts = graph.get_edge_count_by_type()

            # 计算血缘vs地缘比例
            kinship_edges = edge_counts.get('kinship', 0) + edge_counts.get('clan', 0)
            residence_edges = edge_counts.get('residence', 0)
            total_edges = sum(edge_counts.values())
            if total_edges > 0:
                metrics.residence_ratio = residence_edges / total_edges
                metrics.kinship_ratio = kinship_edges / total_edges

            # 计算社会分化（基于库存差异）
            inventories = [len(a.commodity_inventory) for a in model._agent_lookup.values()]
            if inventories:
                avg = sum(inventories) / len(inventories)
                variance = sum((x - avg) ** 2 for x in inventories) / len(inventories)
                metrics.gini_coefficient = min(1.0, variance * 2)

        # 生存资料分析
        if hasattr(model, '_agent_lookup') and model._agent_lookup:
            subs_levels = [a.subsistence_satisfaction for a in model._agent_lookup.values()]
            subs_avg = sum(subs_levels) / len(subs_levels)
            subs_variance = sum((x - subs_avg) ** 2 for x in subs_levels) / len(subs_levels)
            metrics.stratification = min(1.0, subs_variance * 10)

            # 计算定居率（有工具/商品的agent视为有一定定居程度）
            settled_count = sum(1 for a in model._agent_lookup.values()
                              if len(a.commodity_inventory) > 0 or a.skill_type is not None)
            metrics.sedentary_ratio = settled_count / len(model._agent_lookup) if model._agent_lookup else 0.0

            # 计算植物知识（基于技能水平）
            total_skill = sum(a.skill_level for a in model._agent_lookup.values())
            avg_skill = total_skill / len(model._agent_lookup)
            metrics.plant_knowledge = min(1.0, avg_skill / 3.0)  # 归一化

            # 计算剩余生产率
            total_produced = sum(len(a.commodity_inventory) for a in model._agent_lookup.values())
            total_consumed = sum(1 for a in model._agent_lookup.values() if a.subsistence_satisfaction > 0.8)
            if total_consumed > 0:
                metrics.surplus_ratio = (total_produced - total_consumed) / total_consumed

            # 火的使用（在游群阶段假设已掌握）
            metrics.fire_use = metrics.population >= 20

            # 语言能力（基于人口规模）
            metrics.language_capacity = min(1.0, metrics.population / 50.0)

            # 世袭权力指数（基于社会分化 + 剩余产品）
            metrics.hereditary_index = min(1.0, metrics.gini_coefficient * metrics.surplus_ratio / 10.0)

            # 国家能力（基于定居率 + 人口规模）
            metrics.state_capacity = min(1.0, metrics.sedentary_ratio * 0.5 + (metrics.population / 200.0) * 0.5)

            # 计算地缘关系比例（随着社会发展，地缘关系增加）
            if edge_counts:
                total_edges = sum(edge_counts.values())
                if total_edges > 0:
                    # 假设定居率越高，地缘关系越多
                    metrics.residence_ratio = min(1.0, metrics.sedentary_ratio * 0.7)
                    metrics.kinship_ratio = 1.0 - metrics.residence_ratio

        return metrics

    def _check_primitive_horde_transition(self, metrics: StageMetrics) -> SocialStage:
        """原始群 → 游群：火的使用 + 语言能力"""
        if metrics.fire_use and metrics.language_capacity > 0.5:
            return SocialStage.BAND
        if metrics.population >= 30:
            # 人口超过阈值，自动进入游群
            return SocialStage.BAND
        return SocialStage.PRIMITIVE_HORDE

    def _check_band_transition(self, metrics: StageMetrics) -> SocialStage:
        """游群 → 部落：定居率 > 30% + 植物驯化知识"""
        if metrics.sedentary_ratio > 0.3 and metrics.plant_knowledge > 0.5:
            return SocialStage.TRIBE
        if metrics.population >= 50 and metrics.plant_knowledge > 0.3:
            return SocialStage.TRIBE
        return SocialStage.BAND

    def _check_tribe_transition(self, metrics: StageMetrics) -> SocialStage:
        """部落 → 部落联盟：剩余产品率高 + 社会分化显著"""
        if metrics.surplus_ratio > 0.5 and metrics.gini_coefficient > 0.3:
            return SocialStage.TRIBAL_CONFEDERACY
        if metrics.population >= 100 and metrics.surplus_ratio > 0.2:
            return SocialStage.TRIBAL_CONFEDERACY
        return SocialStage.TRIBE

    def _check_confederacy_transition(self, metrics: StageMetrics) -> SocialStage:
        """部落联盟 → 酋邦：社会分化显著 + 基尼系数 > 0.4"""
        if metrics.gini_coefficient > 0.4 and metrics.surplus_ratio > 0.3:
            return SocialStage.CHIEFDOM
        if metrics.population >= 100 and metrics.gini_coefficient > 0.3:
            return SocialStage.CHIEFDOM
        return SocialStage.TRIBAL_CONFEDERACY

    def _check_chiefdom_transition(self, metrics: StageMetrics) -> SocialStage:
        """酋邦 → 早期国家：地缘关系增加 + 国家能力形成"""
        if metrics.residence_ratio > 0.3 and metrics.gini_coefficient > 0.5:
            return SocialStage.EARLY_STATE
        if metrics.population >= 100 and metrics.residence_ratio > 0.2:
            return SocialStage.EARLY_STATE
        return SocialStage.CHIEFDOM

    def _check_early_state_transition(self, metrics: StageMetrics) -> SocialStage:
        """早期国家 → 后续阶段（基于生产关系）"""
        # 根据生产关系类型决定后续阶段
        if hasattr(self, '_production_mode'):
            if self._production_mode == 'enslavement':
                return SocialStage.SLAVERY_STATE
            elif self._production_mode == 'feudal':
                return SocialStage.FEUDAL_STATE
            elif self._production_mode == 'capitalist':
                return SocialStage.CAPITALIST_STATE
        return SocialStage.EARLY_STATE

    def get_current_stage(self) -> SocialStage:
        """获取当前阶段"""
        return self.current_stage

    def _calculate_surplus_ratio(self, model) -> float:
        """计算剩余生产率"""
        total_produced = sum(
            len(a.commodity_inventory) for a in model._agent_lookup.values()
        )
        total_consumed = sum(
            1 for a in model._agent_lookup.values() if a.subsistence_satisfaction > 0.9
        )
        if total_consumed == 0:
            return 0.0
        return (total_produced - total_consumed) / total_consumed

    def _calculate_stratification(self, model) -> float:
        """计算社会分化度"""
        if len(model._agent_lookup) < 2:
            return 0.0

        agents = list(model._agent_lookup.values())

        # 1. 生存资料满足率方差
        subsistence_levels = [a.subsistence_satisfaction for a in agents]
        subs_avg = sum(subsistence_levels) / len(subsistence_levels)
        subs_variance = sum((x - subs_avg) ** 2 for x in subsistence_levels) / len(subsistence_levels)

        # 2. 库存差异（基尼系数风格）
        inventories = [len(a.commodity_inventory) for a in agents]
        inv_avg = sum(inventories) / len(inventories) if inventories else 0
        if inv_avg > 0:
            inv_variance = sum((x - inv_avg) ** 2 for x in inventories) / len(inventories)
            inv_variance = min(1.0, inv_variance / (inv_avg ** 2 + 0.1))
        else:
            inv_variance = 0

        # 3. 技能水平差异
        skill_levels = [a.skill_level for a in agents]
        skill_avg = sum(skill_levels) / len(skill_levels)
        skill_variance = sum((x - skill_avg) ** 2 for x in skill_levels) / len(skill_levels)

        # 综合分化度
        combined = subs_variance * 0.5 + inv_variance * 0.3 + skill_variance * 0.2
        return min(1.0, combined * 10)

    def _calculate_density(self, model) -> float:
        """计算人口密度"""
        num_agents = len(model._agent_lookup)
        max_capacity = 200
        return min(1.0, num_agents / max_capacity)

    def get_stage_info(self) -> Dict:
        """获取阶段信息"""
        stage_info = {
            SocialStage.PRIMITIVE_HORDE: {
                "name": "原始群",
                "population": "10-30",
                "time_scale": "100年/步",
                "core_relation": "无固定关系",
                "power_structure": "完全平等"
            },
            SocialStage.BAND: {
                "name": "游群",
                "population": "20-50",
                "time_scale": "100→10年/步",
                "core_relation": "KinshipEdge",
                "power_structure": "临时自然领袖"
            },
            SocialStage.TRIBE: {
                "name": "部落",
                "population": "100-500",
                "time_scale": "10→1年/步",
                "core_relation": "ClanEdge",
                "power_structure": "议事会民主"
            },
            SocialStage.TRIBAL_CONFEDERACY: {
                "name": "部落联盟",
                "population": "500-2000",
                "time_scale": "1年/步",
                "core_relation": "MilitaryAllianceEdge",
                "power_structure": "选举军事首领"
            },
            SocialStage.CHIEFDOM: {
                "name": "酋邦",
                "population": "2000-10000",
                "time_scale": "1年/步",
                "core_relation": "TributaryEdge",
                "power_structure": "世袭酋长"
            },
            SocialStage.EARLY_STATE: {
                "name": "早期国家",
                "population": "10000+",
                "time_scale": "1年/步",
                "core_relation": "ResidenceEdge",
                "power_structure": "官僚+常备军"
            },
            SocialStage.SLAVERY_STATE: {
                "name": "奴隶社会",
                "population": "可变",
                "time_scale": "1年/步",
                "core_relation": "EnslavementEdge",
                "power_structure": "奴隶主专政"
            },
            SocialStage.FEUDAL_STATE: {
                "name": "封建社会",
                "population": "可变",
                "time_scale": "1年/步",
                "core_relation": "FeudalRentEdge",
                "power_structure": "地主阶级统治"
            },
            SocialStage.CAPITALIST_STATE: {
                "name": "资本主义",
                "population": "可变",
                "time_scale": "1年→1月/步",
                "core_relation": "WageContractEdge",
                "power_structure": "资产阶级专政"
            },
            SocialStage.SOCIALIST_STATE: {
                "name": "社会主义",
                "population": "可变",
                "time_scale": "1月/步",
                "core_relation": "PlanningEdge",
                "power_structure": "无产阶级专政"
            }
        }
        return stage_info.get(self.current_stage, {})
