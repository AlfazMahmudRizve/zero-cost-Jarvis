"""
Async Utility Functions
Helpers for managing async operations in JARVIS.
"""

import asyncio
from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar
from contextlib import asynccontextmanager

T = TypeVar("T")


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run an async function from synchronous code.
    Handles event loop detection gracefully.
    
    Args:
        coro: Coroutine to execute
        
    Returns:
        Result of the coroutine
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    if loop and loop.is_running():
        # We're inside an async context, create a task
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        # No event loop running, safe to use asyncio.run
        return asyncio.run(coro)


@asynccontextmanager
async def timeout_handler(seconds: float, operation_name: str = "Operation"):
    """
    Async context manager for operation timeouts.
    
    Args:
        seconds: Timeout duration in seconds
        operation_name: Name of operation for error messages
        
    Yields:
        None
        
    Raises:
        asyncio.TimeoutError: If operation exceeds timeout
    """
    try:
        async with asyncio.timeout(seconds):
            yield
    except asyncio.TimeoutError:
        raise asyncio.TimeoutError(f"{operation_name} timed out after {seconds}s")


def async_retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator for retrying async functions with exponential backoff.
    
    Args:
        max_retries: Maximum retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., Coroutine]) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
            
            raise last_exception  # type: ignore
        
        return wrapper
    return decorator


class AsyncEventBus:
    """
    Simple async event bus for decoupled component communication.
    Used for JARVIS subsystem coordination.
    """
    
    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable]] = {}
    
    def subscribe(self, event: str, callback: Callable) -> None:
        """Subscribe to an event."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)
    
    def unsubscribe(self, event: str, callback: Callable) -> None:
        """Unsubscribe from an event."""
        if event in self._listeners:
            self._listeners[event].remove(callback)
    
    async def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Emit an event to all subscribers."""
        if event in self._listeners:
            for callback in self._listeners[event]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)


# Global event bus instance
event_bus = AsyncEventBus()
