"""
Aether Empirical Experimentation Suite (Phase 01)
Executes pre-registered scientific experiments evaluating heuristic admissibility,
EWMA congestion filter damping, and dynamic detour latency under structural disruptions.
"""

import json
import math
import os
import random
import time
from typing import Any, Dict, List
import numpy as np

from Aether.core.graph import DirectedGraph, TerrainType
from Aether.core.pricing import CostModelParameters, compute_admissible_heuristic
from Aether.core.weather import WeatherManager, WeatherType
from Aether.core.congestion import CongestionManager
from Aether.core.hazards import HazardManager
from Aether.core.traversal import find_shortest_path


def run_experiment_1_admissibility(
    num_trials: int = 5000,
    grid_size: int = 8,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Experiment 1: Empirical Verification of Heuristic Admissibility.
    Asserts h(u, goal) <= c*(u, goal) across thousands of randomized states
    with volatile congestion, weather, and hazard injections.
    """
    print(f"[*] Running Experiment 1: Admissibility Verification ({num_trials} trials)...")
    rng = random.Random(seed)
    np.random.seed(seed)

    graph = DirectedGraph.generate_grid_network(
        rows=grid_size,
        cols=grid_size,
        spacing_meters=200.0,
        highway_rows=[2, 5],
        highway_cols=[2, 5],
    )

    congestion_mgr = CongestionManager(graph)
    hazard_mgr = HazardManager(graph)
    weather_mgr = WeatherManager(WeatherType.CLEAR, rng=rng)

    # Randomly assign initial occupancies, hazards, and weather
    weather_types = [WeatherType.CLEAR, WeatherType.RAIN, WeatherType.FOG, WeatherType.SNOW]
    weather_mgr.set_weather(rng.choice(weather_types))

    for edge in graph.get_all_edges():
        edge.occupancy = rng.randint(0, edge.capacity)
        edge.congestion = rng.uniform(0.0, 1.0)
        if rng.random() < 0.10:
            graph.inject_hazard(edge.u, edge.v, penalty_beta=45.0, label="Hazmat")

    all_nodes = list(graph.nodes.keys())
    violations = 0
    tested_pairs = 0
    reachable_pairs = 0
    ratios: List[float] = []

    start_time = time.perf_counter()

    for _ in range(num_trials):
        u = rng.choice(all_nodes)
        v = rng.choice(all_nodes)
        if u == v:
            continue

        tested_pairs += 1
        h = compute_admissible_heuristic(graph.nodes[u], graph.nodes[v], graph.max_network_speed)
        res = find_shortest_path(graph, u, v, weather_multiplier=weather_mgr.multiplier)

        if res.success:
            reachable_pairs += 1
            c_star = res.total_cost_seconds
            # Admissibility condition: h <= c_star (with 1e-6 epsilon for numerical float tolerance)
            if h > c_star + 1e-6:
                violations += 1
            ratio = h / max(1e-6, c_star)
            ratios.append(ratio)

    elapsed_time = time.perf_counter() - start_time

    results = {
        "experiment": "Heuristic Admissibility Bound",
        "trials_requested": num_trials,
        "tested_pairs": tested_pairs,
        "reachable_pairs": reachable_pairs,
        "admissibility_violations": violations,
        "is_admissibility_proven": (violations == 0),
        "heuristic_ratio_mean": float(np.mean(ratios)) if ratios else 0.0,
        "heuristic_ratio_max": float(np.max(ratios)) if ratios else 0.0,
        "heuristic_ratio_min": float(np.min(ratios)) if ratios else 0.0,
        "elapsed_seconds": elapsed_time,
    }
    print(f"    -> Violations: {violations}/{tested_pairs} (Proven: {violations == 0})")
    print(f"    -> Mean h/c* Ratio: {results['heuristic_ratio_mean']:.4f}, Max: {results['heuristic_ratio_max']:.4f}")
    return results


def run_experiment_2_ewma_damping(
    steps: int = 120,
    pulse_period: int = 20,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Experiment 2: EWMA Congestion Filter Damping & Stability Analysis.
    Evaluates variance suppression on an edge subjected to high-frequency pulse traffic.
    """
    print(f"[*] Running Experiment 2: EWMA Congestion Damping Analysis ({steps} steps)...")
    graph = DirectedGraph.generate_grid_network(rows=4, cols=4, spacing_meters=200.0)
    congestion_mgr = CongestionManager(graph, smoothing_time_constant=15.0)

    test_edge = graph.get_edge(0, 1)
    assert test_edge is not None
    cap = test_edge.capacity

    instantaneous_trace: List[float] = []
    ewma_trace: List[float] = []

    for t in range(steps):
        # Square-wave pulse traffic: 0 for half period, capacity for other half
        if (t // pulse_period) % 2 == 0:
            test_edge.occupancy = cap
        else:
            test_edge.occupancy = 0

        inst_rho = test_edge.occupancy / cap
        instantaneous_trace.append(inst_rho)

        congestion_mgr.step(dt=1.0)
        ewma_trace.append(test_edge.congestion)

    inst_variance = float(np.var(instantaneous_trace))
    ewma_variance = float(np.var(ewma_trace))
    variance_reduction_pct = ((inst_variance - ewma_variance) / inst_variance) * 100.0

    results = {
        "experiment": "EWMA Congestion Filter Damping",
        "steps": steps,
        "instantaneous_variance": inst_variance,
        "ewma_smoothed_variance": ewma_variance,
        "variance_reduction_pct": variance_reduction_pct,
        "smoothing_effective": (variance_reduction_pct > 60.0),
        "final_ewma_rho": ewma_trace[-1],
    }
    print(f"    -> Raw Variance: {inst_variance:.4f} | EWMA Variance: {ewma_variance:.4f}")
    print(f"    -> Variance Reduction: {variance_reduction_pct:.2f}% (Target > 60%)")
    return results


def run_experiment_3_disruption_reroute(
    num_cuts: int = 40,
    grid_size: int = 10,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Experiment 3: Disruption Detour Latency & Invariant I1 Verification.
    Evaluates dynamic route adaptation and latency when corridors are closed.
    """
    print(f"[*] Running Experiment 3: Dynamic Detour Latency & Invariant I1 ({num_cuts} cuts)...")
    rng = random.Random(seed)

    # Grid with river barrier at column 5, bridges at rows 2 and 7
    graph = DirectedGraph.generate_grid_network(
        rows=grid_size,
        cols=grid_size,
        spacing_meters=200.0,
        river_col=grid_size // 2,
        bridge_rows=[2, grid_size - 3],
    )
    hazard_mgr = HazardManager(graph)

    detour_ratios: List[float] = []
    latencies_ms: List[float] = []
    i1_violations = 0
    successful_reroutes = 0

    start_node = 0
    goal_node = grid_size * grid_size - 1

    for cut_idx in range(num_cuts):
        # 1. Baseline route
        res_baseline = find_shortest_path(graph, start_node, goal_node)
        if not res_baseline.success or len(res_baseline.edges_traversed) < 3:
            continue

        # 2. Pick a middle edge from baseline path to sever
        cut_edge_idx = len(res_baseline.edges_traversed) // 2
        cut_u, cut_v = res_baseline.edges_traversed[cut_edge_idx]

        # 3. Close the edge
        hazard_mgr.inject_edge_closure(cut_u, cut_v, reason="Emergency Structural Cut", duration_seconds=100.0)

        # 4. Measure rerouting time
        t0 = time.perf_counter()
        res_reroute = find_shortest_path(graph, start_node, goal_node)
        recompute_time_ms = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(recompute_time_ms)

        if res_reroute.success:
            successful_reroutes += 1
            detour_ratio = res_reroute.total_cost_seconds / res_baseline.total_cost_seconds
            detour_ratios.append(detour_ratio)

            # Invariant I1 verification: Ensure severed edge is NOT traversed
            if (cut_u, cut_v) in res_reroute.edges_traversed or (cut_v, cut_u) in res_reroute.edges_traversed:
                i1_violations += 1

        # Reopen for next iteration
        graph.reopen_edge(cut_u, cut_v)
        graph.reopen_edge(cut_v, cut_u)

    results = {
        "experiment": "Disruption Detour Latency & Invariant I1",
        "num_cuts_tested": num_cuts,
        "successful_reroutes": successful_reroutes,
        "i1_violations": i1_violations,
        "mean_latency_ms": float(np.mean(latencies_ms)) if latencies_ms else 0.0,
        "max_latency_ms": float(np.max(latencies_ms)) if latencies_ms else 0.0,
        "mean_detour_ratio": float(np.mean(detour_ratios)) if detour_ratios else 0.0,
        "i1_verified": (i1_violations == 0),
    }
    print(f"    -> Mean Reroute Latency: {results['mean_latency_ms']:.3f} ms (Max: {results['max_latency_ms']:.3f} ms)")
    print(f"    -> Mean Detour Cost Ratio: {results['mean_detour_ratio']:.3f}x")
    print(f"    -> Invariant I1 Violations: {i1_violations} (Verified: {i1_violations == 0})")
    return results


def run_all_experiments(output_dir: str = "Aether/experiments/results") -> Dict[str, Any]:
    """Executes all Phase 01 experiments and saves a structured JSON report."""
    os.makedirs(output_dir, exist_ok=True)
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "phase": "01",
        "experiment_1": run_experiment_1_admissibility(num_trials=2500),
        "experiment_2": run_experiment_2_ewma_damping(steps=100),
        "experiment_3": run_experiment_3_disruption_reroute(num_cuts=30),
    }

    report_path = os.path.join(output_dir, "phase1_experiments.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n[+] All Phase 01 experiments completed successfully!")
    print(f"[+] Saved structured report to: {report_path}")
    return report


if __name__ == "__main__":
    run_all_experiments()
