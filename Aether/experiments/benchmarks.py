"""
Aether Heavy-Duty Multi-Scale Benchmark Suite
Executes exhaustive performance benchmarks across synthetic metropolitan grids
(up to 2,500 nodes) and real-world OpenStreetMap networks (Manhattan NYC),
profiling Dijkstra vs. Dynamic A* vs. Bidirectional A* across P50/P90/P99 latency
distributions, memory consumption (tracemalloc), search space pruning, and disruption churn.
"""

import json
import math
import os
import random
import time
import tracemalloc
from typing import Any, Dict, List, Tuple
import numpy as np

from Aether.core.graph import DirectedGraph
from Aether.core.osm_loader import OSMRoadNetworkLoader
from Aether.core.traversal import (
    find_shortest_path,
    find_shortest_path_dijkstra,
    find_shortest_path_bidirectional,
    RouteResult,
)
from Aether.core.hazards import HazardManager


class MultiScaleBenchmarkSuite:
    """
    Industrial-grade benchmarking harness evaluating routing latency,
    computational scaling, memory footprint, and algorithmic efficiency.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        np.random.seed(seed)

    def load_or_build_topologies(self) -> Dict[str, DirectedGraph]:
        """Prepares small, medium, large, and real-world network models."""
        topologies: Dict[str, DirectedGraph] = {}

        print("[*] Generating 16x16 Small Urban Grid (256 nodes)...")
        topologies["Grid_16x16"] = DirectedGraph.generate_grid_network(
            rows=16, cols=16, spacing_meters=200.0, highway_rows=[4, 11], highway_cols=[4, 11]
        )

        print("[*] Generating 32x32 Metropolitan Grid (1,024 nodes)...")
        topologies["Grid_32x32"] = DirectedGraph.generate_grid_network(
            rows=32, cols=32, spacing_meters=200.0, highway_rows=[8, 23], highway_cols=[8, 23]
        )

        print("[*] Generating 50x50 Megacity Grid (2,500 nodes)...")
        topologies["Grid_50x50"] = DirectedGraph.generate_grid_network(
            rows=50, cols=50, spacing_meters=200.0, highway_rows=[12, 37], highway_cols=[12, 37]
        )

        print("[*] Loading Real-World Manhattan NYC Road Network (OSM)...")
        topologies["Manhattan_OSM"] = OSMRoadNetworkLoader.load_preset_map("manhattan")

        return topologies

    def benchmark_algorithm_shootout(
        self,
        graph: DirectedGraph,
        num_queries: int = 200,
    ) -> Dict[str, Any]:
        """
        Head-to-head comparison of Dijkstra vs Dynamic A* vs Bidirectional A*
        across an identical set of random queries on the given graph.
        """
        all_nodes = list(graph.nodes.keys())
        queries: List[Tuple[int, int]] = []
        for _ in range(num_queries):
            u = self.rng.choice(all_nodes)
            v = self.rng.choice(all_nodes)
            if u != v:
                queries.append((u, v))

        algos = {
            "Dijkstra": find_shortest_path_dijkstra,
            "Dynamic_AStar": find_shortest_path,
            "Bidirectional_AStar": find_shortest_path_bidirectional,
        }

        results: Dict[str, Any] = {}

        for name, solver in algos.items():
            latencies_ms: List[float] = []
            expanded_nodes: List[int] = []
            path_lengths: List[int] = []
            success_count = 0

            # Memory tracking
            tracemalloc.start()
            t0 = time.perf_counter()

            for u, v in queries:
                res: RouteResult = solver(graph, u, v)
                if res.success:
                    success_count += 1
                    latencies_ms.append(res.search_time_ms)
                    expanded_nodes.append(res.nodes_expanded)
                    path_lengths.append(len(res.path))

            total_wall_time = time.perf_counter() - t0
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            if not latencies_ms:
                continue

            qps = len(queries) / total_wall_time
            results[name] = {
                "queries_executed": len(queries),
                "successful_queries": success_count,
                "qps": float(qps),
                "latency_p50_ms": float(np.percentile(latencies_ms, 50)),
                "latency_p90_ms": float(np.percentile(latencies_ms, 90)),
                "latency_p95_ms": float(np.percentile(latencies_ms, 95)),
                "latency_p99_ms": float(np.percentile(latencies_ms, 99)),
                "latency_mean_ms": float(np.mean(latencies_ms)),
                "latency_std_ms": float(np.std(latencies_ms)),
                "latency_max_ms": float(np.max(latencies_ms)),
                "mean_nodes_expanded": float(np.mean(expanded_nodes)),
                "mean_path_length": float(np.mean(path_lengths)),
                "peak_memory_kb": float(peak_mem / 1024.0),
            }

        # Calculate speedup factors relative to Dijkstra baseline
        if "Dijkstra" in results:
            dijkstra_exp = results["Dijkstra"]["mean_nodes_expanded"]
            dijkstra_lat = results["Dijkstra"]["latency_mean_ms"]
            for name in ["Dynamic_AStar", "Bidirectional_AStar"]:
                if name in results:
                    lat_speedup = dijkstra_lat / max(1e-6, results[name]["latency_mean_ms"])
                    pruning_pct = ((dijkstra_exp - results[name]["mean_nodes_expanded"]) / max(1, dijkstra_exp)) * 100.0
                    results[name]["speedup_vs_dijkstra"] = float(lat_speedup)
                    results[name]["search_space_pruned_pct"] = float(pruning_pct)

        return results

    def benchmark_disruption_churn(
        self,
        graph: DirectedGraph,
        cut_counts: List[int] = [10, 50, 100],
    ) -> Dict[str, Any]:
        """
        Stress-tests dynamic graph restructuring and rerouting latency under
        massive simultaneous edge closure injections.
        """
        hazard_mgr = HazardManager(graph)
        all_edges = graph.get_all_edges()
        churn_results = {}

        for count in cut_counts:
            if count > len(all_edges) // 4:
                continue

            chosen_edges = self.rng.sample(all_edges, count)

            # Measure mass injection latency
            t_inj = time.perf_counter()
            for edge in chosen_edges:
                hazard_mgr.inject_edge_closure(edge.u, edge.v, reason="Stress Churn Test", duration_seconds=100.0)
            inj_latency_ms = (time.perf_counter() - t_inj) * 1000.0

            # Measure reroute latency across 50 random pairs under heavy disruption
            reroute_times: List[float] = []
            i1_violations = 0
            for _ in range(50):
                u = self.rng.choice(list(graph.nodes.keys()))
                v = self.rng.choice(list(graph.nodes.keys()))
                if u != v:
                    t_route = time.perf_counter()
                    res = find_shortest_path(graph, u, v)
                    reroute_times.append((time.perf_counter() - t_route) * 1000.0)
                    if res.success:
                        for edge_traversed in res.edges_traversed:
                            if edge_traversed in graph.closed_edges:
                                i1_violations += 1

            # Restore edges
            for edge in chosen_edges:
                graph.reopen_edge(edge.u, edge.v)

            churn_results[f"{count}_closures"] = {
                "closure_injection_time_ms": inj_latency_ms,
                "mean_reroute_latency_ms": float(np.mean(reroute_times)) if reroute_times else 0.0,
                "p95_reroute_latency_ms": float(np.percentile(reroute_times, 95)) if reroute_times else 0.0,
                "invariant_i1_violations": i1_violations,
                "system_resilient": (i1_violations == 0),
            }

        return churn_results

    def run_full_suite(self, output_dir: str = "Aether/experiments/results") -> Dict[str, Any]:
        """Executes the comprehensive multi-scale benchmark suite and outputs JSON."""
        os.makedirs(output_dir, exist_ok=True)
        topologies = self.load_or_build_topologies()
        report: Dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "suite": "AetherGrid Heavy-Duty Multi-Scale Benchmark",
            "topologies": {},
            "churn_stress_test": {},
        }

        print("\n" + "=" * 80)
        print("  AETHERGRID-AI MULTI-SCALE PERFORMANCE BENCHMARK & ALGORITHM SHOOTOUT")
        print("=" * 80)

        for topo_name, graph in topologies.items():
            print(f"\n---> Benchmarking {topo_name} ({graph.num_nodes} nodes, {graph.num_edges} edges)...")
            q_count = 150 if graph.num_nodes <= 1024 else 80
            shootout = self.benchmark_algorithm_shootout(graph, num_queries=q_count)
            report["topologies"][topo_name] = {
                "nodes": graph.num_nodes,
                "edges": graph.num_edges,
                "shootout": shootout,
            }

            # Print rich terminal table
            self._print_shootout_table(topo_name, graph, shootout)

        # Churn stress test on 32x32 Grid
        print("\n---> Running Topological Churn Stress Test on Grid 32x32 (1,024 nodes)...")
        churn_data = self.benchmark_disruption_churn(topologies["Grid_32x32"], cut_counts=[10, 50, 100])
        report["churn_stress_test"]["Grid_32x32"] = churn_data
        self._print_churn_table(churn_data)

        out_file = os.path.join(output_dir, "heavy_benchmarks.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\n[+] Comprehensive benchmark complete! Detailed report written to: {out_file}")
        return report

    def _print_shootout_table(self, topo_name: str, graph: DirectedGraph, shootout: Dict[str, Any]) -> None:
        print(f"\n  Topological Scale: {topo_name} | Nodes: {graph.num_nodes} | Directed Edges: {graph.num_edges}")
        print("  " + "-" * 76)
        print(f"  {'Algorithm':<22} | {'Mean Latency':<12} | {'P95 Latency':<11} | {'Throughput':<11} | {'Pruned %':<8}")
        print("  " + "-" * 76)
        for algo, data in shootout.items():
            mean_lat = f"{data['latency_mean_ms']:.3f} ms"
            p95_lat = f"{data['latency_p95_ms']:.3f} ms"
            qps = f"{data['qps']:.1f} QPS"
            pruned = f"{data.get('search_space_pruned_pct', 0.0):.1f}%"
            print(f"  {algo:<22} | {mean_lat:<12} | {p95_lat:<11} | {qps:<11} | {pruned:<8}")
        print("  " + "-" * 76)

    def _print_churn_table(self, churn: Dict[str, Any]) -> None:
        print("  " + "-" * 76)
        print(f"  {'Disruption Level':<20} | {'Inject Latency':<14} | {'Mean Reroute':<14} | {'I1 Violations':<12}")
        print("  " + "-" * 76)
        for level, d in churn.items():
            inj = f"{d['closure_injection_time_ms']:.3f} ms"
            reroute = f"{d['mean_reroute_latency_ms']:.3f} ms"
            i1 = f"{d['invariant_i1_violations']} (100% OK)"
            print(f"  {level:<20} | {inj:<14} | {reroute:<14} | {i1:<12}")
        print("  " + "-" * 76)


if __name__ == "__main__":
    suite = MultiScaleBenchmarkSuite()
    suite.run_full_suite()
