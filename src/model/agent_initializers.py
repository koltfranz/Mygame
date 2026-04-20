"""
Agent Initializer - Agent 初始化工厂

Factory for creating agents with proper class-specific initialization.
"""

from typing import List, Tuple


class AgentInitializer:
    """
    Agent 初始化工厂 - Factory for creating properly initialized agents.

    Handles:
    - Initial agent distribution by mode of production
    - Class-specific attribute initialization
    - Social relation establishment
    """

    @staticmethod
    def create_primitive_society(model, num_foragers: int, num_tribe_members: int) -> List:
        """创建原始社会Agent"""
        from src.model.agents import Forager, TribeMember

        agents = []

        for _ in range(num_foragers):
            agent = Forager(model)
            agent.subsistence_satisfaction = 1.0
            agents.append(agent)

        for _ in range(num_tribe_members):
            agent = TribeMember(model)
            agent.subsistence_satisfaction = 1.0
            agents.append(agent)

        return agents

    @staticmethod
    def create_slave_society(model, num_slaves: int, num_owners: int) -> Tuple[List, List]:
        """创建奴隶社会Agent"""
        from src.model.agents import Slave, SlaveOwner

        slaves = []
        owners = []

        for _ in range(num_slaves):
            slave = Slave(model)
            slave.subsistence_satisfaction = 0.5  # 奴隶低满足率
            slaves.append(slave)

        for _ in range(num_owners):
            owner = SlaveOwner(model)
            owner.subsistence_satisfaction = 1.0
            owners.append(owner)

        return slaves, owners

    @staticmethod
    def create_feudal_society(model, num_peasants: int, num_lords: int) -> Tuple[List, List]:
        """创建封建社会Agent"""
        from src.model.agents import Serf, Lord

        serfs = []
        lords = []

        for _ in range(num_peasants):
            serf = Serf(model)
            serf.subsistence_satisfaction = 0.6
            serf.skill_type = 'farming'
            serfs.append(serf)

        for _ in range(num_lords):
            lord = Lord(model)
            lord.subsistence_satisfaction = 0.9
            lord.skill_type = 'management'
            lords.append(lord)

        return serfs, lords

    @staticmethod
    def create_capitalist_society(model, num_workers: int, num_capitalists: int) -> Tuple[List, List]:
        """创建资本主义社会Agent"""
        from src.model.agents import Worker, Capitalist

        workers = []
        capitalists = []

        for _ in range(num_workers):
            worker = Worker(model)
            worker.subsistence_satisfaction = 0.7
            workers.append(worker)

        for _ in range(num_capitalists):
            capitalist = Capitalist(model)
            capitalist.subsistence_satisfaction = 1.0
            capitalist.capital_stock = 100.0
            capitalists.append(capitalist)

        return workers, capitalists

    @staticmethod
    def distribute_land(serfs: List, lords: List, land_per_serf: float = 5.0):
        """分配土地 - 给农奴分配小块土地"""
        for serf in serfs:
            serf.land_holding = land_per_serf

    @staticmethod
    def establish_relations(model, agents, relation_type, bidirectional: bool = True):
        """建立社会关系"""
        from src.model.relations import RelationTypes

        for i, agent in enumerate(agents):
            # Connect to nearby agents
            for other in agents[i+1:i+4]:
                dist = ((agent.pos[0] - other.pos[0])**2 +
                       (agent.pos[1] - other.pos[1])**2)**0.5

                if dist < 30:
                    model.social_graph.add_edge(
                        agent.unique_id, other.unique_id,
                        relation_type, weight=1.0
                    )
                    if bidirectional:
                        model.social_graph.add_edge(
                            other.unique_id, agent.unique_id,
                            relation_type, weight=1.0
                        )