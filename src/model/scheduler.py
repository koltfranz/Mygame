"""
CapitalistStagedScheduler - 资本主义五步时序调度器

强制执行严格的五步时序（不可颠倒）：
1. 生产期：工人消耗劳动力，产出 Commodity (Pending)
2. SNLT 事后裁决
3. 阻抗路由与强制交割
4. 阶级博弈期
5. 淘汰期（SNLT断头台）

只有当社会阶段为 CAPITALIST_STATE 时才使用此调度器。
其他阶段使用标准的 RandomActivation。
"""

from mesa.time import BaseScheduler
from typing import List, Callable


class CapitalistStagedScheduler(BaseScheduler):
    """
    资本主义阶段调度器 - Enforces strict 5-step production cycle.

    严格时序确保：
    - 价值形式分析在交换之前完成
    - 阶级斗争在分配之前进行
    - 落后生产者被淘汰后才能进入下一轮生产
    """

    def __init__(self, model):
        super().__init__(model)
        self.stage_handlers: List[Callable] = []
        self.current_stage = 0
        self._setup_stages()

    def _setup_stages(self):
        """设置五步阶段处理器"""
        self.stage_handlers = [
            self._stage_production,
            self._stage_snlt_adjudication,
            self._stage_impedance_routing,
            self._stage_class_struggle,
            self._stage_elimination,
        ]

    def step(self):
        """执行一步调度 - 按五步顺序执行"""
        # 资本主义阶段才使用五步时序
        if self.model.social_stage.value != 'capitalist_state':
            # 非资本主义阶段，使用标准顺序
            for agent in list(self.agents):
                agent.step(self.model)
            self.time += 1
            return

        # 五步时序
        for stage_idx, handler in enumerate(self.stage_handlers):
            self.current_stage = stage_idx
            handler()

        self.time += 1

    def _stage_production(self):
        """第一阶段：生产期"""
        # 1. 所有工人进行生产
        for agent in list(self.agents):
            if hasattr(agent, 'employed_by') and agent.employed_by:
                # 工人在生产
                agent._produce_labor(model=self.model)

        # 2. 资本家积累不变资本（机器折旧）
        for agent in list(self.agents):
            if hasattr(agent, 'machines_owned'):
                for machine in agent.machines_owned[:]:
                    if hasattr(machine, 'check_use_value_loss'):
                        machine.check_use_value_loss()
                        if machine.state.value == 'useless':
                            agent.machines_owned.remove(machine)

    def _stage_snlt_adjudication(self):
        """第二阶段：SNLT 事后裁决"""
        from src.engine.labor_value import SNLTCalculator

        # 对所有 Pending 状态的商品进行 SNLT 裁决
        for agent in list(self.agents):
            for commodity in agent.commodity_inventory[:]:
                if hasattr(commodity, 'exchange_status') and commodity.exchange_status == 'Pending':
                    # SNLT 裁决：计算该部门的标准劳动时间
                    sector = getattr(commodity, 'sector', 'craft_tool')
                    snlt = SNLTCalculator.get_snlt(sector)

                    # 如果商品的实际劳动时间超过 SNLT，该商品价值受损
                    if hasattr(commodity, 'individual_labor_embodied'):
                        if commodity.individual_labor_embodied > snlt * 1.5:
                            # 标记为过时商品（SNLT断头台前兆）
                            commodity.physical_props['snlt_eliminated'] = True

    def _stage_impedance_routing(self):
        """第三阶段：阻抗路由与强制交割"""
        from src.engine.value_form_router import ImpedanceRouter

        router = ImpedanceRouter()

        # 对所有 Pending 商品进行阻抗路由
        for agent in list(self.agents):
            for commodity in agent.commodity_inventory[:]:
                if hasattr(commodity, 'exchange_status') and commodity.exchange_status == 'Pending':
                    # 计算最优路由
                    route = router.calculate_route(commodity, self.model)
                    if route:
                        # 强制交割
                        target = route.get('target')
                        if target:
                            self._force_delivery(agent, commodity, target)

    def _stage_class_struggle(self):
        """第四阶段：阶级博弈期"""
        from src.engine.class_struggle import ClassStruggleEngine

        struggle_engine = ClassStruggleEngine()

        # 执行阶级斗争：工资博弈、罢工、地租抵抗
        for agent in list(self.agents):
            if hasattr(agent, 'workers_employed'):
                # 资本家面临工资压力
                struggle_engine.consolidate_wage_struggle(agent, self.model)

            if hasattr(agent, 'lord_id'):
                # 农奴面临地租压力
                struggle_engine.consolidate_rent_struggle(agent, self.model)

    def _stage_elimination(self):
        """第五阶段：SNLT断头台 - 淘汰落后生产者"""
        from src.engine.labor_value import SNLTCalculator

        # 检查哪些资本家无法在 SNLT 阈值内完成生产
        for agent in list(self.agents):
            if hasattr(agent, 'capital_stock') and hasattr(agent, 'workers_employed'):
                # 计算资本家的平均生产效率
                total_labor = len(agent.workers_employed) * 8.0  # 假设每个工人每天劳动8小时

                # 如果劳动力成本超过资本家的承受力
                if total_labor > agent.capital_stock * 2:
                    # 资本家面临破产
                    agent.capital_stock -= total_labor * 0.1  # 亏损

                    # 如果资本耗尽，触发淘汰
                    if agent.capital_stock <= 0:
                        self._eliminate_capitalist(agent)

        # 检查哪些工人的工资无法被支付
        for agent in list(self.agents):
            if hasattr(agent, 'employed_by') and agent.employed_by:
                employer = self.model.get_agent(agent.employed_by)
                if employer and hasattr(employer, 'capital_stock'):
                    if employer.capital_stock < agent.wage_rate:
                        # 工人失业，进入产业后备军
                        agent.employed_by = None

    def _force_delivery(self, sender, commodity, receiver_id):
        """强制交割：商品从一方转移到另一方"""
        receiver = self.model.get_agent(receiver_id)
        if receiver and commodity in sender.commodity_inventory:
            sender.commodity_inventory.remove(commodity)
            commodity.exchange_status = 'Exchanged'
            receiver.commodity_inventory.append(commodity)

    def _eliminate_capitalist(self, capitalist):
        """淘汰资本家：其生产资料被其他资本家接管"""
        # 将机器分配给其他资本家
        for machine in capitalist.machines_owned[:]:
            # 找到另一个资本家
            for other in list(self.agents):
                if other != capitalist and hasattr(other, 'machines_owned'):
                    other.machines_owned.append(machine)
                    break

        # 工人失业
        for worker_id in capitalist.workers_employed[:]:
            worker = self.model.get_agent(worker_id)
            if worker:
                worker.employed_by = None

        # 移除资本家
        self.model.remove_agent(capitalist)

    def get_current_stage_name(self) -> str:
        """获取当前阶段名称"""
        stage_names = [
            '生产期',
            'SNLT裁决',
            '阻抗路由',
            '阶级博弈',
            '淘汰期'
        ]
        if 0 <= self.current_stage < len(stage_names):
            return stage_names[self.current_stage]
        return '未知'
