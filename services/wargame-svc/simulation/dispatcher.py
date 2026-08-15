"""
EventDispatcher — routes immutable SimulationEvents to registered domain handlers.

The dispatcher owns no domain logic. It:
  1. Receives an event from the SimPy process.
  2. Appends it to the immutable EventLog.
  3. Looks up the handler registered for that event type.
  4. Calls the handler (which mutates WorldState and may return cascading events).
  5. Returns the list of cascading events to the caller for scheduling.

All state mutation lives in dedicated handler functions, not here.
"""
from __future__ import annotations

from typing import Any, Callable, Protocol

from .events import SimulationEvent, SimulationEventType


# ── Handler protocol ──────────────────────────────────────────────────────────
class EventHandlerProtocol(Protocol):
    """
    Type contract for a domain handler function.

    Signature:  handler(event, world_state) -> list[SimulationEvent]

    The handler may mutate world_state and MUST return a (possibly empty) list
    of cascading events that the dispatcher will schedule next.
    """

    def __call__(
        self,
        event: SimulationEvent,
        world_state: Any,
    ) -> list[SimulationEvent]: ...


# ── Dispatcher ────────────────────────────────────────────────────────────────
class EventDispatcher:
    """
    Central event router.

    Maintains a dispatch table (event_type → handler) and the immutable
    append-only EventLog. The dispatcher never performs physics or domain
    calculations — those are the sole responsibility of the handlers.
    """

    def __init__(self) -> None:
        self._handlers: dict[SimulationEventType, EventHandlerProtocol] = {}
        self._log: list[dict[str, Any]] = []

    # ── Registration ──────────────────────────────────────────────────────────
    def register(
        self,
        event_type: SimulationEventType,
        handler: EventHandlerProtocol,
    ) -> None:
        """
        Register a domain handler for an event type.

        One handler per event type is enforced; later calls overwrite earlier
        ones so that tests can substitute stubs cleanly.
        """
        self._handlers[event_type] = handler

    # ── Dispatch ─────────────────────────────────────────────────────────────
    def dispatch(
        self,
        event: SimulationEvent,
        world_state: Any,
    ) -> list[SimulationEvent]:
        """
        Route *event* to its handler, log it, and return any cascading events.

        If no handler is registered the event is still logged (for audit
        completeness) and an empty list is returned.
        """
        self._log.append(event.to_log_dict())
        handler = self._handlers.get(event.event_type)
        if handler is None:
            return []
        return handler(event, world_state)

    def dispatch_all(
        self,
        events: list[SimulationEvent],
        world_state: Any,
    ) -> list[SimulationEvent]:
        """Dispatch a batch of events and collect all cascading events."""
        cascading: list[SimulationEvent] = []
        for event in events:
            cascading.extend(self.dispatch(event, world_state))
        return cascading

    # ── Log access ────────────────────────────────────────────────────────────
    @property
    def event_log(self) -> list[dict[str, Any]]:
        """Return a shallow copy of the immutable event log."""
        return list(self._log)

    @property
    def log_size(self) -> int:
        """Total events recorded this simulation run."""
        return len(self._log)


# ── Default no-op handler ─────────────────────────────────────────────────────
def noop_handler(
    event: SimulationEvent,
    world_state: Any,   # noqa: ARG001
) -> list[SimulationEvent]:
    """A no-op handler for event types that carry no domain consequence."""
    return []
