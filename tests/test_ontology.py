"""
Tests for Matter ontology and state transitions

Validates the four-state machine and use-value loss logic.
"""

import pytest
from src.model.ontology import Matter, MatterState, ItemTags


class TestMatterStateMachine:
    """测试物品四态机"""

    def test_initial_state_is_useless(self):
        """初始状态应为无用物"""
        matter = Matter()
        assert matter.state == MatterState.STATE_USELESS

    def test_pure_use_value_has_no_labor(self):
        """纯使用价值无劳动凝结"""
        matter = Matter()
        matter.state = MatterState.STATE_PURE_USE_VALUE
        matter.physical_props = {'name': 'berries', 'satisfies': ['edible']}
        matter.physical_props['tags'] = [ItemTags.EDIBLE]

        assert matter.individual_labor_embodied == 0.0
        assert matter.matches_need('edible')

    def test_product_has_labor(self):
        """产品有劳动凝结"""
        matter = Matter()
        matter.state = MatterState.STATE_PRODUCT
        matter.individual_labor_embodied = 5.0
        matter.physical_props = {'name': 'stone_tool', 'tags': [ItemTags.TOOL]}

        assert matter.individual_labor_embodied == 5.0
        assert matter.matches_need('tool')

    def test_commodity_exchange_status(self):
        """商品有待交换状态"""
        matter = Matter()
        matter.state = MatterState.STATE_COMMODITY
        matter.exchange_status = "Pending"

        assert matter.exchange_status == "Pending"

    def test_use_value_loss_check(self):
        """使用价值丧失检查"""
        matter = Matter()
        matter.state = MatterState.STATE_PURE_USE_VALUE
        matter.use_value_lifespan = 5

        # Simulate time passing
        for _ in range(5):
            result = matter.check_use_value_loss()

        assert matter.state == MatterState.STATE_USELESS

    def test_commodity_value_loss_triggers_event(self):
        """商品使用价值丧失时触发事件"""
        matter = Matter()
        matter.state = MatterState.STATE_COMMODITY
        matter.exchange_status = "Pending"
        matter.use_value_lifespan = 1

        from src.model.ontology import EventBus
        emitted_events = []

        def capture_event(data):
            emitted_events.append(data)

        EventBus.on('unrealized_commodity_value_loss', capture_event)

        matter.check_use_value_loss()

        assert len(emitted_events) == 1
        assert emitted_events[0] == matter


class TestItemTags:
    """测试物品标签"""

    def test_edible_tag(self):
        """可食用标签"""
        matter = Matter()
        matter.state = MatterState.STATE_PURE_USE_VALUE
        matter.physical_props = {'tags': [ItemTags.EDIBLE]}

        assert matter.matches_need('edible')

    def test_tool_tag(self):
        """工具标签"""
        matter = Matter()
        matter.state = MatterState.STATE_PRODUCT
        matter.physical_props = {'tags': [ItemTags.TOOL]}

        assert matter.matches_need('tool')


class TestSectorDetermination:
    """测试部类判定"""

    def test_determine_sector_money(self):
        """货币商品"""
        matter = Matter()
        matter.state = MatterState.STATE_COMMODITY
        matter.physical_props = {'tags': [ItemTags.MONEY_COMMODITY]}

        sector = Matter.determine_sector(matter)
        assert sector == "SECTOR_MONEY"

    def test_determine_sector_production_means(self):
        """生产资料"""
        matter = Matter()
        matter.state = MatterState.STATE_PRODUCT
        matter.physical_props = {'tags': [ItemTags.TOOL, ItemTags.RAW_MATERIAL]}

        sector = Matter.determine_sector(matter)
        assert sector == "SECTOR_I"

    def test_determine_sector_consumption(self):
        """消费资料"""
        matter = Matter()
        matter.state = MatterState.STATE_COMMODITY
        matter.physical_props = {'tags': [ItemTags.EDIBLE]}

        sector = Matter.determine_sector(matter)
        assert sector == "SECTOR_II"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
