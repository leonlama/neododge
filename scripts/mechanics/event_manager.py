"""
Event system for decoupled communication between game components.
"""
from typing import Callable, Dict, List, Any

class EventManager:
    """
    Manages game-wide events using a publisher-subscriber pattern.
    Allows components to communicate without direct dependencies.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
            cls._instance._subscribers = {}
        return cls._instance

    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to an event type

        Args:
            event_type: String identifier for the event
            callback: Function to call when event is published
        """
        if event_type not in self._subscribers:
            self._subscribers = {}
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        """
        Unsubscribe from an event type

        Args:
            event_type: String identifier for the event
            callback: Function to remove from subscribers
        """
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)

    def publish(self, event_type: str, data: Any = None):
        """
        Publish an event to all subscribers

        Args:
            event_type: String identifier for the event
            data: Optional data to pass to subscribers
        """
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(data)

# Create singleton instance
event_manager = EventManager()