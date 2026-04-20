"""
Matter - The Four-State Machine for CapitalSimulator

ONTOLOGICAL RED LINE: Value and use-value are NEVER static attributes.
Use-value is a dynamic matching event. Value is a post-hoc ghost ratio (SNLT).
"""

from enum import Enum
from typing import Dict, Optional, Set
from dataclasses import dataclass, field
import uuid


class MatterState(Enum):
    """物品四态机 - Four states of matter in the Marxist simulation"""
    STATE_USELESS = "useless"           # 无用物
    STATE_PURE_USE_VALUE = "pure_use"   # 纯使用价值
    STATE_PRODUCT = "product"           # 产品
    STATE_COMMODITY = "commodity"       # 商品


class ItemTags(Enum):
    """物品职能标签 - Functional tags for matter"""
    EDIBLE = "edible"                   # 可食用
    SEED = "seed"                       # 可作为种子
    TOOL = "tool"                       # 可作为工具
    RAW_MATERIAL = "raw_material"       # 可作为原料
    LUXURY = "luxury"                   # 奢侈品属性
    MONEY_COMMODITY = "money_commodity" # 货币商品属性
    WEAPON = "weapon"                   # 武器
    LOCATION_CHANGE = "location_change"  # 运输服务


@dataclass
class Matter:
    """
    物质团块 - Any mass of matter in the simulation.

    CRITICAL: value and use_value are NOT stored as static attributes.
    - use_value is determined dynamically via matches_need()
    - value is post-hoc calculated as SNLT ghost ratio
    """
    unique_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # State machine
    state: MatterState = MatterState.STATE_USELESS

    # Physical properties (what it IS, not what it's WORTH)
    physical_props: Dict[str, any] = field(default_factory=dict)

    # Individual labor embodied (凝结的私人劳动)
    individual_labor_embodied: float = 0.0

    # Exchange status (for commodities)
    exchange_status: Optional[str] = None  # "Pending" or None

    # Use-value lifespan (turns until decay)
    use_value_lifespan: int = 100

    # === Production Means Specific Attributes ===
    # 生产资料特有属性 - only present when physical_props["means_of_production"] is True
    physical_wear_rate: float = 0.0
    idle_wear_rate: float = 0.0
    remaining_use_value_ratio: float = 1.0
    moral_depreciation_factor: float = 1.0
    original_value: float = 0.0
    transferred_value_accumulated: float = 0.0
    original_snlt_at_production: float = 0.0

    def matches_need(self, need_type: str) -> bool:
        """
        动态判定使用价值 - Dynamic use-value matching.
        This is an EVENT, not a static property.
        """
        if self.state == MatterState.STATE_USELESS:
            return False
        if self.state == MatterState.STATE_PURE_USE_VALUE:
            # 自然界的直接赐予，无需劳动
            return need_type in self.physical_props.get("satisfies", [])

        # For products and commodities, check functional tags
        if self.state in (MatterState.STATE_PRODUCT, MatterState.STATE_COMMODITY):
            for tag in self.physical_props.get("tags", []):
                if tag.value == need_type or tag.value == "edible":
                    return True
        return False

    def check_use_value_loss(self) -> bool:
        """
        使用价值丧失检查 - Check and apply use-value loss.

        Returns True if use-value was lost (state changed to USELESS).
        """
        if self.state == MatterState.STATE_USELESS:
            return False

        self.use_value_lifespan -= 1

        if self.use_value_lifespan <= 0:
            self._apply_use_value_loss()
            return True
        return False

    def _apply_use_value_loss(self):
        """
        应用使用价值丧失 - Apply use-value loss.
        Triggers unrealized_commodity_value_loss event if commodity was pending.
        """
        if self.state == MatterState.STATE_COMMODITY and self.exchange_status == "Pending":
            # Emit event for SNLT calculator to remove from pending pool
            # 幽灵比例被还原为虚无
            from src.utils.event_bus import EventBus
            EventBus.emit("unrealized_commodity_value_loss", self)

        self.state = MatterState.STATE_USELESS
        self.individual_labor_embodied = 0.0

    def to_product(self, labor_time: float):
        """将物品转变为我产品 - Transition to product state"""
        self.state = MatterState.STATE_PRODUCT
        self.individual_labor_embodied = labor_time

    def to_commodity(self):
        """将产品转变为商品 - Transition to commodity (for exchange)"""
        if self.state == MatterState.STATE_PRODUCT:
            self.state = MatterState.STATE_COMMODITY
            self.exchange_status = "Pending"

    @staticmethod
    def determine_sector(matter, context: str = None) -> str:
        """
        部类动态判定 - Determine sector dynamically.
        Returns: SECTOR_I (生产资料), SECTOR_II (消费资料),
                 SECTOR_TRANSPORT, or SECTOR_MONEY
        """
        if matter.state == MatterState.STATE_USELESS:
            return "SECTOR_II"  # Default

        tags = matter.physical_props.get("tags", [])

        if ItemTags.MONEY_COMMODITY.value in tags:
            return "SECTOR_MONEY"
        if ItemTags.LOCATION_CHANGE.value in tags:
            return "SECTOR_TRANSPORT"
        if ItemTags.TOOL.value in tags or ItemTags.RAW_MATERIAL.value in tags:
            return "SECTOR_I"
        return "SECTOR_II"


class EventBus:
    """
    事件总线 - Simple event bus for simulation events.
    Used to decouple components and trigger reactive behaviors.
    """
    _listeners: Dict[str, list] = {}

    @classmethod
    def emit(cls, event_type: str, data: any = None):
        """触发事件"""
        if event_type in cls._listeners:
            for callback in cls._listeners[event_type]:
                callback(data)

    @classmethod
    def on(cls, event_type: str, callback):
        """订阅事件"""
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        cls._listeners[event_type].append(callback)
