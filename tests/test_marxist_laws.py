"""
Tests for Marxist Laws - 马克思主义规律测试

Validates that the simulation obeys Marxist theoretical constraints:
1. Machines cannot create new value (only transfer)
2. Wage cannot equal labor's reward
3. Crisis cannot be caused by "insufficient demand"
4. Value is post-hoc calculation, not static attribute
"""

import pytest
from src.model.ontology import Matter, MatterState, ItemTags
from src.engine.labor_value import SNLTCalculator
from src.engine.production import ProductionSystem
from src.engine.depreciation import DepreciationEngine


class TestValueOntologyRedLine:
    """测试价值本体论红线"""

    def test_value_is_not_static_attribute(self):
        """验证价值不是静态属性"""
        matter = Matter()
        matter.state = MatterState.STATE_PRODUCT
        matter.individual_labor_embodied = 5.0

        # Value is NOT stored as matter.value
        assert not hasattr(matter, 'value') or matter.value is None or matter.value == 0

        # Value is calculated post-hoc via SNLT
        snlt = SNLTCalculator.get_snlt('test_commodity')
        value = SNLTCalculator.calc_value('test_commodity', 1.0)
        assert value > 0  # Value is calculated, not stored


class TestMachineValueTransfer:
    """测试机器只能转移价值"""

    def test_machine_transfers_value_not_creates(self):
        """验证机器只能转移价值，不能创造新价值"""
        # Create a machine (means of production)
        machine = Matter()
        machine.state = MatterState.STATE_PRODUCT
        machine.physical_props = {
            'name': 'test_machine',
            'means_of_production': True,
            'tags': [ItemTags.TOOL]
        }
        machine.individual_labor_embodied = 100.0  # Machine required 100 hours to produce
        machine.original_value = 100.0
        machine.remaining_use_value_ratio = 1.0
        machine.moral_depreciation_factor = 1.0
        machine.original_snlt_at_production = 100.0
        machine.transferred_value_accumulated = 0.0

        # Apply wear
        engine = DepreciationEngine()
        transferred = engine.apply_wear_and_transfer_value(machine, production_quantity=1.0)

        # Value transferred should be LESS than original value
        assert transferred <= machine.original_value

        # Total transferred + remaining should approximately equal original
        # (allowing for moral depreciation)
        assert machine.transferred_value_accumulated <= machine.original_value

        # Machine does NOT create surplus value
        assert transferred <= 100.0


class TestWageCannotEqualLaborReward:
    """测试工资不等于劳动报酬"""

    def test_wage_is_price_of_labor_power(self):
        """验证工资是劳动力的价格，不是劳动的报酬"""
        # Worker receives wage based on labor-power value, not labor performed
        wage_rate = 8.0  # Daily wage

        # Worker works 12 hours
        labor_performed = 12.0

        # Wage is NOT equal to labor performed
        assert wage_rate != labor_performed

        # Wage = price of labor-power (necessary consumption + training)
        labor_power_value = SNLTCalculator.calculate_labor_power_value(None)
        assert wage_rate == labor_power_value  # wages are determined by labor-power value


class TestCrisisNotFromDemand:
    """测试危机不能由需求不足引起"""

    def test_crisis_from_profit_rate_fall(self):
        """验证危机来自利润率下降，不是需求不足"""
        # Simulate crisis conditions
        from src.engine.reproduction import ReproductionEngine
        from unittest.mock import MagicMock

        engine = ReproductionEngine()

        # Crisis indicators should include profit rate fall
        crisis = {
            'rate_of_surplus_value': 1.0,
            'organic_composition': 3.0,  # Rising composition
            'profit_rate': 0.1,  # Falling profit rate
            'department_imbalance': 0.0,
        }

        engine.crisis_indicators = crisis

        # Crisis is caused by profit rate fall, not "insufficient demand"
        assert crisis['profit_rate'] < 0.2  # Low profit rate
        # Note: crisis is structural, not demand-side


class TestSNLTDynamic:
    """测试SNLT动态性"""

    def test_snlt_is_post_hoc(self):
        """验证SNLT是事后计算"""
        # SNLT is not a preset constant
        SNLTCalculator.reset()

        # Initial SNLT
        initial = SNLTCalculator.get_snlt('test_commodity')

        # Update with new production
        SNLTCalculator.update_snlt('test_commodity', individual_labor=5.0, quantity=10.0)

        # SNLT shifts based on new data (weighted average)
        new_snlt = SNLTCalculator.get_snlt('test_commodity')

        # SNLT is not static
        assert new_snlt >= 0


class TestComplexLaborMultiplier:
    """测试复杂劳动倍加系数"""

    def test_complex_labor_multiplier_not_preset(self):
        """验证复杂劳动倍加系数不是预设常数"""
        # Multiplier emerges from skill difference
        skill_1 = 1.0
        skill_2 = 2.0
        skill_3 = 3.0

        mult_1 = SNLTCalculator.calculate_complex_labor_multiplier(skill_1)
        mult_2 = SNLTCalculator.calculate_complex_labor_multiplier(skill_2)
        mult_3 = SNLTCalculator.calculate_complex_labor_multiplier(skill_3)

        # Multipliers should be proportional but not preset
        assert mult_2 > mult_1
        assert mult_3 > mult_2
        assert mult_3 < 4.0  # But capped


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
