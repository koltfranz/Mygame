"""
Event Bus - 全局事件发布/订阅

Decouples simulation components through an event system.
Used for:
- Use-value loss events
- Means of production scrapping
- Revolution/crisis events
- Stage transitions
"""

from typing import Dict, List, Callable, Any


class EventBus:
    """
    事件总线 - Simple event bus for simulation events.

    Decouples components and triggers reactive behaviors.
    """

    _listeners: Dict[str, List[Callable]] = {}

    @classmethod
    def emit(cls, event_type: str, data: Any = None):
        """触发事件 - Emit an event"""
        if event_type in cls._listeners:
            for callback in cls._listeners[event_type]:
                callback(data)

    @classmethod
    def on(cls, event_type: str, callback: Callable):
        """订阅事件 - Subscribe to an event"""
        if event_type not in cls._listeners:
            cls._listeners[event_type] = []
        cls._listeners[event_type].append(callback)

    @classmethod
    def off(cls, event_type: str, callback: Callable = None):
        """取消订阅 - Unsubscribe from an event"""
        if callback is None:
            cls._listeners.pop(event_type, None)
        elif event_type in cls._listeners:
            cls._listeners[event_type] = [
                cb for cb in cls._listeners[event_type] if cb != callback
            ]

    @classmethod
    def clear(cls):
        """清除所有监听器 - Clear all listeners"""
        cls._listeners.clear()
