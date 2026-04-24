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
        # 各阶段最小步数要求（防止过快过渡）
        # 时间表: 原始群(-100k) -> 部落(-90k) -> 早期国家(-80k) -> 封建(500) -> 资本主义(1800) -> 社会主义(2000)
        self._min_steps_in_stage: Dict[SocialStage, int] = {
            SocialStage.PRIMITIVE_HORDE: 50,   # 50步 × 200年 = 10,000年
            SocialStage.BAND: 100,              # 100步 × 100年 = 10,000年
            SocialStage.TRIBE: 100,             # 100步 × 100年 = 10,000年
            SocialStage.TRIBAL_CONFEDERACY: 100,  # 100步 × 100年 = 10,000年
            SocialStage.CHIEFDOM: 100,          # 100步 × 100年 = 10,000年
            SocialStage.EARLY_STATE: 101,       # 101步 × 500年 = 50,500年 → 公元500年
            SocialStage.SLAVERY_STATE: 50,      # 50步 × 100年 = 5,000年
            SocialStage.FEUDAL_STATE: 260,      # 260步 × 5年 = 1,300年 → 公元1800年
            SocialStage.CAPITALIST_STATE: 200,  # 200步 × 1月 = 200月 = 16.7年 (但由于强制过渡会延长)
            SocialStage.SOCIALIST_STATE: 200,   # 200步 × 1月 = 200月 = 16.7年
        }
        self._steps_in_current_stage: int = 0

    def evaluate(self, model) -> SocialStage:
        """
        评估是否满足跃迁条件 - Evaluate if transition conditions are met.

        Returns current stage if no transition, otherwise returns new stage.
        """
        # 收集当前指标
        metrics = self._collect_metrics(model)

        # 检查是否满足最小步数要求
        min_steps = self._min_steps_in_stage.get(self.current_stage, 0)
        self._steps_in_current_stage += 1

        if self._steps_in_current_stage < min_steps:
            # 未满足最小步数要求，不能转换
            return self.current_stage

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
            # 获取边类型统计用于自动判断生产模式
            edge_counts = {}
            if hasattr(model, 'social_graph'):
                edge_counts = model.social_graph.get_edge_count_by_type()
            new_stage = self._check_early_state_transition(metrics, edge_counts, model)
        elif self.current_stage == SocialStage.SLAVERY_STATE:
            edge_counts = {}
            if hasattr(model, 'social_graph'):
                edge_counts = model.social_graph.get_edge_count_by_type()
            new_stage = self._check_slavery_state_transition(metrics, edge_counts, model)
        elif self.current_stage == SocialStage.FEUDAL_STATE:
            edge_counts = {}
            if hasattr(model, 'social_graph'):
                edge_counts = model.social_graph.get_edge_count_by_type()
            new_stage = self._check_feudal_state_transition(metrics, edge_counts, model)
        elif self.current_stage == SocialStage.CAPITALIST_STATE:
            edge_counts = {}
            if hasattr(model, 'social_graph'):
                edge_counts = model.social_graph.get_edge_count_by_type()
            new_stage = self._check_capitalist_state_transition(metrics, edge_counts, model)
        else:
            new_stage = self.current_stage

        # 更新当前阶段
        if new_stage != self.current_stage:
            self.current_stage = new_stage
            self._steps_in_current_stage = 0  # 重置步数计数器

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
        """原始群 → 游群：人口积累到一定程度后自动过渡"""
        # 需要更多人口和一定时间才进入游群
        if metrics.population >= 40 and metrics.language_capacity > 0.3:
            return SocialStage.BAND
        return SocialStage.PRIMITIVE_HORDE

    def _check_band_transition(self, metrics: StageMetrics) -> SocialStage:
        """游群 → 部落：人口积累 + 定居率提升"""
        # 需要更多人口积累才进入部落
        if metrics.population >= 60 and metrics.sedentary_ratio > 0.2:
            return SocialStage.TRIBE
        if metrics.population >= 50 and metrics.plant_knowledge >= 0.4:
            return SocialStage.TRIBE
        return SocialStage.BAND

    def _check_tribe_transition(self, metrics: StageMetrics) -> SocialStage:
        """部落 → 部落联盟：人口积累 + 剩余产品"""
        # 需要更多人口积累
        if metrics.population >= 100 and metrics.surplus_ratio > 0.15:
            return SocialStage.TRIBAL_CONFEDERACY
        if metrics.population >= 80 and metrics.gini_coefficient > 0.25:
            return SocialStage.TRIBAL_CONFEDERACY
        return SocialStage.TRIBE

    def _check_confederacy_transition(self, metrics: StageMetrics) -> SocialStage:
        """部落联盟 → 酋邦：人口积累 + 社会分化"""
        # 降低条件，只要人口有一定增长就可以转换
        if metrics.population >= 150 and metrics.gini_coefficient > 0.3:
            return SocialStage.CHIEFDOM
        if metrics.population >= 120 and metrics.surplus_ratio > 0.2:
            return SocialStage.CHIEFDOM
        return SocialStage.TRIBAL_CONFEDERACY

    def _check_chiefdom_transition(self, metrics: StageMetrics) -> SocialStage:
        """酋邦 → 早期国家：人口积累 + 定居率"""
        if metrics.population >= 100 and metrics.residence_ratio > 0.25:
            return SocialStage.EARLY_STATE
        if metrics.population >= 80 and metrics.residence_ratio > 0.4:
            return SocialStage.EARLY_STATE
        return SocialStage.CHIEFDOM

    def _check_early_state_transition(self, metrics: StageMetrics, edge_counts: dict = None,
                                     model=None) -> SocialStage:
        """早期国家 → 后续阶段（基于社会关系自动判断）

        早期国家阶段需要持续较长时间(约80,000年)才进入封建社会。
        时间推进快(500年/步)，所以需要更多步数积累。
        """
        if edge_counts is None:
            return SocialStage.EARLY_STATE

        # 按历史顺序检查（从高到低）
        if edge_counts.get('planning', 0) > 0:
            return SocialStage.SOCIALIST_STATE
        elif edge_counts.get('wage_contract', 0) > 0:
            return SocialStage.CAPITALIST_STATE
        elif edge_counts.get('feudal_rent', 0) > 0:
            return SocialStage.FEUDAL_STATE
        elif edge_counts.get('enslavement', 0) > 0:
            return SocialStage.SLAVERY_STATE

        # 如果没有特定边类型，根据社会分化度和人口决定后续阶段
        # 需要更高的阈值来延长早期国家阶段
        if model and metrics.gini_coefficient > 0.6 and metrics.population > 100:
            # 根据剩余生产率决定是奴隶制还是封建制
            if metrics.surplus_ratio > 0.4:
                # 高剩余产品率倾向于封建生产方式
                self._auto_create_feudal_edges(model)
                return SocialStage.FEUDAL_STATE
            else:
                self._auto_create_slave_edges(model)
                return SocialStage.SLAVERY_STATE

        return SocialStage.EARLY_STATE

    def _auto_create_feudal_edges(self, model):
        """自动创建封建地租边（用于早期国家阶段触发封建化）"""
        from src.model.agents import Serf, Lord
        from src.model.relations import RelationTypes

        existing = list(model._agent_lookup.values())
        if not existing:
            return

        # 创建1-3个领主
        num_lords = min(3, max(1, len(existing) // 30))
        lords = []

        for i in range(num_lords):
            lord = Lord(model)
            pos = (model.random.random() * model.space.width,
                   model.random.random() * model.space.height)
            model.space.place_agent(lord, pos)
            lord.pos = pos
            model.social_graph.add_agent(lord.unique_id)
            model._agent_lookup[lord.unique_id] = lord
            lords.append(lord)

        # 创建农奴并建立封建关系
        num_serfs = min(20, max(5, len(existing) // 5))
        for i in range(num_serfs):
            serf = Serf(model)
            pos = (model.random.random() * model.space.width,
                   model.random.random() * model.space.height)
            model.space.place_agent(serf, pos)
            serf.pos = pos
            model.social_graph.add_agent(serf.unique_id)
            model._agent_lookup[serf.unique_id] = serf

            # 分配给领主
            lord_idx = i % len(lords)
            lord = lords[lord_idx]
            serf.lord_id = lord.unique_id
            lord.serfs_controlled.append(serf.unique_id)

            # 创建封建地租边
            model.social_graph.add_edge(
                serf.unique_id, lord.unique_id,
                RelationTypes.FEUDAL_RENT,
                weight=1.0
            )

    def _auto_create_slave_edges(self, model):
        """自动创建奴役边（用于早期国家阶段触发奴隶制）"""
        from src.model.agents import Slave, SlaveOwner
        from src.model.relations import RelationTypes

        existing = list(model._agent_lookup.values())
        if not existing:
            return

        # 创建奴隶主
        num_owners = min(3, max(1, len(existing) // 40))
        owners = []

        for i in range(num_owners):
            owner = SlaveOwner(model)
            pos = (model.random.random() * model.space.width,
                   model.random.random() * model.space.height)
            model.space.place_agent(owner, pos)
            owner.pos = pos
            model.social_graph.add_agent(owner.unique_id)
            model._agent_lookup[owner.unique_id] = owner
            owners.append(owner)

        # 创建奴隶并建立奴役关系
        num_slaves = min(15, max(5, len(existing) // 4))
        for i in range(num_slaves):
            slave = Slave(model)
            pos = (model.random.random() * model.space.width,
                   model.random.random() * model.space.height)
            model.space.place_agent(slave, pos)
            slave.pos = pos
            model.social_graph.add_agent(slave.unique_id)
            model._agent_lookup[slave.unique_id] = slave

            # 分配给奴隶主
            owner_idx = i % len(owners)
            owner = owners[owner_idx]
            owner.slaves_owned.append(slave.unique_id)

            # 创建奴役边
            model.social_graph.add_edge(
                owner.unique_id, slave.unique_id,
                RelationTypes.ENSLAVEMENT,
                weight=1.0
            )

    def _check_slavery_state_transition(self, metrics: StageMetrics, edge_counts: dict = None,
                                         model=None) -> SocialStage:
        """奴隶社会阶段转换检查

        奴隶社会可以转变为封建社会（通过隶农制转型）
        或者在特定条件下直接向资本主义过渡
        """
        if edge_counts is None:
            return SocialStage.SLAVERY_STATE

        # 如果出现计划关系边，说明正在向社会主义过渡
        if edge_counts.get('planning', 0) > 0:
            return SocialStage.SOCIALIST_STATE

        # 如果出现雇佣关系边，说明正在向资本主义过渡
        if edge_counts.get('wage_contract', 0) > 0:
            return SocialStage.CAPITALIST_STATE

        # 如果封建地租关系出现，可能转向封建社会
        if edge_counts.get('feudal_rent', 0) > 0:
            return SocialStage.FEUDAL_STATE

        # 奴隶社会后期，奴隶反抗加剧可能导致向封建制转型
        if model and metrics.stratification > 0.7 and metrics.surplus_ratio > 0.4:
            self._auto_create_feudal_edges(model)
            return SocialStage.FEUDAL_STATE

        return SocialStage.SLAVERY_STATE

    def _check_feudal_state_transition(self, metrics: StageMetrics, edge_counts: dict = None,
                                        model=None) -> SocialStage:
        """封建社会阶段转换检查

        封建社会可以转变为资本主义（通过货币地租积累和雇佣关系萌芽）
        或者转变为社会主义（通过计划关系的出现）
        """
        if edge_counts is None:
            return SocialStage.FEUDAL_STATE

        # 如果出现计划关系边，说明正在向社会主义过渡
        if edge_counts.get('planning', 0) > 0:
            return SocialStage.SOCIALIST_STATE

        # 如果出现雇佣关系边，说明正在向资本主义过渡
        if edge_counts.get('wage_contract', 0) > 0:
            return SocialStage.CAPITALIST_STATE

        # 封建社会中后期，货币地租积累可能导致资本主义萌芽
        # 当剩余生产率高且人口达到一定规模时，触发资本主义化
        if model and metrics.surplus_ratio > 0.5 and metrics.population > 80:
            self._auto_create_capitalist_edges(model)
            return SocialStage.CAPITALIST_STATE

        return SocialStage.FEUDAL_STATE

    def _check_capitalist_state_transition(self, metrics: StageMetrics, edge_counts: dict = None,
                                           model=None) -> SocialStage:
        """资本主义阶段转换检查

        资本主义可以转变为社会主义（通过革命或计划关系的出现）
        """
        if edge_counts is None:
            return SocialStage.CAPITALIST_STATE

        # 如果出现计划关系边，说明正在向社会主义过渡
        if edge_counts.get('planning', 0) > 0:
            return SocialStage.SOCIALIST_STATE

        # 资本主义后期，利润率下降和危机可能导致向社会主义过渡
        if model:
            profit_rate = model.reproduction_engine.crisis_indicators.get('rate_of_profit', 0)

            # 条件：利润率低 OR 高度分化 OR 人口足够多（超过一定时间后强制过渡）
            time_in_capitalism = model.time - getattr(model, '_capitalism_start_time', model.time)
            # 降低时间阈值，使演示更快速看到完整演进
            force_transition = time_in_capitalism > 50  # 超过50步强制过渡（用于演示）

            if (profit_rate < 0.10 and metrics.stratification > 0.3) or force_transition:
                # 危机深化时，创建计划关系边
                self._auto_create_socialist_edges(model)
                return SocialStage.SOCIALIST_STATE

        return SocialStage.CAPITALIST_STATE

    def _auto_create_capitalist_edges(self, model):
        """自动创建雇佣关系边（用于封建社会阶段触发资本主义化）"""
        from src.model.agents import Capitalist, Worker
        from src.model.relations import RelationTypes

        existing = list(model._agent_lookup.values())
        if not existing:
            return

        # 创建资本家
        num_capitalists = min(3, max(1, len(existing) // 50))
        capitalists = []

        for i in range(num_capitalists):
            capitalist = Capitalist(model)
            pos = (model.random.random() * model.space.width,
                   model.random.random() * model.space.height)
            model.space.place_agent(capitalist, pos)
            capitalist.pos = pos
            model.social_graph.add_agent(capitalist.unique_id)
            model._agent_lookup[capitalist.unique_id] = capitalist
            capitalists.append(capitalist)

        # 创建工人并建立雇佣关系
        num_workers = min(20, max(10, len(existing) // 5))
        for i in range(num_workers):
            worker = Worker(model)
            pos = (model.random.random() * model.space.width,
                   model.random.random() * model.space.height)
            model.space.place_agent(worker, pos)
            worker.pos = pos
            model.social_graph.add_agent(worker.unique_id)
            model._agent_lookup[worker.unique_id] = worker

            # 分配给资本家
            capitalist_idx = i % len(capitalists)
            capitalist = capitalists[capitalist_idx]
            worker.employed_by = capitalist.unique_id
            capitalist.workers_employed.append(worker.unique_id)

            # 创建工资合同边
            model.social_graph.add_edge(
                worker.unique_id, capitalist.unique_id,
                RelationTypes.WAGE_CONTRACT,
                weight=1.0
            )

    def _auto_create_socialist_edges(self, model):
        """自动创建计划分配边（用于资本主义阶段触发社会主义化）"""
        from src.model.relations import RelationTypes

        all_agents = list(model._agent_lookup.values())
        if len(all_agents) > 1:
            for i, agent in enumerate(all_agents[:30]):  # 限制数量
                next_agent = all_agents[(i + 1) % len(all_agents)]
                model.social_graph.add_edge(
                    agent.unique_id, next_agent.unique_id,
                    RelationTypes.PLANNING,
                    weight=1.0
                )

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
