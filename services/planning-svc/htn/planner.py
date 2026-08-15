from __future__ import annotations

from .domain import Domain
from .models import Plan, Task, TaskHierarchy, WorldState


class PlanningError(ValueError):
    pass


class HTNPlanner:
    """Depth-first HTN planner with early doctrine/constraint pruning."""

    def __init__(self, domain: Domain, rule_engine=None, max_depth: int = 32):
        self.domain = domain
        self.rule_engine = rule_engine
        self.max_depth = max_depth

    def plan(self, mission_type: str, state: WorldState) -> Plan:
        root = Task(f"MISSION:{mission_type}")
        hierarchy, final_state = self._decompose(root, state, 0)
        firings = self.rule_engine.fired_rule_ids if self.rule_engine else []
        return Plan(hierarchy, final_state, firings)

    def _decompose(self, task: Task, state: WorldState, depth: int) -> tuple[TaskHierarchy, WorldState]:
        if depth > self.max_depth:
            raise PlanningError("HTN decomposition depth exceeded")
        if task.primitive:
            if self.rule_engine:
                self.rule_engine.validate_task(state, task)
            operator = self.domain.operators.get(task.name)
            if not operator or not operator.applicable(state, task):
                raise PlanningError(f"operator preconditions not met: {task.name}")
            return TaskHierarchy(task), state.updated(operator.effect(state, task))

        errors: list[str] = []
        for method in self.domain.methods_for(task):
            if not method.applicable(state, task):
                continue
            try:
                current = state
                children: list[TaskHierarchy] = []
                for child in method.decompose(current, task):
                    child_tree, current = self._decompose(child, current, depth + 1)
                    children.append(child_tree)
                return TaskHierarchy(task, children), current
            except PlanningError as error:
                errors.append(str(error))
        detail = "; ".join(errors) if errors else "no applicable method"
        raise PlanningError(f"cannot decompose {task.name}: {detail}")
