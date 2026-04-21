"""
Tests for M5: Feudal Society Module

Validates:
- Serf and Lord mechanics
- FeudalRentRelation edge type
- Rent payment system
"""

import pytest
from src.model.agents import Serf, Lord
from src.model.ontology import Matter, MatterState, ItemTags
from src.model.relations import SocialRelationGraph, RelationTypes


class TestSerfMechanics:
    """测试农奴机制"""

    def test_serf_initial_state(self):
        """农奴初始状态"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)
        serf = Serf(model)

        assert serf.skill_type == 'farming'
        assert serf.rent_owed == 0.0
        assert serf.lord_id is None

    def test_serf_labor_capacity_recovers(self):
        """农奴劳动能力恢复"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)
        serf = Serf(model)
        serf.labor_power_capacity = 0.1

        serf.step(model)

        assert serf.labor_power_capacity > 0.1

    def test_serf_finds_lord_from_graph(self):
        """农奴从社会关系图找到领主"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)
        lord = Lord(model)
        serf = Serf(model)

        # 注册到模型
        model._agent_lookup[lord.unique_id] = lord
        model._agent_lookup[serf.unique_id] = serf
        model.lords.append(lord)

        # 添加封建地租关系
        model.social_graph.add_edge(
            serf.unique_id, lord.unique_id,
            RelationTypes.FEUDAL_RENT,
            weight=1.0
        )

        # 找到领主
        found_lord_id = serf._find_lord_from_graph(model)
        assert found_lord_id == lord.unique_id


class TestLordMechanics:
    """测试领主机制"""

    def test_lord_initial_state(self):
        """领主初始状态"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)
        lord = Lord(model)

        assert lord.skill_type == 'management'
        assert lord.skill_level == 1.5
        assert lord.serfs_controlled == []

    def test_lord_adds_serf(self):
        """领主添加农奴"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)
        lord = Lord(model)
        serf = Serf(model)

        lord.serfs_controlled.append(serf.unique_id)

        assert len(lord.serfs_controlled) == 1
        assert serf.unique_id in lord.serfs_controlled

    def test_lord_cleans_dead_serfs(self):
        """领主清理已死亡农奴"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)
        lord = Lord(model)
        serf = Serf(model)

        # 注册到模型（这样 get_agent 才能找到）
        model._agent_lookup[serf.unique_id] = serf
        model.lords.append(lord)

        # 添加一个已死亡的农奴和一个活着的农奴
        dead_serf_id = 99999
        lord.serfs_controlled.append(dead_serf_id)
        lord.serfs_controlled.append(serf.unique_id)

        lord._cleanup_dead_serfs(model)

        # dead_serf_id 被移除，只剩 serf
        assert len(lord.serfs_controlled) == 1
        assert serf.unique_id in lord.serfs_controlled


class TestFeudalRentRelation:
    """测试封建地租关系"""

    def test_feudal_rent_relation_exists(self):
        """封建地租关系类型存在"""
        assert RelationTypes.FEUDAL_RENT.value == "feudal_rent"

    def test_social_graph_add_feudal_rent(self):
        """社会图添加封建地租关系"""
        graph = SocialRelationGraph()
        graph.add_agent(1)  # lord
        graph.add_agent(2)  # serf

        graph.add_edge(2, 1, RelationTypes.FEUDAL_RENT, weight=1.0)

        relations = graph.get_relations(2)
        assert "feudal_rent" in relations

    def test_infer_class_position_serf(self):
        """推断农奴阶级位置"""
        graph = SocialRelationGraph()
        graph.add_agent(1)  # lord
        graph.add_agent(2)  # serf

        graph.add_edge(2, 1, RelationTypes.FEUDAL_RENT, weight=1.0)

        class_pos = graph.infer_class_position(2)
        assert class_pos == "serf"

    def test_infer_class_position_lord(self):
        """推断领主阶级位置"""
        graph = SocialRelationGraph()
        graph.add_agent(1)  # lord
        graph.add_agent(2)  # serf

        graph.add_edge(2, 1, RelationTypes.FEUDAL_RENT, weight=1.0)

        class_pos = graph.infer_class_position(1)
        assert class_pos == "lord"


class TestRentPayment:
    """测试地租支付"""

    def test_serf_pays_rent_to_lord(self):
        """农奴向领主支付地租"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)

        lord = Lord(model)
        serf = Serf(model)
        serf.lord_id = lord.unique_id

        # 注册到模型
        model._agent_lookup[lord.unique_id] = lord
        model._agent_lookup[serf.unique_id] = serf
        model.lords.append(lord)

        # 领主控制该农奴
        lord.serfs_controlled.append(serf.unique_id)

        # 模拟农奴有产品
        product = Matter()
        product.state = MatterState.STATE_PRODUCT
        product.individual_labor_embodied = 8.0
        product.physical_props = {'name': 'grain', 'tags': [ItemTags.EDIBLE]}
        serf.add_commodity(product)

        # 支付地租
        serf._pay_rent(model)

        # 25% 地租 = 1个产品
        # 领主应该收到产品
        assert len(lord.commodity_inventory) >= 1

    def test_serf_without_lord_does_not_crash(self):
        """没有领主的农奴不会崩溃"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)
        serf = Serf(model)
        serf.lord_id = None

        model._agent_lookup[serf.unique_id] = serf

        # 模拟有产品
        product = Matter()
        product.state = MatterState.STATE_PRODUCT
        product.individual_labor_embodied = 8.0
        serf.add_commodity(product)

        # 支付地租（没有领主，不应该崩溃）
        serf._pay_rent(model)

        # 产品应该还在农奴手中
        assert len(serf.commodity_inventory) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
