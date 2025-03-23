from typing import Any, Callable, Dict, List, Optional

from lilya.compat import is_async_callable


class EventDispatcher:
    """Centralized event dispatcher to handle auto-triggering of event listeners."""

    _listeners: Dict[str, List[Callable]] = {}

    @classmethod
    def register(cls, func: Callable, listen: Optional[List[str]] = None) -> None:
        """Registers a function as a listener for given events."""
        if listen:
            for event in listen:
                if event not in cls._listeners:
                    cls._listeners[event] = []
                cls._listeners[event].append(func)

    @classmethod
    async def emit(cls, event: str, *args: Any, **kwargs: Any) -> None:
        """Triggers all listeners for a given event."""
        if event in cls._listeners:
            for listener in cls._listeners[event]:
                if is_async_callable(listener):
                    await listener(*args, **kwargs)
                else:
                    listener(*args, **kwargs)
