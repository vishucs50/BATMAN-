from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .models import Task, WorldState

Predicate = Callable[[WorldState, Task], bool]
Effect = Callable[[WorldState, Task], dict]
Decomposer = Callable[[WorldState, Task], list[Task]]


@dataclass(frozen=True)
class Operator:
    task_name: str
    preconditions: tuple[Predicate, ...] = ()
    effect: Effect = lambda _state, _task: {}

    def applicable(self, state: WorldState, task: Task) -> bool:
        return all(predicate(state, task) for predicate in self.preconditions)


@dataclass(frozen=True)
class Method:
    task_name: str
    name: str
    decompose: Decomposer
    preconditions: tuple[Predicate, ...] = ()
    priority: int = 100

    def applicable(self, state: WorldState, task: Task) -> bool:
        return all(predicate(state, task) for predicate in self.preconditions)


@dataclass
class Domain:
    operators: dict[str, Operator] = field(default_factory=dict)
    methods: dict[str, list[Method]] = field(default_factory=dict)

    def add_operator(self, operator: Operator) -> None:
        self.operators[operator.task_name] = operator

    def add_method(self, method: Method) -> None:
        self.methods.setdefault(method.task_name, []).append(method)
        self.methods[method.task_name].sort(key=lambda item: item.priority)

    def methods_for(self, task: Task) -> list[Method]:
        return self.methods.get(task.name, [])
