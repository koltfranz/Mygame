"""
Production Functions - 生产函数系统

Implements production with:
- Concrete labor (具体劳动) transformation
- Skill requirements and dynamic skill calculation
- Production means depreciation and value transfer
"""

from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field

from src.model.ontology import Matter, MatterState, ItemTags


@dataclass
class ProductionRecipe:
    """生产配方 - Recipe for producing goods"""
    inputs: List[Tuple[str, float]] = field(default_factory=list)
    labor_time: float = 1.0
    skill_required: float = 1.0
    skill_type: Optional[str] = None
    tools_required: List[str] = field(default_factory=list)
    output: str = ""
    output_quantity: float = 1.0


class ProductionSystem:
    """
    生产系统 - Production system for transforming inputs to outputs.

    Concrete labor transforms raw materials into useful products.
    """

    # Default recipes for primitive agriculture and tools
    RECIPES = {
        'grain_grow': ProductionRecipe(
            inputs=[('seeds', 1.0)],
            labor_time=4.0,
            skill_required=1.0,
            skill_type='farming',
            tools_required=['hand_tool'],
            output='grain',
            output_quantity=3.0
        ),
        'craft_tool': ProductionRecipe(
            inputs=[('stone', 2.0), ('wood', 1.0)],
            labor_time=3.0,
            skill_required=1.5,
            skill_type='crafting',
            tools_required=['hand_tool'],
            output='hand_tool',
            output_quantity=1.0
        ),
        'craft_spear': ProductionRecipe(
            inputs=[('wood', 1.0), ('stone', 1.0)],
            labor_time=2.5,
            skill_required=1.2,
            skill_type='crafting',
            tools_required=['hand_tool'],
            output='weapon',
            output_quantity=1.0
        ),
        'build_shelter': ProductionRecipe(
            inputs=[('wood', 5.0), ('stone', 3.0)],
            labor_time=8.0,
            skill_required=1.0,
            skill_type='building',
            tools_required=['hand_tool'],
            output='shelter',
            output_quantity=1.0
        ),
    }

    def __init__(self):
        self.recipes = self.RECIPES.copy()

    def calculate_skill_requirement(self,
                                    sector: str,
                                    tech_knowledge: float,
                                    tool_quality: float,
                                    avg_worker_skill: float) -> float:
        """
        动态计算技能要求 - Calculate skill requirement dynamically.

        skill_requirement = f(tech_knowledge, tool_quality, avg_worker_skill)
        NOT a fixed constant.
        """
        base_requirement = 1.0

        # Higher tech knowledge -> higher skill requirement
        tech_factor = tech_knowledge * 0.5

        # Better tools reduce skill requirement
        tool_factor = (1.0 - tool_quality * 0.3)

        # Workers with higher skill can meet higher requirements
        skill_factor = avg_worker_skill * 0.2

        requirement = base_requirement + tech_factor - tool_factor + skill_factor
        return max(0.5, requirement)  # Minimum skill of 0.5

    def can_produce(self, agent, recipe_name: str) -> Tuple[bool, str]:
        """
        检查是否可以生产 - Check if agent can produce given recipe.
        """
        if recipe_name not in self.recipes:
            return False, f"Unknown recipe: {recipe_name}"

        recipe = self.recipes[recipe_name]

        # Check skill requirement
        if agent.skill_level < recipe.skill_required:
            return False, f"Insufficient skill: {agent.skill_level} < {recipe.skill_required}"

        # Check skill type if required
        if recipe.skill_type and agent.skill_type != recipe.skill_type:
            return False, f"Wrong skill type: {agent.skill_type} != {recipe.skill_type}"

        # Check labor capacity
        if agent.labor_power_capacity < recipe.labor_time:
            return False, f"Insufficient labor capacity"

        # Check for tools (if agent has any tool in inventory)
        if recipe.tools_required:
            has_tool = any(
                m.physical_props.get('tags', []) and
                any(t.value in [tag.value for tag in m.physical_props.get('tags', [])]
                    for t in recipe.tools_required)
                for m in agent.commodity_inventory
            )
            if not has_tool:
                return False, f"Missing required tools: {recipe.tools_required}"

        return True, "OK"

    def produce(self, agent, recipe_name: str, model) -> Optional[Matter]:
        """
        执行生产 - Execute production.

        Returns the produced Matter, or None if production failed.
        """
        can_proceed, reason = self.can_produce(agent, recipe_name)
        if not can_proceed:
            return None

        recipe = self.recipes[recipe_name]

        # Consume inputs from agent's inventory
        self._consume_inputs(agent, recipe.inputs)

        # Consume labor time
        agent.labor_power_capacity -= recipe.labor_time / 24.0  # Normalize to days

        # Create output product
        product = Matter()
        product.state = MatterState.STATE_PRODUCT
        product.individual_labor_embodied = recipe.labor_time
        product.physical_props = {
            'name': recipe.output,
            'quantity': recipe.output_quantity,
            'tags': self._get_tags_for_output(recipe.output)
        }

        # If product is a tool/means of production, set depreciation attributes
        if recipe.output in ['hand_tool', 'weapon']:
            product.physical_props['means_of_production'] = True
            product.physical_wear_rate = 0.01
            product.idle_wear_rate = 0.001
            product.remaining_use_value_ratio = 1.0
            product.original_value = recipe.labor_time  # Value = labor time
            product.original_snlt_at_production = recipe.labor_time

        return product

    def _consume_inputs(self, agent, inputs: List[Tuple[str, float]]):
        """消费投入品"""
        for input_type, quantity in inputs:
            consumed = 0.0
            for matter in agent.commodity_inventory[:]:
                if matter.physical_props.get('name') == input_type:
                    if consumed >= quantity:
                        break
                    # Partially consume
                    if matter.physical_props.get('quantity', 1.0) <= quantity - consumed:
                        consumed += matter.physical_props.get('quantity', 1.0)
                        agent.commodity_inventory.remove(matter)
                    else:
                        # Reduce quantity
                        matter.physical_props['quantity'] -= (quantity - consumed)
                        consumed = quantity

    def _get_tags_for_output(self, output: str) -> List[ItemTags]:
        """获取产出的标签"""
        tag_map = {
            'grain': [ItemTags.EDIBLE, ItemTags.SEED],
            'hand_tool': [ItemTags.TOOL],
            'weapon': [ItemTags.WEAPON],
            'shelter': [ItemTags.TOOL],  # Can be used as tool
        }
        return tag_map.get(output, [])