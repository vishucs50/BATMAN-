from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Task:
    """A typed HTN task. Primitive tasks are executable operators."""

    name: str
    primitive: bool = False
    parameters: dict[str, Any] = field(default_factory=dict)
    duration_min: int = 0
    required_resources: dict[str, float] = field(default_factory=dict)


@dataclass
class WorldState:
    """Small, serialisable projection of W = <E,R,T,L,C,H> used by Phase 1."""

    facts: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.facts.get(key, default)

    def updated(self, effects: dict[str, Any]) -> "WorldState":
        return WorldState({**self.facts, **effects})


@dataclass
class TaskHierarchy:
    task: Task
    children: list["TaskHierarchy"] = field(default_factory=list)

    def executable_tasks(self) -> list[Task]:
        if self.task.primitive:
            return [self.task]
        return [task for child in self.children for task in child.executable_tasks()]

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.task.name,
            "primitive": self.task.primitive,
            "parameters": self.task.parameters,
            "duration_min": self.task.duration_min,
            "required_resources": self.task.required_resources,
            "children": [child.as_dict() for child in self.children],
        }


@dataclass
class Plan:
    hierarchy: TaskHierarchy
    final_state: WorldState
    rule_firings: list[str] = field(default_factory=list)

    @property
    def executable_tasks(self) -> list[Task]:
        return self.hierarchy.executable_tasks()

    @property
    def estimated_duration_min(self) -> int:
        return sum(task.duration_min for task in self.executable_tasks)
