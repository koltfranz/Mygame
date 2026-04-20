"""
Landscape - 地块系统 for resource allocation and natural matter

Represents the natural environment where use-values are extracted.
"""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass, field

from src.model.ontology import Matter, MatterState, ItemTags


@dataclass
class LandscapeCell:
    """
    景观地块 - A cell in the landscape.

    Contains naturally occurring matter (pure use-values)
    and can regenerate resources over time.
    """
    x: int
    y: int

    # Natural matter available for gathering
    natural_matter: List[Matter] = field(default_factory=list)

    # Resource regeneration parameters
    regeneration_rate: float = 0.1
    max_natural_items: int = 20

    # Cell productivity (affected by tech/tools)
    productivity: float = 1.0


class Landscape:
    """
    景观系统 - Landscape system for spatial resource allocation.

    Uses ContinuousSpace via Mesa but provides custom cell logic.
    """

    def __init__(self, width: int, height: int, num_cells_x: int = 20, num_cells_y: int = 20):
        self.width = width
        self.height = height
        self.num_cells_x = num_cells_x
        self.num_cells_y = num_cells_y

        self.cell_width = width / num_cells_x
        self.cell_height = height / num_cells_y

        # Create grid of cells
        self.cells: Dict[Tuple[int, int], LandscapeCell] = {}
        self._initialize_cells()

    def _initialize_cells(self):
        """初始化所有地块"""
        for x in range(self.num_cells_x):
            for y in range(self.num_cells_y):
                cell = LandscapeCell(x=x, y=y)
                self._populate_natural_matter(cell)
                self.cells[(x, y)] = cell

    def _populate_natural_matter(self, cell: LandscapeCell):
        """
        向地块填充自然物品 - Populate cell with naturally occurring matter.

        These are pure use-values from nature - no labor involved.
        """
        # Random number of natural items (0 to max)
        num_items = np.random.randint(0, cell.max_natural_items)

        for _ in range(num_items):
            matter = self._generate_natural_matter()
            cell.natural_matter.append(matter)

    def _generate_natural_matter(self) -> Matter:
        """生成随机自然物品"""
        matter = Matter()
        matter.state = MatterState.STATE_PURE_USE_VALUE

        # Random natural items: berries, water, wood, stone
        item_type = np.random.choice([
            'berries', 'water', 'wood', 'stone', 'roots', 'herbs'
        ])

        if item_type == 'berries':
            matter.physical_props = {
                'name': 'berries',
                'satisfies': ['edible'],
                'tags': [ItemTags.EDIBLE]
            }
            matter.use_value_lifespan = 20
        elif item_type == 'water':
            matter.physical_props = {
                'name': 'water',
                'satisfies': ['edible'],  # water satisfies thirst (edible)
                'tags': [ItemTags.EDIBLE]
            }
            matter.use_value_lifespan = 50
        elif item_type == 'wood':
            matter.physical_props = {
                'name': 'wood',
                'satisfies': ['tool', 'fuel'],
                'tags': [ItemTags.TOOL, ItemTags.RAW_MATERIAL]
            }
            matter.use_value_lifespan = 100
        elif item_type == 'stone':
            matter.physical_props = {
                'name': 'stone',
                'satisfies': ['tool'],
                'tags': [ItemTags.TOOL]
            }
            matter.use_value_lifespan = 150
        elif item_type == 'roots':
            matter.physical_props = {
                'name': 'roots',
                'satisfies': ['edible'],
                'tags': [ItemTags.EDIBLE]
            }
            matter.use_value_lifespan = 30
        elif item_type == 'herbs':
            matter.physical_props = {
                'name': 'herbs',
                'satisfies': ['edible', 'medicine'],
                'tags': [ItemTags.EDIBLE]
            }
            matter.use_value_lifespan = 15

        return matter

    def get_cell_at(self, pos: Tuple[float, float]) -> LandscapeCell:
        """获取位置对应的地块"""
        cell_x = min(self.num_cells_x - 1, max(0, int(pos[0] / self.cell_width)))
        cell_y = min(self.num_cells_y - 1, max(0, int(pos[1] / self.cell_height)))
        return self.cells.get((cell_x, cell_y))

    def regenerate(self):
        """
        资源再生 - Regenerate natural matter in all cells.

        Called periodically (e.g., each simulation step).
        """
        for cell in self.cells.values():
            # Random chance to regenerate
            if np.random.random() < cell.regeneration_rate:
                if len(cell.natural_matter) < cell.max_natural_items:
                    new_matter = self._generate_natural_matter()
                    cell.natural_matter.append(new_matter)

            # Remove expired matter
            cell.natural_matter = [
                m for m in cell.natural_matter
                if m.state != MatterState.STATE_USELESS
            ]
