#!/usr/bin/env python3
"""
BATMAN Phase 2 — N=500 Monte Carlo Benchmark & Memory Profiler.

Measures:
  - Wall clock time for 500 runs (single COA)
  - Throughput (runs/s)
  - Peak RSS memory (via psutil)
  - Peak heap allocation (via tracemalloc)
  - CPU utilisation (process + system)

Outputs a JSON report to benchmark_results.json and prints a summary.
"""
from __future__ import annotations

import gc
import json
import os
import sys
import time
import tracemalloc

# Resolve paths relative to project root (parent of scripts/).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "services"))
sys.path.insert(0, os.path.join(_ROOT, "services/wargame-svc"))

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False
    print("[WARN] psutil not installed — skipping RSS and CPU metrics")

from shared.contracts import Mission, WorldState, COA
from simulation.engine import BATMANSimulation
from simulation.models import SimulationConfig
from monte_carlo.orchestrator import MonteCarloOrchestrator, _sample_uncertain_world


def _make_inputs() -> tuple[Mission, WorldState, COA]:
    mission = Mission(
        mission_id="BATMAN-BENCH-500",
        mission_type="COUNTER_INFILTRATION",
        objectives=("Secure_Alpha", "Establish_Cordon", "Extract_Hostage"),
        constraints={"max_friendly_casualties": 1, "roe": "RETURN_FIRE_ONLY"},
    )
    world = WorldState(
        terrain="MIXED",
        elevation_m=2800.0,
        slope_degrees=15.0,
        trafficability=0.72,
        vegetation_density=0.45,
        initial_weather="CLEAR",
        threat_probability=0.55,
        civilian_density=0.18,
        comms_baseline=0.88,
        fuel_available=0.92,
        ammunition_available=0.85,
    )
    coa = COA(
        coa_id="COA-BOLD",
        task_hierarchy={
            "name": "Root",
            "primitive": False,
            "children": [
                {"name": "Secure_Alpha",      "primitive": True, "duration_min": 75},
                {"name": "Establish_Cordon",  "primitive": True, "duration_min": 45},
                {"name": "Extract_Hostage",   "primitive": True, "duration_min": 60},
            ],
        },
        estimated_duration_min=180,
        required_resources={"fuel": 0.7, "ammo": 0.5},
    )
    return mission, world, coa


def banner(text: str) -> None:
    line = "═" * 70
    print(f"\n{line}\n  {text}\n{line}\n")


def run_benchmark(n: int = 500, workers: int = 16) -> dict:
    mission, world, coa = _make_inputs()
    config = SimulationConfig(
        tick_minutes=15,
        max_duration_minutes=300,
        friendly_count=3,
        threat_count=2,
        civilian_count=1,
    )

    factory = lambda m, ws, c, cfg: BATMANSimulation(m, ws, c, config=cfg).run()
    orchestrator = MonteCarloOrchestrator(simulation_factory=factory)

    # Force GC before measurement.
    gc.collect()

    # Start memory tracking.
    tracemalloc.start()
    if _PSUTIL:
        proc = psutil.Process(os.getpid())
        rss_before_mb = proc.memory_info().rss / 1024 / 1024
        cpu_before = proc.cpu_percent(interval=None)

    # ── THE BENCHMARK ────────────────────────────────────────────────────────
    t0 = time.perf_counter()
    results, stats, bench = orchestrator.run(
        coa, mission, world, runs=n, workers=workers, base_config=config
    )
    elapsed = time.perf_counter() - t0
    # ─────────────────────────────────────────────────────────────────────────

    # Capture memory.
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    report: dict = {
        "runs": n,
        "workers": workers,
        "wall_time_s": round(elapsed, 3),
        "throughput_runs_per_s": round(n / max(elapsed, 0.001), 2),
        "executor_type": bench.executor_type,
        "peak_heap_mb": round(peak_mem / 1024 / 1024, 2),
        "current_heap_mb": round(current_mem / 1024 / 1024, 2),
        "statistics": {
            "mission_success_rate": round(stats.mission_success_rate, 4),
            "objective_completion_rate": round(stats.objective_completion_rate, 4),
            "expected_casualties": round(stats.expected_friendly_casualties, 4),
            "casualty_stddev": round(stats.casualty_stddev, 4),
            "time_p50_min": round(stats.completion_time_quantiles.get("p50", 0), 1),
            "time_p95_min": round(stats.completion_time_quantiles.get("p95", 0), 1),
            "fuel_mean": round(stats.expected_fuel_usage, 4),
            "roe_violation_rate": round(stats.roe_violation_rate, 4),
            "constraint_violation_rate": round(stats.constraint_violation_rate, 4),
            "failure_modes": dict(list(stats.failure_mode_frequency.items())[:5]),
        },
    }

    if _PSUTIL:
        rss_after_mb = proc.memory_info().rss / 1024 / 1024
        cpu_after = proc.cpu_percent(interval=None)
        report["rss_before_mb"] = round(rss_before_mb, 1)
        report["rss_after_mb"] = round(rss_after_mb, 1)
        report["rss_delta_mb"] = round(rss_after_mb - rss_before_mb, 1)
        report["cpu_pct_after"] = round(cpu_after, 1)
        # System-wide cpu
        report["system_cpu_pct"] = round(psutil.cpu_percent(interval=0.1), 1)
        mem = psutil.virtual_memory()
        report["system_ram_available_mb"] = round(mem.available / 1024 / 1024, 0)
        report["system_ram_percent"] = round(mem.percent, 1)

    return report


