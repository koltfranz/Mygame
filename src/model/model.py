"""
CapitalModel - Main Mesa Model for CapitalSimulator

Coordinates all subsystems: agents, social relations, landscape, data collection.
"""

from mesa import Model
from mesa.space import ContinuousSpace
import networkx as nx

from src.model.agents import Forager, TribeMember, Farmer, Slave, SlaveOwner, Serf, Lord, Worker, Capitalist, Human
from src.model.relations import SocialRelationGraph, RelationTypes
from src.model.resources import Landscape
from src.model.social_stage import SocialStage, TransitionEngine
from src.model.ontology import Matter, MatterState
from src.analysis.data_collector import DataCollector
from src.engine.reproduction import ReproductionEngine
from src.engine.value_form_router import ImpedanceRouter
from src.engine.class_struggle import ClassStruggleEngine
from src.population.demography import DemographyEngine
from src.superstructure.state_apparatus import StateApparatus
from src.superstructure.political_regime import PoliticalRegime
from src.superstructure.ideology_manager import IdeologyManager
from src.utils.snapshot import SnapshotManager, Snapshot


class CapitalModel(Model):
    """
    资本模拟器主模型 - Main model for the CapitalSimulator.

    Implements historical materialist simulation with:
    - Four-state matter machine
    - Social relation graph (no "human nature" behavioral assumptions)
    - Social stage transitions (塞维斯-弗里德框架)
    """

    def __init__(self,
                 width: int = 100,
                 height: int = 100,
                 num_foragers: int = 30,
                 num_tribe_members: int = 20,
                 num_farmers: int = 0,
                 seed: int = None):
        super().__init__(seed=seed)

        # Space
        self.space = ContinuousSpace(width, height, torus=True)

        # Social relations graph
        self.social_graph = SocialRelationGraph()

        # Landscape
        self.landscape = Landscape(width, height, num_cells_x=20, num_cells_y=20)

        # Social stage and transition engine
        self.social_stage = SocialStage.PRIMITIVE_HORDE
        self.transition_engine = TransitionEngine()

        # Reproduction engine (for crisis detection)
        self.reproduction_engine = ReproductionEngine()

        # Demography engine (for population dynamics)
        self.demography_engine = DemographyEngine()

        # Political subsystems
        self.state_apparatus = StateApparatus()
        self.political_regime = PoliticalRegime()
        self.ideology_manager = IdeologyManager()

        # Data collector
        self.data_collector = DataCollector(self)

        # Snapshot manager for diagnostic reports
        self.snapshot_manager = SnapshotManager(max_snapshots=50)

        # Track agents for lookup
        self._agent_lookup: dict = {}
        self.lords: list = []
        self.serfs: list = []

        #资本主义阶段开始时间（用于五步时序调度）
        self._capitalism_start_time: float = 0

        # 时间追踪（从公元前10万年start）
        self._current_year: int = -100000  # 公元前10万年

        # Initialize agents
        self._initialize_agents(num_foragers, num_tribe_members, num_farmers)

    def _initialize_agents(self, num_foragers: int, num_tribe_members: int, num_farmers: int):
        """初始化Agent群体"""
        # Create Foragers
        for i in range(num_foragers):
            agent = Forager(self)
            pos = (self.random.random() * self.space.width,
                   self.random.random() * self.space.height)
            self.space.place_agent(agent, pos)
            agent.pos = pos

            self.social_graph.add_agent(agent.unique_id)
            self._agent_lookup[agent.unique_id] = agent

        # Create TribeMembers
        for i in range(num_tribe_members):
            agent = TribeMember(self)
            pos = (self.random.random() * self.space.width,
                   self.random.random() * self.space.height)
            self.space.place_agent(agent, pos)
            agent.pos = pos

            self.social_graph.add_agent(agent.unique_id)
            self._agent_lookup[agent.unique_id] = agent

        # Create Farmers
        for i in range(num_farmers):
            agent = Farmer(self)
            pos = (self.random.random() * self.space.width,
                   self.random.random() * self.space.height)
            self.space.place_agent(agent, pos)
            agent.pos = pos

            self.social_graph.add_agent(agent.unique_id)
            self._agent_lookup[agent.unique_id] = agent

        # Establish kinship network
        self._create_kinship_network()

    def _create_kinship_network(self):
        """创建血缘网络"""
        tribe_members = [a for a in self.agents if isinstance(a, (TribeMember, Farmer))]

        for i, agent in enumerate(tribe_members):
            for other in tribe_members[i+1:i+4]:
                dist = self._distance(agent.pos, other.pos)
                if dist < 20:
                    self.social_graph.add_edge(
                        agent.unique_id, other.unique_id,
                        RelationTypes.KINSHIP,
                        weight=1.0
                    )
                    self.social_graph.add_edge(
                        other.unique_id, agent.unique_id,
                        RelationTypes.KINSHIP,
                        weight=1.0
                    )

    def _distance(self, pos1: tuple, pos2: tuple) -> float:
        """计算两点间距离"""
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

    def _advance_year(self):
        """根据当前社会阶段推进年份

        目标时间线 (从公元前100,000年开始):
        - 原始群 -> 部落: ~10,000年
        - 部落 -> 早期国家: ~10,000年
        - 早期国家 -> 封建(公元500年): ~80,500年
        - 封建 -> 资本主义(1800年): ~1,300年
        - 资本主义 -> 社会主义(2000年): ~200年

        时间尺度:
        - 原始群、游群时期: 每步100年 (快进)
        - 部落、部落联盟、酋邦时期: 每步100年 (快进)
        - 早期国家: 每步500年 (快进)
        - 奴隶社会: 每步100年
        - 封建社会: 每步5年
        - 资本主义社会: 每步1个月
        - 社会主义社会: 每步1个月
        """
        if self.social_stage == SocialStage.PRIMITIVE_HORDE:
            # 原始群: 200年/步 (约500步到游群)
            self._current_year += 200
        elif self.social_stage == SocialStage.BAND:
            # 游群: 100年/步
            self._current_year += 100
        elif self.social_stage == SocialStage.TRIBE:
            # 部落: 100年/步
            self._current_year += 100
        elif self.social_stage == SocialStage.TRIBAL_CONFEDERACY:
            # 部落联盟: 100年/步
            self._current_year += 100
        elif self.social_stage == SocialStage.CHIEFDOM:
            # 酋邦: 100年/步
            self._current_year += 100
        elif self.social_stage == SocialStage.EARLY_STATE:
            # 早期国家: 500年/步 (快速跨越)
            self._current_year += 500
        elif self.social_stage == SocialStage.SLAVERY_STATE:
            # 奴隶社会: 100年/步
            self._current_year += 100
        elif self.social_stage == SocialStage.FEUDAL_STATE:
            # 封建社会: 5年/步
            self._current_year += 5
        else:
            # 资本主义和社会主义: 1个月/步
            self._current_year += 1  # 1个月

    def get_formatted_year(self) -> str:
        """获取格式化的年份字符串"""
        year = self._current_year
        if year <= 0:
            # 公元前
            return f"公元前{abs(year):,}年"
        else:
            return f"公元{year:,}年"

    def step(self):
        """模型步进"""
        # 0. Advance year based on current stage
        self._advance_year()

        # 1. Evaluate social stage transition
        new_stage = self.transition_engine.evaluate(self)
        if new_stage != self.social_stage:
            old_stage = self.social_stage
            self.social_stage = new_stage
            self._on_stage_transition(old_stage, new_stage)

        # 2. Update political subsystems based on current stage
        self._update_political_subsystems()

        # 资本主义阶段启用生产价格转换
        if self.social_stage == SocialStage.CAPITALIST_STATE:
            self.reproduction_engine.enable_production_price(True)
        else:
            self.reproduction_engine.enable_production_price(False)

        # 3. All agents act (资本主义阶段使用五步时序)
        if self.social_stage == SocialStage.CAPITALIST_STATE:
            self._step_capitalist_staged()
        else:
            for agent in list(self.agents):
                agent.step(self)

        # 3.5. Update population (births and deaths)
        self._update_population()

        # 4. Landscape regenerates
        self.landscape.regenerate()

        # 5. Detect crises
        crisis_data = self.reproduction_engine.detect_crisis(self)

        # 6. Collect data
        self.data_collector.collect()

        # 7. Take snapshots periodically
        if int(self.time) % self.snapshot_manager.snapshot_interval == 0:
            snap = Snapshot(self.model if hasattr(self, 'model') else self, int(self.time))
            snap.capture(self)
            self.snapshot_manager.add_snapshot(snap)

    def _step_capitalist_staged(self):
        """资本主义五步时序步进

        严格按照开发大纲附录 E 的时序：
        1. 生产(磨损转移)
        2. SNLT计算(触发精神磨损)
        3. 交换(价值实现)
        4. 阶级博弈
        5. 破产淘汰
        """
        from src.engine.labor_value import SNLTCalculator
        from src.engine.class_struggle import ClassStruggleEngine

        # 第一阶段：生产期 + 磨损转移
        for agent in list(self.agents):
            # Worker produces (driven by WageContractEdge)
            if isinstance(agent, Worker):
                agent._produce_labor(model=self)

            # Capitalist's machines undergo wear
            if isinstance(agent, Capitalist):
                from src.engine.depreciation import DepreciationEngine
                de = DepreciationEngine()
                for machine in agent.machines_owned[:]:
                    de.apply_wear_and_transfer_value(machine, production_quantity=1.0)
                    # Scrapped machines are removed
                    if machine.state == MatterState.STATE_USELESS:
                        agent.machines_owned.remove(machine)

        # 第二阶段：SNLT 事后裁决（触发精神磨损）
        for agent in list(self.agents):
            for commodity in agent.commodity_inventory[:]:
                if hasattr(commodity, 'exchange_status') and commodity.exchange_status == 'Pending':
                    sector = Matter.determine_sector(commodity)
                    snlt = SNLTCalculator.get_snlt(commodity.physical_props.get('name', 'craft_tool'))
                    if hasattr(commodity, 'individual_labor_embodied'):
                        # 个别劳动时间 > SNLT * 1.5 的会被淘汰
                        if commodity.individual_labor_embodied > snlt * 1.5:
                            commodity.physical_props['snlt_eliminated'] = True
                            commodity.state = MatterState.STATE_USELESS

        # 第三阶段：交换与价值实现（通过阻抗路由）
        router = ImpedanceRouter(self.social_graph)
        for agent in list(self.agents):
            for commodity in agent.commodity_inventory[:]:
                if commodity.state == MatterState.STATE_COMMODITY and commodity.exchange_status == 'Pending':
                    # 查找交换伙伴（简化：通过社会关系图）
                    if self.social_graph.graph.has_node(agent.unique_id):
                        try:
                            neighbors = list(self.social_graph.graph.predecessors(agent.unique_id))
                            for neighbor_id in neighbors:
                                neighbor = self.get_agent(neighbor_id)
                                if neighbor and isinstance(neighbor, (Worker, Capitalist)):
                                    self._force_delivery(agent, commodity, neighbor_id)
                                    router.record_exchange(
                                        agent.unique_id, neighbor_id,
                                        commodity.physical_props.get('name', 'unknown'), 1.0
                                    )
                                    break
                        except Exception:
                            pass

        # 第四阶段：阶级博弈期
        struggle_engine = ClassStruggleEngine()
        for agent in list(self.agents):
            if isinstance(agent, Capitalist):
                struggle_engine.consolidate_wage_struggle(agent, self)
            if isinstance(agent, Serf):
                struggle_engine.consolidate_rent_struggle(agent, self)

        # 第五阶段：SNLT断头台 - 淘汰落后者
        self._eliminate_uncompetitive()

    def _force_delivery(self, sender, commodity, receiver_id):
        """强制交割"""
        receiver = self.get_agent(receiver_id)
        if receiver and commodity in sender.commodity_inventory:
            sender.commodity_inventory.remove(commodity)
            commodity.exchange_status = 'Exchanged'
            receiver.commodity_inventory.append(commodity)

    def _eliminate_uncompetitive(self):
        """SNLT断头台：淘汰竞争力不足的资本家"""
        for agent in list(self.agents):
            if hasattr(agent, 'capital_stock') and hasattr(agent, 'workers_employed'):
                total_labor = len(agent.workers_employed) * 8.0
                if total_labor > agent.capital_stock * 2:
                    agent.capital_stock -= total_labor * 0.1
                    if agent.capital_stock <= 0:
                        self._eliminate_capitalist(agent)

        # 失业工人进入产业后备军
        for agent in list(self.agents):
            if hasattr(agent, 'employed_by') and agent.employed_by:
                employer = self.get_agent(agent.employed_by)
                if not employer or not hasattr(employer, 'capital_stock'):
                    agent.employed_by = None

    def _eliminate_capitalist(self, capitalist):
        """淘汰资本家，机器被其他资本家接管"""
        for machine in capitalist.machines_owned[:]:
            for other in list(self.agents):
                if other != capitalist and hasattr(other, 'machines_owned'):
                    other.machines_owned.append(machine)
                    break
        for worker_id in capitalist.workers_employed[:]:
            worker = self.get_agent(worker_id)
            if worker:
                worker.employed_by = None
        self.remove_agent(capitalist)

    def _update_political_subsystems(self):
        """更新政治子系统"""
        # Determine mode of production from social stage
        mode_map = {
            SocialStage.PRIMITIVE_HORDE: "primitive_communal",
            SocialStage.BAND: "primitive_communal",
            SocialStage.TRIBE: "primitive_communal",
            SocialStage.TRIBAL_CONFEDERACY: "primitive_communal",
            SocialStage.CHIEFDOM: "primitive_communal",
            SocialStage.EARLY_STATE: "slave_society",
            SocialStage.SLAVERY_STATE: "slave_society",
            SocialStage.FEUDAL_STATE: "feudalism",
            SocialStage.CAPITALIST_STATE: "capitalism",
            SocialStage.SOCIALIST_STATE: "socialism",
        }
        mode = mode_map.get(self.social_stage, "primitive_communal")

        # Update class forces
        class_forces = self._calculate_class_forces()

        # Update political regime
        self.political_regime.determine_regime(class_forces, mode)

        # Update state apparatus
        self.state_apparatus.check_state_form_transition(mode)
        if class_forces:
            dominant_class = max(class_forces.items(), key=lambda x: x[1])[0]
            self.state_apparatus.ruling_class = dominant_class

        # Update ideology manager
        crisis_level = self.reproduction_engine.crisis_indicators.get('department_imbalance', 0.0)
        self.ideology_manager.update_hegemony(mode, crisis_level)

    def _calculate_class_forces(self) -> dict:
        """计算阶级力量对比"""
        class_counts = self.data_collector.get_latest().get('class_distribution', {})
        total = sum(class_counts.values())
        if total == 0:
            return {}

        return {cls: count / total for cls, count in class_counts.items() if count > 0}

    def _on_stage_transition(self, old_stage: SocialStage, new_stage: SocialStage):
        """阶段转换时的处理"""
        print(f"\n*** Social Stage Transition: {old_stage.value} -> {new_stage.value} ***\n")

        if new_stage == SocialStage.SLAVERY_STATE:
            self._transition_to_slave_society()
        elif new_stage == SocialStage.FEUDAL_STATE:
            self._transition_to_feudalism()
        elif new_stage == SocialStage.CAPITALIST_STATE:
            self._capitalism_start_time = self.time
            self._transition_to_capitalism()
        elif new_stage == SocialStage.SOCIALIST_STATE:
            self._transition_to_socialism()

    def _transition_to_slave_society(self):
        """转换到奴隶社会 SLAVERY_STATE"""
        from src.model.agents import Slave, SlaveOwner

        # Create slave owners and slaves
        num_slave_owners = max(1, len(list(self.agents)) // 10)
        num_slaves = max(3, len(list(self.agents)) // 3)

        owners = []
        for i in range(num_slave_owners):
            owner = SlaveOwner(self)
            pos = (self.random.random() * self.space.width,
                   self.random.random() * self.space.height)
            self.space.place_agent(owner, pos)
            owner.pos = pos
            self.social_graph.add_agent(owner.unique_id)
            self._agent_lookup[owner.unique_id] = owner
            owners.append(owner)

        # Assign slaves to owners
        for i in range(num_slaves):
            slave = Slave(self)
            pos = (self.random.random() * self.space.width,
                   self.random.random() * self.space.height)
            self.space.place_agent(slave, pos)
            slave.pos = pos
            self.social_graph.add_agent(slave.unique_id)
            self._agent_lookup[slave.unique_id] = slave

            # Assign to an owner
            owner_idx = i % len(owners)
            owner = owners[owner_idx]
            owner.slaves_owned.append(slave.unique_id)
            # Create enslavement relation
            self.social_graph.add_edge(
                owner.unique_id, slave.unique_id,
                RelationTypes.ENSLAVEMENT,
                weight=1.0
            )

    def _transition_to_feudalism(self):
        """转换到封建社会 FEUDAL_STATE"""
        from src.model.agents import Serf, Lord

        # Convert some existing agents to serfs and create lords
        existing_agents = list(self.agents)
        num_lords = max(1, len(existing_agents) // 20)
        num_serfs = max(5, len(existing_agents) // 3)

        lords = []
        for i in range(num_lords):
            lord = Lord(self)
            pos = (self.random.random() * self.space.width,
                   self.random.random() * self.space.height)
            self.space.place_agent(lord, pos)
            lord.pos = pos
            self.social_graph.add_agent(lord.unique_id)
            self._agent_lookup[lord.unique_id] = lord
            lords.append(lord)

        # Assign peasants to lords
        for i in range(num_serfs):
            if i < len(existing_agents):
                # Convert existing agent to serf
                agent = existing_agents[i]
                if isinstance(agent, Human):
                    # Create new serf
                    serf = Serf(self)
                    # Handle case where agent.pos might be None
                    if agent.pos is not None:
                        serf.pos = agent.pos
                        self.space.place_agent(serf, agent.pos)
                    else:
                        # Use a random position if agent has no position
                        pos = (self.random.random() * self.space.width,
                               self.random.random() * self.space.height)
                        serf.pos = pos
                        self.space.place_agent(serf, pos)
                    serf.skill_type = 'farming'
                    self.social_graph.add_agent(serf.unique_id)
                    self._agent_lookup[serf.unique_id] = serf

                    # Remove old agent
                    self.remove_agent(agent)

                    # Assign to lord
                    lord_idx = i % len(lords)
                    lord = lords[lord_idx]
                    lord.serfs_controlled.append(serf.unique_id)

                    # 设置 serf 的 lord_id
                    serf.lord_id = lord.unique_id

                    # Create feudal rent relation
                    self.social_graph.add_edge(
                        serf.unique_id, lord.unique_id,
                        RelationTypes.FEUDAL_RENT,
                        weight=1.0
                    )

    def _transition_to_capitalism(self):
        """转换到资本主义社会 CAPITALIST_STATE

        创建资本家和工人，建立雇佣关系边。
        """
        from src.model.agents import Capitalist, Worker

        existing_agents = list(self.agents)
        total_pop = len(existing_agents)

        # 根据人口决定资本家和工人数量
        num_capitalists = max(2, total_pop // 50)
        num_workers = max(10, total_pop // 5)

        capitalists = []
        workers = []

        # 创建资本家
        for i in range(num_capitalists):
            capitalist = Capitalist(self)
            pos = (self.random.random() * self.space.width,
                   self.random.random() * self.space.height)
            self.space.place_agent(capitalist, pos)
            capitalist.pos = pos
            self.social_graph.add_agent(capitalist.unique_id)
            self._agent_lookup[capitalist.unique_id] = capitalist
            capitalists.append(capitalist)

        # 创建工人并建立雇佣关系
        for i in range(num_workers):
            worker = Worker(self)
            pos = (self.random.random() * self.space.width,
                   self.random.random() * self.space.height)
            self.space.place_agent(worker, pos)
            worker.pos = pos
            self.social_graph.add_agent(worker.unique_id)
            self._agent_lookup[worker.unique_id] = worker
            workers.append(worker)

            # 分配给资本家（轮询分配）
            capitalist_idx = i % len(capitalists)
            capitalist = capitalists[capitalist_idx]
            capitalist.workers_employed.append(worker.unique_id)
            worker.employed_by = capitalist.unique_id

            # 创建工资合同边（工人 -> 资本家）
            self.social_graph.add_edge(
                worker.unique_id, capitalist.unique_id,
                RelationTypes.WAGE_CONTRACT,
                weight=1.0
            )

    def _transition_to_socialism(self):
        """转换到社会主义社会 SOCIALIST_STATE

        将雇佣关系转换为计划分配关系。
        价值形式消亡，SNLT计算器停机。
        """
        from src.model.agents import Worker
        from src.model.relations import RelationTypes
        from src.engine.labor_value import SNLTCalculator

        # 启用社会主义模式 - 价值形式消亡
        SNLTCalculator.set_socialist_mode(True)

        existing_agents = list(self.agents)

        # 将所有资本家转换为管理者（保留但不占有剩余价值）
        for agent in existing_agents:
            if isinstance(agent, Worker):
                # 工人保持，但雇佣关系转为计划关系
                # 移除旧的 WAGE_CONTRACT 边
                if hasattr(agent, 'employed_by') and agent.employed_by:
                    # WAGE_CONTRACT 边会在社会图中被 PLANNING 边替代
                    pass

        # 创建 PLANNING 边（所有人 -> 规划中心，简化处理为环形）
        all_agents = list(self._agent_lookup.values())
        if len(all_agents) > 1:
            for i, agent in enumerate(all_agents):
                # 每个人与下一个人形成计划关系（环形）
                next_agent = all_agents[(i + 1) % len(all_agents)]
                self.social_graph.add_edge(
                    agent.unique_id, next_agent.unique_id,
                    RelationTypes.PLANNING,
                    weight=1.0
                )

    def remove_agent(self, agent):
        """移除Agent"""
        try:
            self.space.remove_agent(agent)
        except Exception:
            pass
        try:
            self.social_graph.remove_agent(agent.unique_id)
        except nx.NetworkXError:
            pass
        if agent.unique_id in self._agent_lookup:
            del self._agent_lookup[agent.unique_id]

        # Remove from special lists
        if hasattr(self, 'lords') and agent in self.lords:
            self.lords.remove(agent)
        if hasattr(self, 'serfs') and agent in self.serfs:
            self.serfs.remove(agent)

    def get_agent(self, agent_id: int):
        """获取Agent"""
        return self._agent_lookup.get(agent_id)

    def get_population_count(self) -> int:
        """获取总人口"""
        return len(self._agent_lookup)

    def get_average_subsistence(self) -> float:
        """获取平均生活资料满足率"""
        if not self._agent_lookup:
            return 0.0
        return sum(a.subsistence_satisfaction for a in self._agent_lookup.values()) / len(self._agent_lookup)

    def _update_population(self):
        """更新人口 - 处理出生和死亡"""
        agents = list(self._agent_lookup.values())
        births, deaths = self.demography_engine.calculate_population_change(agents, self)

        # 创建新生儿
        for _ in range(births):
            self._create_newborn()

        # 记录死亡（死亡由agent.step()中的remove_agent处理）

    def _create_newborn(self):
        """创建新生儿 - 根据当前社会阶段创建合适的Agent类型"""
        from src.model.agents import Forager, TribeMember, Slave, Serf, Worker

        # 根据当前阶段决定创建哪种Agent
        stage = self.social_stage

        if stage == SocialStage.PRIMITIVE_HORDE:
            agent = Forager(self)
        elif stage == SocialStage.BAND:
            # BAND阶段：社会组织更复杂，新生儿为TribeMember
            agent = TribeMember(self)
        elif stage == SocialStage.TRIBE:
            # 部落阶段：开始农业生产，新生儿为农民
            agent = Farmer(self)
        elif stage == SocialStage.TRIBAL_CONFEDERACY:
            agent = Farmer(self)
        elif stage == SocialStage.CHIEFDOM:
            agent = Farmer(self)
        elif stage == SocialStage.EARLY_STATE:
            agent = Farmer(self)
        elif stage == SocialStage.SLAVERY_STATE:
            # 奴隶社会：按比例创建奴隶主和奴隶
            if self.random.random() < 0.7:
                agent = Slave(self)
            else:
                agent = Slave(self)  # 简化：暂时都创建Slave
        elif stage == SocialStage.FEUDAL_STATE:
            agent = Serf(self)
        elif stage == SocialStage.CAPITALIST_STATE:
            agent = Worker(self)
        elif stage == SocialStage.SOCIALIST_STATE:
            agent = Worker(self)
        else:
            agent = Forager(self)

        # 放置新Agent
        pos = (self.random.random() * self.space.width,
               self.random.random() * self.space.height)
        self.space.place_agent(agent, pos)
        agent.pos = pos
        self.social_graph.add_agent(agent.unique_id)
        self._agent_lookup[agent.unique_id] = agent