"""
Depreciation - 生产资料磨损与价值转移

Handles:
- Physical wear (有形磨损)
- Moral depreciation (精神磨损)
- Value transfer to new products
"""

from src.model.ontology import Matter, EventBus


class DepreciationEngine:
    """
    磨损与价值转移引擎 - Depreciation and value transfer engine.

    Machines cannot create new value - they can only transfer their own value
    to the products they help create.
    """

    def __init__(self):
        self.event_listeners = {
            'means_of_production_scrapped': [],
        }

    def apply_wear_and_transfer_value(self, machine: Matter, production_quantity: float = 1.0) -> float:
        """
        应用磨损并转移价值 - Apply wear and transfer value to products.

        Returns the value transferred to the products in this production cycle.

        Following the outline spec:
        value_transferred = original_value * effective_wear - transferred_value_accumulated
        where effective_wear = 1 - (remaining_use_value_ratio * moral_factor)
        """
        if not machine.physical_props.get('means_of_production'):
            return 0.0

        # Physical wear (usage)
        physical_wear = machine.physical_wear_rate * production_quantity

        # Idle wear (time decay)
        idle_wear = machine.idle_wear_rate

        total_wear = physical_wear + idle_wear

        # Calculate moral depreciation factor
        # If SNLT in this sector has decreased, machine loses value
        current_snlt = self._get_current_snlt(machine)
        original_snlt = machine.original_snlt_at_production

        if original_snlt > 0:
            moral_factor = current_snlt / original_snlt
        else:
            moral_factor = 1.0

        # Clamp moral factor (outline spec: no lower bound except 0.01)
        machine.moral_depreciation_factor = max(0.01, moral_factor)

        # Update remaining use value ratio
        machine.remaining_use_value_ratio -= total_wear

        # Calculate effective wear (combining physical and moral) - following outline spec
        # effective_wear = 1 - (remaining_use_value_ratio * moral_factor)
        effective_wear = 1.0 - (machine.remaining_use_value_ratio * machine.moral_depreciation_factor)

        # Calculate value transferred per outline spec:
        # transferred = original_value * effective_wear - transferred_value_accumulated
        if machine.original_value > 0:
            value_transferred = machine.original_value * effective_wear - machine.transferred_value_accumulated
        else:
            value_transferred = machine.individual_labor_embodied * effective_wear - machine.transferred_value_accumulated

        # Accumulate transferred value
        machine.transferred_value_accumulated += max(0.0, value_transferred)

        # Check for scrappage
        if machine.remaining_use_value_ratio <= 0 or machine.moral_depreciation_factor <= 0.01:
            self._scrapp_machine(machine)

        return max(0.0, value_transferred)

    def _get_current_snlt(self, machine: Matter) -> float:
        """获取当前部门SNLT"""
        from src.engine.labor_value import SNLTCalculator

        # Determine sector from machine type
        sector = Matter.determine_sector(machine)
        commodity_type = machine.physical_props.get('name', 'unknown')

        return SNLTCalculator.get_snlt(commodity_type)

    def _scrapp_machine(self, machine: Matter):
        """报废生产资料"""
        from src.model.ontology import MatterState
        machine.state = MatterState.STATE_USELESS
        machine.individual_labor_embodied = 0.0

        # Emit scrappage event
        EventBus.emit('means_of_production_scrapped', machine)

    def check_use_value_loss(self, matter: Matter) -> bool:
        """
        检查使用价值丧失 - Check use-value loss.

        Returns True if matter lost use-value.
        """
        return matter.check_use_value_loss()