def main() -> None:
    banner("BATMAN Phase 2 — N=500 Monte Carlo Benchmark")

    print("Running N=500 simulation benchmark (this will take ~30-90s)...")
    print("(Using injected factory — single-process to avoid REPL spawn issues)")
    print()

    report = run_benchmark(n=500, workers=16)

    # ── Print report ──────────────────────────────────────────────────────────
    print(f"{'─'*70}")
    print(f"  TIMING")
    print(f"{'─'*70}")
    print(f"  Runs              : {report['runs']}")
    print(f"  Wall time         : {report['wall_time_s']:.3f}s")
    print(f"  Throughput        : {report['throughput_runs_per_s']:.1f} runs/s")
    print(f"  Executor          : {report['executor_type']}")
    print()
    print(f"{'─'*70}")
    print(f"  MEMORY")
    print(f"{'─'*70}")
    print(f"  Peak heap (trace) : {report['peak_heap_mb']:.2f} MB")
    print(f"  Curr heap (trace) : {report['current_heap_mb']:.2f} MB")
    if "rss_before_mb" in report:
        print(f"  RSS before        : {report['rss_before_mb']:.1f} MB")
        print(f"  RSS after         : {report['rss_after_mb']:.1f} MB")
        print(f"  RSS delta         : {report['rss_delta_mb']:+.1f} MB")
        print(f"  CPU% (process)    : {report['cpu_pct_after']:.1f}%")
        print(f"  CPU% (system)     : {report['system_cpu_pct']:.1f}%")
        print(f"  RAM available     : {report['system_ram_available_mb']:.0f} MB")
        print(f"  RAM used%         : {report['system_ram_percent']:.1f}%")
    print()
    print(f"{'─'*70}")
    print(f"  OUTCOME STATISTICS (N=500)")
    print(f"{'─'*70}")
    s = report["statistics"]
    print(f"  Success rate         : {s['mission_success_rate']:.1%}")
    print(f"  Objective completion : {s['objective_completion_rate']:.1%}")
    print(f"  Casualties (mean±σ)  : {s['expected_casualties']:.2f} ± {s['casualty_stddev']:.2f}")
    print(f"  Time P50/P95 (min)   : {s['time_p50_min']:.0f} / {s['time_p95_min']:.0f}")
    print(f"  Fuel usage (mean)    : {s['fuel_mean']:.4f}")
    print(f"  ROE violation rate   : {s['roe_violation_rate']:.1%}")
    print(f"  Constraint viol.     : {s['constraint_violation_rate']:.1%}")
    if s["failure_modes"]:
        print(f"  Top failure modes    : {s['failure_modes']}")

    # Save JSON.
    out_path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report saved → {out_path}")

    # ── Pass/fail checks ──────────────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  ACCEPTANCE CRITERIA")
    print(f"{'─'*70}")
    checks = [
        ("Throughput ≥ 2 runs/s",            report["throughput_runs_per_s"] >= 2.0),
        ("Peak heap < 512 MB",               report["peak_heap_mb"] < 512.0),
        ("Success rate > 0% (non-trivial)",  s["mission_success_rate"] > 0.0),
        ("Success rate < 100% (stochastic)", s["mission_success_rate"] < 1.0),
        ("Time quantiles monotonic",         s["time_p50_min"] <= s["time_p95_min"]),
    ]
    if "rss_delta_mb" in report:
        checks.append(("RSS delta < 500 MB (no leak)", report["rss_delta_mb"] < 500.0))

    all_pass = True
    for label, passed in checks:
        symbol = "✅" if passed else "❌"
        print(f"  {symbol}  {label}")
        if not passed:
            all_pass = False

    print()
    if all_pass:
        print("  ✅ All acceptance criteria met — Phase 2 benchmark ACCEPTED")
    else:
        print("  ❌ Some acceptance criteria failed — review above")
        sys.exit(1)


if __name__ == "__main__":
    main()
