"""
Tests for M4: Slave Society Module

Validates:
- Slave forced labor mechanics
- SlaveOwner extraction mechanics
- Resistance level effects
- EnslavementRelation edge type
"""

import pytest
from src.model.agents import Slave, SlaveOwner
from src.model.ontology import Matter, MatterState, ItemTags
from src.model.relations import SocialRelationGraph, RelationTypes


class TestSlaveMechanics:
    """测试奴隶 Mechanics"""

    def test_slave_initial_state(self):
        """奴隶初始状态"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)
        slave = Slave(model)

        assert slave.subsistence_satisfaction == 0.5
        assert slave.resistance_level == 0.0
        assert slave.forced_labor_done == 0.0

    def test_slave_labor_capacity_recovers_slowly(self):
        """奴隶劳动能力恢复较慢"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)
        slave = Slave(model)
        slave.labor_power_capacity = 0.1

        slave.step(model)

        # 奴隶恢复速度慢（0.1）
        assert slave.labor_power_capacity <= 0.2

    def test_slave_forced_labor_tracked(self):
        """奴隶被迫劳动被追踪"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)
        slave = Slave(model)
        slave.labor_power_capacity = 0.8

        slave._perform_forced_labor(model)

        assert slave.forced_labor_done > 0

    def test_slave_resistance_increases_low_subsistence(self):
        """奴隶生存资料极低时抵抗增加"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)
        slave = Slave(model)
        slave.subsistence_satisfaction = 0.25  # 极低，< 0.3
        slave.resistance_level = 0.0

        slave.step(model)

        # 抵抗检查在 clamp 之前，所以 0.25 < 0.3 会触发抵抗增加
        assert slave.resistance_level > 0


class TestSlaveOwnerExtraction:
    """测试奴隶主榨取机制"""

    def test_slaveowner_initial_state(self):
        """奴隶主初始状态"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)
        owner = SlaveOwner(model)

        assert owner.extraction_rate == 0.8
        assert owner.slaves_owned == []

    def test_slaveowner_extracts_slave_products(self):
        """奴隶主提取奴隶产品"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)

        owner = SlaveOwner(model)
        slave = Slave(model)

        # 注册到模型
        model._agent_lookup[slave.unique_id] = slave

        # 模拟奴隶有产品
        product = Matter()
        product.state = MatterState.STATE_PRODUCT
        product.individual_labor_embodied = 5.0
        slave.add_commodity(product)

        owner.slaves_owned.append(slave.unique_id)

        # 奴隶主提取
        owner._extract_slave_surplus(model)

        # 按 80% 提取率，至少提取了 1 个产品
        assert len(owner.commodity_inventory) >= 1

    def test_slaveowner_creates_value_equivalent(self):
        """奴隶主从奴隶劳动创建价值等价物"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)

        owner = SlaveOwner(model)
        slave = Slave(model)
        slave.forced_labor_done = 10.0

        # 注册到模型
        model._agent_lookup[slave.unique_id] = slave

        owner.slaves_owned.append(slave.unique_id)

        # 提取
        owner._extract_slave_surplus(model)

        # 创建了价值等价物
        extracted_matters = [m for m in owner.commodity_inventory
                           if m.physical_props.get('extracted_value')]
        assert len(extracted_matters) >= 1
        assert extracted_matters[0].individual_labor_embodied > 0


class TestEnslavementRelation:
    """测试奴役关系边类型"""

    def test_enslavement_relation_exists(self):
        """奴役关系类型存在"""
        assert RelationTypes.ENSLAVEMENT.value == "enslavement"

    def test_social_graph_add_enslavement(self):
        """社会图添加奴役关系"""
        graph = SocialRelationGraph()
        graph.add_agent(1)
        graph.add_agent(2)

        graph.add_edge(1, 2, RelationTypes.ENSLAVEMENT, weight=1.0)

        relations = graph.get_relations(2)
        assert "enslavement" in relations

    def test_infer_class_position_slave(self):
        """推断奴隶阶级位置"""
        graph = SocialRelationGraph()
        graph.add_agent(1)  # slave owner
        graph.add_agent(2)  # slave

        graph.add_edge(1, 2, RelationTypes.ENSLAVEMENT, weight=1.0)

        class_pos = graph.infer_class_position(2)
        assert class_pos == "slave"

    def test_infer_class_position_slave_owner(self):
        """推断奴隶主阶级位置"""
        graph = SocialRelationGraph()
        graph.add_agent(1)  # slave owner
        graph.add_agent(2)  # slave

        graph.add_edge(1, 2, RelationTypes.ENSLAVEMENT, weight=1.0)

        class_pos = graph.infer_class_position(1)
        assert class_pos == "slave_owner"


class TestSlaveResistanceEffect:
    """测试奴隶抵抗效果"""

    def test_resistance_reduces_labor_output(self):
        """抵抗降低实际劳动产出"""
        from src.model.model import CapitalModel
        model = CapitalModel(num_foragers=0, num_tribe_members=0)

        slave_low_resistance = Slave(model)
        slave_low_resistance.labor_power_capacity = 0.8
        slave_low_resistance.resistance_level = 0.0

        slave_high_resistance = Slave(model)
        slave_high_resistance.labor_power_capacity = 0.8
        slave_high_resistance.resistance_level = 0.8  # 高抵抗

        slave_low_resistance._perform_forced_labor(model)
        labor_low = slave_low_resistance.forced_labor_done

        slave_high_resistance._perform_forced_labor(model)
        labor_high = slave_high_resistance.forced_labor_done

        # 高抵抗的劳动产出更低
        assert labor_high < labor_low


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
