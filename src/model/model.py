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
from src.analysis.data_collector import DataCollector
from src.engine.reproduction import ReproductionEngine


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

        # Data collector
        self.data_collector = DataCollector(self)

        # Track agents for lookup
        self._agent_lookup: dict = {}
        self.lords: list = []
        self.serfs: list = []

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

    def step(self):
        """模型步进"""
        # 1. Evaluate social stage transition
        new_stage = self.transition_engine.evaluate(self)
        if new_stage != self.social_stage:
            old_stage = self.social_stage
            self.social_stage = new_stage
            self._on_stage_transition(old_stage, new_stage)

        # 2. All agents act
        for agent in list(self.agents):
            agent.step(self)

        # 3. Landscape regenerates
        self.landscape.regenerate()

        # 4. Detect crises
        crisis_data = self.reproduction_engine.detect_crisis(self)

        # 5. Collect data
        self.data_collector.collect()

    def _on_stage_transition(self, old_stage: SocialStage, new_stage: SocialStage):
        """阶段转换时的处理"""
        print(f"\n*** Social Stage Transition: {old_stage.value} -> {new_stage.value} ***\n")

        if new_stage == SocialStage.SLAVERY_STATE:
            self._transition_to_slave_society()
        elif new_stage == SocialStage.FEUDAL_STATE:
            self._transition_to_feudalism()

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
                    serf.pos = agent.pos
                    serf.skill_type = 'farming'
                    self.space.place_agent(serf, agent.pos)
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