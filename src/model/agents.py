"""
Agents - Human Agent Base Class and Primitive Society Agents

BEHAVIORAL RED LINE: No "greed", "utility maximization", or "risk aversion"
in step() logic. Agent behavior is STRICTLY derived from SocialRelationGraph edges.
"""

from mesa import Agent
from typing import Optional, List
import random
import networkx as nx

from src.model.ontology import Matter, MatterState, ItemTags
from src.engine.production import ProductionSystem
from src.engine.labor_value import SNLTCalculator


class Human(Agent):
    """
    Human Agent 基类 - Base class for all human agents.

    Class position is inferred from SocialRelationGraph, not stored as attribute.
    """

    def __init__(self, model):
        super().__init__(model)

        # Skill attributes
        self.skill_level = 1.0
        self.skill_type: Optional[str] = None
        self.education_invested = 0.0
        self.training_remaining = 0

        # Labor capacity (normalized 0-1, represents daily available labor time)
        self.labor_power_capacity = 1.0

        # Economic attributes
        self.value_equivalent_held = 0.0
        self.commodity_inventory: List[Matter] = []
        self.subsistence_satisfaction = 1.0

        # Position in space
        self.pos = None

        # Production system reference
        self.production = ProductionSystem()

    def check_subsistence(self) -> bool:
        """检查是否满足生存需求"""
        return self.subsistence_satisfaction >= 0.8

    def consume_matter(self, matter: Matter) -> bool:
        """消费物品"""
        if matter.matches_need("edible"):
            if matter.state == MatterState.STATE_PURE_USE_VALUE:
                self.subsistence_satisfaction = min(1.0, self.subsistence_satisfaction + 0.3)
                matter.check_use_value_loss()
                return True
            elif matter.state in (MatterState.STATE_PRODUCT, MatterState.STATE_COMMODITY):
                self.subsistence_satisfaction = min(1.0, self.subsistence_satisfaction + 0.5)
                matter.check_use_value_loss()
                return True
        return False

    def gather_naturally(self, resource_patch: 'LandscapeCell'):
        """从自然界采集"""
        for matter in resource_patch.natural_matter:
            if matter.state == MatterState.STATE_PURE_USE_VALUE:
                if matter.matches_need("edible"):
                    if self.consume_matter(matter):
                        break

    def add_commodity(self, matter: Matter):
        """添加商品到库存"""
        self.commodity_inventory.append(matter)

    def step(self, model):
        """Agent step function"""
        pass


class Forager(Human):
    """原始社会早期采集者"""

    def step(self, model):
        """采集者的行为"""
        if self.pos and hasattr(model, 'landscape'):
            cell = model.landscape.get_cell_at(self.pos)
            if cell:
                self.gather_naturally(cell)

        self.subsistence_satisfaction = max(0.0, self.subsistence_satisfaction - 0.05)

        if self.subsistence_satisfaction <= 0:
            model.remove_agent(self)


class TribeMember(Human):
    """原始社会中晚期部落成员 - 可从事生产活动"""

    def step(self, model):
        """部落成员的行为"""
        # 恢复劳动能力（每天）
        self.labor_power_capacity = min(1.0, self.labor_power_capacity + 0.2)

        # 采集
        if self.pos and hasattr(model, 'landscape'):
            cell = model.landscape.get_cell_at(self.pos)
            if cell:
                self.gather_naturally(cell)

        # 尝试生产
        self._attempt_production(model)

        # 物物交换
        if hasattr(model, 'social_graph'):
            self._attempt_barter(model)

        self.subsistence_satisfaction = max(0.0, self.subsistence_satisfaction - 0.05)

        if self.subsistence_satisfaction <= 0:
            model.remove_agent(self)

    def _attempt_production(self, model):
        """尝试生产活动"""
        # 尝试制作工具
        if self.labor_power_capacity > 0.3:
            can_produce, reason = self.production.can_produce(self, 'craft_tool')
            if can_produce:
                tool = self.production.produce(self, 'craft_tool', model)
                if tool:
                    self.add_commodity(tool)
                    # 更新SNLT
                    SNLTCalculator.update_snlt('hand_tool', tool.individual_labor_embodied)

    def _attempt_barter(self, model):
        """尝试物物交换"""
        if self.unique_id not in model.social_graph.graph:
            return

        try:
            neighbors = list(model.social_graph.graph.successors(self.unique_id))
        except nx.NetworkXError:
            neighbors = []
        if not neighbors:
            try:
                neighbors = list(model.social_graph.graph.predecessors(self.unique_id))
            except nx.NetworkXError:
                neighbors = []

        for neighbor_id in neighbors[:3]:
            neighbor = model.get_agent(neighbor_id)
            if neighbor and isinstance(neighbor, TribeMember):
                self._exchange_with(neighbor)

    def _exchange_with(self, other: 'TribeMember'):
        """与另一成员交换物品"""
        if not self.commodity_inventory or not other.commodity_inventory:
            return

        my_goods = [m for m in self.commodity_inventory
                   if m.state == MatterState.STATE_COMMODITY]
        their_goods = [m for m in other.commodity_inventory
                      if m.state == MatterState.STATE_COMMODITY]

        if my_goods and their_goods:
            my_item = my_goods[0]
            their_item = their_goods[0]

            self.commodity_inventory.remove(my_item)
            other.commodity_inventory.remove(their_item)

            self.commodity_inventory.append(their_item)
            other.commodity_inventory.append(my_item)

            my_item.exchange_status = "Exchanged"
            their_item.exchange_status = "Exchanged"


