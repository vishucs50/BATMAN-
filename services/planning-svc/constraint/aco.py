from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Assignment:
    unit_id: str
    task_id: str
    fuel_cost: float
    resource_cost: float
    suitability: float
    hard_eligible: bool = True


@dataclass
class OptimizationResult:
    assignments: list[Assignment]
    score: float
    fuel_used: float
    resource_used: float
    iterations: int


class ConstraintOptimizer:
    """Small deterministic Ant Colony Optimisation solver for assignments."""

    def __init__(self, ants: int = 24, iterations: int = 40, evaporation: float = .2, seed: int = 7):
        self.ants, self.iterations, self.evaporation = ants, iterations, evaporation
        self.random = random.Random(seed)

    def optimize(self, assignments: list[Assignment], fuel_budget: float, resource_budget: float, soft_weight: float = 1.0) -> OptimizationResult:
        feasible = [item for item in assignments if item.hard_eligible]
        tasks = sorted({item.task_id for item in feasible})
        if not tasks:
            return OptimizationResult([], 0.0, 0.0, 0.0, self.iterations)
        pheromone = {(item.unit_id, item.task_id): 1.0 for item in feasible}
        best: list[Assignment] = []
        best_score = float("-inf")
        for _ in range(self.iterations):
            candidates: list[tuple[list[Assignment], float]] = []
            for _ant in range(self.ants):
                selected, units = [], set()
                fuel, resources = 0.0, 0.0
                for task in tasks:
                    options = [item for item in feasible if item.task_id == task and item.unit_id not in units and fuel + item.fuel_cost <= fuel_budget and resources + item.resource_cost <= resource_budget]
                    if not options:
                        continue
                    weights = [pheromone[(item.unit_id, item.task_id)] * max(item.suitability, .01) for item in options]
                    choice = self.random.choices(options, weights=weights, k=1)[0]
                    selected.append(choice); units.add(choice.unit_id)
                    fuel += choice.fuel_cost; resources += choice.resource_cost
                score = sum(item.suitability for item in selected) - soft_weight * (fuel / max(fuel_budget, 1) + resources / max(resource_budget, 1))
                candidates.append((selected, score))
                if len(selected) == len(tasks) and score > best_score:
                    best, best_score = selected, score
            for key in pheromone:
                pheromone[key] *= 1 - self.evaporation
            for selected, score in candidates:
                if score > 0:
                    for item in selected:
                        pheromone[(item.unit_id, item.task_id)] += score / max(len(selected), 1)
        return OptimizationResult(best, max(best_score, 0.0), sum(item.fuel_cost for item in best), sum(item.resource_cost for item in best), self.iterations)
