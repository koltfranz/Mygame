"""
Tests for Social Stage Framework (v10.2)

Tests the new 10-stage Service-Fried framework:
- SocialStage enum values
- TransitionEngine metrics calculation
- Stage transition conditions
"""

import pytest
from src.model.social_stage import SocialStage, TransitionEngine, StageMetrics
from src.model.relations import RelationTypes
from src.model.model import CapitalModel


class TestSocialStageEnum:
    """测试社会阶段枚举"""

    def test_all_10_stages_exist(self):
        """验证所有10个阶段存在"""
        expected_stages = [
            'primitive_horde', 'band', 'tribe', 'tribal_confederacy',
            'chiefdom', 'early_state', 'slavery_state', 'feudal_state',
            'capitalist_state', 'socialist_state'
        ]
        actual_values = [stage.value for stage in SocialStage]
        for expected in expected_stages:
            assert expected in actual_values, f"Missing stage: {expected}"

    def test_stage_order(self):
        """测试阶段顺序"""
        stages = list(SocialStage)
        # 前6个是原始社会阶段
        assert stages[0] == SocialStage.PRIMITIVE_HORDE
        assert stages[5] == SocialStage.EARLY_STATE


class TestTransitionEngine:
    """测试转型引擎"""

    def test_engine_initialization(self):
        """测试引擎初始化"""
        engine = TransitionEngine()
        assert engine.current_stage == SocialStage.PRIMITIVE_HORDE

    def test_collect_metrics(self):
        """测试指标收集"""
        model = CapitalModel(width=50, height=50, num_foragers=20, num_tribe_members=20)
        engine = TransitionEngine()
        metrics = engine._collect_metrics(model)

        assert isinstance(metrics, StageMetrics)
        assert metrics.population > 0

    def test_calculate_surplus_ratio(self):
        """测试剩余生产率计算"""
        model = CapitalModel(width=50, height=50, num_foragers=10, num_tribe_members=10)
        engine = TransitionEngine()
        ratio = engine._calculate_surplus_ratio(model)
        assert isinstance(ratio, float)

    def test_calculate_stratification(self):
        """测试社会分化度计算"""
        model = CapitalModel(width=50, height=50, num_foragers=10, num_tribe_members=10)
        engine = TransitionEngine()
        strat = engine._calculate_stratification(model)
        assert isinstance(strat, float)
        assert 0.0 <= strat <= 1.0

    def test_calculate_density(self):
        """测试人口密度计算"""
        model = CapitalModel(width=50, height=50, num_foragers=10, num_tribe_members=10)
        engine = TransitionEngine()
        density = engine._calculate_density(model)
        assert isinstance(density, float)
        assert 0.0 <= density <= 1.0


class TestStageMetrics:
    """测试阶段指标数据类"""

    def test_metrics_initialization(self):
        """测试指标初始化"""
        metrics = StageMetrics()
        assert metrics.population == 0
        assert metrics.surplus_ratio == 0.0
        assert metrics.fire_use == False


class TestRelationTypes:
    """测试关系边类型"""

    def test_12_relation_types_exist(self):
        """验证12种关系边类型存在"""
        expected = [
            'kinship', 'clan', 'barter', 'tributary', 'military_service',
            'residence', 'enslavement', 'feudal_rent', 'wage_contract',
            'training', 'colonial_extraction', 'planning'
        ]
        actual = [rt.value for rt in RelationTypes]
        for e in expected:
            assert e in actual, f"Missing relation type: {e}"

    def test_relation_type_count(self):
        """验证关系类型数量"""
        assert len(RelationTypes) == 12


class TestSocialGraphInference:
    """测试社会关系图推断"""

    def test_infer_band_member(self):
        """测试游群成员推断"""
        model = CapitalModel(width=50, height=50, num_foragers=5, num_tribe_members=5)
        agent_id = list(model._agent_lookup.keys())[0]

        # 游群阶段应该推断为 band_member
        model.social_stage = SocialStage.BAND

        # 添加 kinship 边
        other_id = list(model._agent_lookup.keys())[1]
        model.social_graph.add_edge(agent_id, other_id, RelationTypes.KINSHIP, weight=1.0)

        class_pos = model.social_graph.infer_class_position(agent_id)
        assert class_pos == 'band_member'

    def test_infer_tribesman(self):
        """测试部落成员推断"""
        model = CapitalModel(width=50, height=50, num_foragers=5, num_tribe_members=5)
        agent_id = list(model._agent_lookup.keys())[0]

        model.social_stage = SocialStage.TRIBE

        # 添加 clan 边
        other_id = list(model._agent_lookup.keys())[1]
        model.social_graph.add_edge(agent_id, other_id, RelationTypes.CLAN, weight=1.0)

        class_pos = model.social_graph.infer_class_position(agent_id)
        assert class_pos == 'tribesman'


class TestStageTransition:
    """测试阶段转换"""

    def test_evaluate_returns_current_stage(self):
        """测试评估返回当前阶段"""
        model = CapitalModel(width=50, height=50, num_foragers=10, num_tribe_members=10)
        engine = TransitionEngine()

        new_stage = engine.evaluate(model)
        assert new_stage in SocialStage

    def test_stage_info(self):
        """测试阶段信息获取"""
        engine = TransitionEngine()
        info = engine.get_stage_info()

        assert 'name' in info
        assert 'population' in info
        assert 'time_scale' in info
        assert 'core_relation' in info
        assert 'power_structure' in info

    def test_get_current_stage(self):
        """测试获取当前阶段"""
        engine = TransitionEngine()
        stage = engine.get_current_stage()
        assert stage == SocialStage.PRIMITIVE_HORDE


class TestDataCollectorExtended:
    """测试扩展的数据收集器"""

    def test_collect_includes_social_stage(self):
        """测试收集包含社会阶段"""
        model = CapitalModel(width=50, height=50, num_foragers=10, num_tribe_members=10)
        model.step()

        latest = model.data_collector.get_latest()
        assert 'social_stage' in latest
        assert latest['social_stage'] in [s.value for s in SocialStage]

    def test_collect_includes_transition_indicators(self):
        """测试收集包含跃迁指标"""
        model = CapitalModel(width=50, height=50, num_foragers=10, num_tribe_members=10)
        model.step()

        latest = model.data_collector.get_latest()
        assert 'transition_indicators' in latest

        indicators = latest['transition_indicators']
        assert 'surplus_ratio' in indicators
        assert 'stratification' in indicators
        assert 'density' in indicators

    def test_collect_includes_economic_metrics(self):
        """测试收集包含经济指标"""
        model = CapitalModel(width=50, height=50, num_foragers=10, num_tribe_members=10)
        model.step()

        latest = model.data_collector.get_latest()
        assert 'economic_metrics' in latest

        metrics = latest['economic_metrics']
        assert 'avg_inventory' in metrics
        assert 'avg_labor_capacity' in metrics
        assert 'avg_skill_level' in metrics


if __name__ == '__main__':
    pytest.main([__file__, '-v'])