class Farmer(TribeMember):
    """农业社会的农民 - 可耕种土地"""

    def __init__(self, model):
        super().__init__(model)
        self.skill_type = 'farming'
        self.skill_level = 1.2

    def _attempt_production(self, model):
        """农民的生产活动"""
        # 恢复劳动能力
        self.labor_power_capacity = min(1.0, self.labor_power_capacity + 0.2)

        # 采集
        if self.pos and hasattr(model, 'landscape'):
            cell = model.landscape.get_cell_at(self.pos)
            if cell:
                self.gather_naturally(cell)

        # 种植作物
        if self.labor_power_capacity > 0.4:
            can_produce, reason = self.production.can_produce(self, 'grain_grow')
            if can_produce:
                grain = self.production.produce(self, 'grain_grow', model)
                if grain:
                    self.add_commodity(grain)
                    SNLTCalculator.update_snlt('grain', grain.individual_labor_embodied)

        # 制作工具
        if self.labor_power_capacity > 0.3:
            can_produce, _ = self.production.can_produce(self, 'craft_tool')
            if can_produce:
                tool = self.production.produce(self, 'craft_tool', model)
                if tool:
                    self.add_commodity(tool)
                    SNLTCalculator.update_snlt('hand_tool', tool.individual_labor_embodied)


class Slave(Human):
    """奴隶社会的奴隶"""

    def __init__(self, model):
        super().__init__(model)
        self.subsistence_satisfaction = 0.5  # 奴隶生活资料满足率较低
        self.resistance_level = 0.0  # 抵抗程度
        self.forced_labor_done = 0.0  # 被迫完成的劳动

    def step(self, model):
        """奴隶的行为 - 被迫劳动"""
        # 恢复有限劳动能力
        self.labor_power_capacity = min(1.0, self.labor_power_capacity + 0.1)

        # 奴隶被迫劳动
        self._perform_forced_labor(model)

        # 只能获得极低限度的生存资料
        if self.subsistence_satisfaction < 0.4:
            self.subsistence_satisfaction = 0.4

        # 抵抗增加
        if self.subsistence_satisfaction < 0.3:
            self.resistance_level = min(1.0, self.resistance_level + 0.05)

        # 检查是否死亡
        if self.subsistence_satisfaction <= 0:
            model.remove_agent(self)

    def _perform_forced_labor(self, model):
        """被迫劳动 - 产出被剥夺"""
        if self.labor_power_capacity > 0.2:
            labor_output = self.labor_power_capacity * 0.8
            self.forced_labor_done += labor_output

            # 创建产品但立即被剥夺
            if hasattr(self, 'production') and self.production:
                product = self.production.produce(self, 'craft_tool', model)
                if product:
                    pass  # 产品被奴隶主占有 (由SlaveOwner的step处理)


class SlaveOwner(Human):
    """奴隶社会的奴隶主"""

    def __init__(self, model):
        super().__init__(model)
        self.slaves_owned: List[int] = []
        self.extraction_rate = 0.8  # 榨取率 80%

    def step(self, model):
        """奴隶主的行为 - 占有奴隶产出"""
        self.labor_power_capacity = min(1.0, self.labor_power_capacity + 0.1)

        # 剥削奴隶劳动
        self._extract_slave_surplus(model)

        # 消费
        self._consume_surplus()

    def _extract_slave_surplus(self, model):
        """榨取奴隶剩余"""
        for slave_id in self.slaves_owned[:]:
            slave = model.get_agent(slave_id)
            if slave and isinstance(slave, Slave):
                # 占有奴隶的产品
                for matter in slave.commodity_inventory[:]:
                    if model.random.random() < self.extraction_rate:
                        slave.commodity_inventory.remove(matter)
                        self.commodity_inventory.append(matter)

                # 奴隶被迫劳动的产品也在此被占有
                if slave.forced_labor_done > 0:
                    # 创建等价物代表奴隶劳动
                    extracted_value = slave.forced_labor_done * self.extraction_rate
                    slave.forced_labor_done = 0

    def _consume_surplus(self):
        """消费剩余"""
        for matter in self.commodity_inventory[:]:
            if self.consume_matter(matter):
                self.commodity_inventory.remove(matter)
                break

        # 剥削奴隶劳动
        for slave_id in self.slaves_owned[:]:
            slave = model.get_agent(slave_id)
            if slave and isinstance(slave, Slave):
                # 奴隶产出归奴隶主
                for matter in slave.commodity_inventory[:]:
                    slave.commodity_inventory.remove(matter)
                    self.commodity_inventory.append(matter)

        # 消费
        for matter in self.commodity_inventory[:]:
            if self.consume_matter(matter):
                self.commodity_inventory.remove(matter)
                break


class Serf(Human):
    """封建社会的农奴"""

    def __init__(self, model):
        super().__init__(model)
        self.skill_type = 'farming'
        self.rent_owed = 0.0

    def step(self, model):
        """农奴的行为"""
        self.labor_power_capacity = min(1.0, self.labor_power_capacity + 0.15)

        # 耕种自己的小块土地
        if self.labor_power_capacity > 0.5:
            self._attempt_production(model)

        # 上缴地租
        self._pay_rent(model)

        self.subsistence_satisfaction = max(0.0, self.subsistence_satisfaction - 0.03)

        if self.subsistence_satisfaction <= 0:
            model.remove_agent(self)

    def _pay_rent(self, model):
        """支付地租"""
        # 将部分产出交给领主
        goods_to_rent = [m for m in self.commodity_inventory[:] if m.state == MatterState.STATE_PRODUCT]
        if goods_to_rent:
            rent_quantity = len(goods_to_rent) // 4  # 25% 作为地租
            for i in range(rent_quantity):
                if goods_to_rent[i] in self.commodity_inventory:
                    self.commodity_inventory.remove(goods_to_rent[i])
                    # 找到领主并交付
                    if hasattr(model, 'lords'):
                        for lord in model.lords:
                            if lord.unique_id in self.social_graph.graph:
                                lord.add_commodity(goods_to_rent[i])
                                break


class Lord(Human):
    """封建社会的领主"""

    def __init__(self, model):
        super().__init__(model)
        self.skill_type = 'management'
        self.skill_level = 1.5
        self.serfs_controlled: List[int] = []

    def step(self, model):
        """领主的行为"""
        self.labor_power_capacity = min(1.0, self.labor_power_capacity + 0.1)

        # 消费从农奴那里获得的地租
        for matter in self.commodity_inventory[:]:
            if self.consume_matter(matter):
                self.commodity_inventory.remove(matter)
                break


class Worker(Human):
    """资本主义社会的工人"""

    def __init__(self, model):
        super().__init__(model)
        self.wage_rate = 8.0  # 劳动力价值（日工资）
        self.employed_by: Optional[int] = None  # 雇主ID

    def step(self, model):
        """工人的行为"""
        self.labor_power_capacity = min(1.0, self.labor_power_capacity + 0.2)

        # 被迫出卖劳动力
        if self.employed_by:
            employer = model.get_agent(self.employed_by)
            if employer:
                # 劳动完成后获得工资
                self.labor_power_capacity -= 0.8
                self.value_equivalent_held += self.wage_rate
                self.subsistence_satisfaction = min(1.0, self.subsistence_satisfaction + 0.3)

        # 消费
        self._consume_as_worker()

        if self.subsistence_satisfaction <= 0:
            model.remove_agent(self)

    def _consume_as_worker(self):
        """工人消费"""
        # 用工资购买生活资料
        if self.value_equivalent_held >= 8.0:
            matter = Matter()
            matter.state = MatterState.STATE_COMMODITY
            matter.physical_props = {
                'name': 'grain',
                'tags': [ItemTags.EDIBLE]
            }
            self.commodity_inventory.append(matter)
            self.value_equivalent_held -= 8.0

            # 消费
            self.consume_matter(matter)


class Capitalist(Human):
    """资本主义社会的资本家"""

    def __init__(self, model):
        super().__init__(model)
        self.skill_type = 'management'
        self.skill_level = 2.0
        self.capital_stock = 100.0  # 资本存量
        self.workers_employed: List[int] = []
        self.machines_owned: List[Matter] = []

    def step(self, model):
        """资本家的行为 - 盲目积累"""
        # 消费剩余价值
        self._consume_surplus()

        # 积累资本（扩大再生产）
        self._accumulate_capital(model)

        # 支付工资
        self._pay_wages(model)

    def _consume_surplus(self):
        """消费剩余价值"""
        if self.capital_stock > 50.0:
            matter = Matter()
            matter.state = MatterState.STATE_COMMODITY
            matter.physical_props = {
                'name': 'luxury_goods',
                'tags': [ItemTags.LUXURY]
            }
            self.commodity_inventory.append(matter)

    def _accumulate_capital(self, model):
        """积累资本"""
        # 购买机器（不变资本c）
        if self.capital_stock > 30.0:
            machine = Matter()
            machine.state = MatterState.STATE_COMMODITY
            machine.physical_props = {
                'name': 'machine',
                'tags': [ItemTags.TOOL],
                'means_of_production': True,
                'quantity': 1.0
            }
            machine.individual_labor_embodied = 20.0
            self.machines_owned.append(machine)
            self.capital_stock -= 30.0

    def _pay_wages(self, model):
        """支付工资"""
        for worker_id in self.workers_employed[:]:
            worker = model.get_agent(worker_id)
            if worker and isinstance(worker, Worker):
                if self.capital_stock >= worker.wage_rate:
                    self.capital_stock -= worker.wage_rate
                    worker.value_equivalent_held += worker.wage_rate