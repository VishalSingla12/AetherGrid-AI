"""
Aether Unit & Property Test Suite (Phase 01)
Formal verification of Graph, Pricing, Weather, Congestion, and Pathfinding Invariants.
"""

import math
import unittest
from Aether.core.graph import DirectedGraph, NodeData, TerrainType
from Aether.core.pricing import (
    CostModelParameters,
    calculate_edge_cost,
    compute_admissible_heuristic,
)
from Aether.core.weather import WeatherManager, WeatherType
from Aether.core.congestion import CongestionManager
from Aether.core.hazards import HazardManager
from Aether.core.traversal import find_shortest_path
from Aether.simulation.demo_sim import DemoSimulation


class TestPhase01Core(unittest.TestCase):
    """Unit and property test suite for Phase 01 components."""

    def setUp(self):
        self.graph = DirectedGraph("TestCity")
        # Build a small 3x3 grid
        for r in range(3):
            for c in range(3):
                node_id = r * 3 + c
                self.graph.add_node(node_id, float(c * 100), float(r * 100))

        # Add horizontal and vertical edges
        for r in range(3):
            for c in range(3):
                u = r * 3 + c
                if c + 1 < 3:
                    self.graph.add_edge(u, r * 3 + c + 1, length_meters=100.0, free_flow_speed_mps=20.0, bidirectional=True)
                if r + 1 < 3:
                    self.graph.add_edge(u, (r + 1) * 3 + c, length_meters=100.0, free_flow_speed_mps=20.0, bidirectional=True)

    def test_graph_properties(self):
        """Verify node count, edge count, and basic topological access."""
        self.assertEqual(self.graph.num_nodes, 9)
        self.assertEqual(self.graph.num_edges, 24)  # 12 undirected segments = 24 directed edges
        self.assertEqual(self.graph.num_open_edges, 24)

    def test_cost_pricing_exact_formula(self):
        """
        Verify master cost formula against exact hand calculation:
        c(e, t) = ell_e * tau_e * (1 + alpha * rho_e) * omega + beta
        """
        edge = self.graph.get_edge(0, 1)
        self.assertIsNotNone(edge)
        edge.free_flow_time_seconds = 10.0  # ell_e = 10s
        edge.terrain = TerrainType.URBAN     # tau_e = 1.45
        edge.congestion = 0.50               # rho_e = 0.50
        edge.is_hazard = True
        edge.hazard_penalty_seconds = 45.0   # beta = 45s

        params = CostModelParameters(alpha=0.85)
        weather_multiplier = 1.22  # RAIN

        # Hand calculation:
        # dynamic_time = 10.0 * 1.45 * (1.0 + 0.85 * 0.50) * 1.22
        # = 14.5 * 1.425 * 1.22 = 25.1956
        # total_cost = 25.1956 + 45.0 = 70.1956
        expected_cost = 10.0 * 1.45 * (1.0 + 0.85 * 0.50) * 1.22 + 45.0
        calculated_cost = calculate_edge_cost(edge, weather_multiplier=weather_multiplier, params=params)

        self.assertAlmostEqual(calculated_cost, expected_cost, places=4)

    def test_closed_edge_returns_infinite_cost_and_excluded_from_open_edges(self):
        """Invariant I1 verification at graph & pricing boundary."""
        edge = self.graph.get_edge(0, 1)
        self.assertIsNotNone(edge)

        # Initially open
        self.assertFalse(math.isinf(calculate_edge_cost(edge)))
        open_outs_before = [v for v, e in self.graph.get_open_out_edges(0)]
        self.assertIn(1, open_outs_before)

        # Close the edge
        self.graph.close_edge(0, 1, reason="Sinkhole")
        self.assertTrue(math.isinf(calculate_edge_cost(edge)))

        # Assert excluded from open outgoing edges
        open_outs_after = [v for v, e in self.graph.get_open_out_edges(0)]
        self.assertNotIn(1, open_outs_after)
        self.assertIn((0, 1), self.graph.closed_edges)

    def test_heuristic_admissibility(self):
        """Assert h(u, goal) <= c*(u, goal) on grid."""
        max_speed = self.graph.max_network_speed
        for u in self.graph.nodes:
            for v in self.graph.nodes:
                h = compute_admissible_heuristic(self.graph.nodes[u], self.graph.nodes[v], max_speed)
                res = find_shortest_path(self.graph, u, v)
                if res.success:
                    self.assertLessEqual(h, res.total_cost_seconds + 1e-6)

    def test_ewma_congestion_convergence(self):
        """Assert EWMA filter smoothly converges to steady-state density."""
        congestion_mgr = CongestionManager(self.graph, smoothing_time_constant=10.0)
        edge = self.graph.get_edge(0, 1)
        self.assertIsNotNone(edge)
        edge.capacity = 100
        edge.occupancy = 100  # 100% capacity

        # Step 50 times
        prev_rho = edge.congestion
        for _ in range(50):
            congestion_mgr.step(dt=1.0)
            self.assertGreaterEqual(edge.congestion, prev_rho)  # monotonic increase
            prev_rho = edge.congestion

        # After 50 seconds (5 time constants), should be > 0.98
        self.assertGreater(edge.congestion, 0.98)

    def test_dynamic_reroute_avoiding_closed_corridor(self):
        """
        Verify that Dynamic A* automatically routes around a closed edge
        and that Invariant I1 (no closed edge in path) holds strictly.
        """
        # Baseline path 0 -> 8
        res1 = find_shortest_path(self.graph, 0, 8)
        self.assertTrue(res1.success)
        self.assertIn((0, 1), res1.edges_traversed)

        # Now close edge (0, 1)
        self.graph.close_edge(0, 1, reason="Pipeline Blast")

        # Re-route
        res2 = find_shortest_path(self.graph, 0, 8)
        self.assertTrue(res2.success)
        # Should now detour through node 3
        self.assertNotIn((0, 1), res2.edges_traversed)
        self.assertEqual(res2.path[0], 0)
        self.assertEqual(res2.path[1], 3)

        # Invariant I1 assertion on all traversed edges
        for u, v in res2.edges_traversed:
            self.assertNotIn((u, v), self.graph.closed_edges)

    def test_siren_mode_reduces_congestion_cost(self):
        """Verify siren mode attenuates congestion penalty."""
        edge = self.graph.get_edge(0, 1)
        self.assertIsNotNone(edge)
        edge.congestion = 1.0  # full congestion

        cost_normal = calculate_edge_cost(edge, is_siren=False)
        cost_siren = calculate_edge_cost(edge, is_siren=True)

        self.assertLess(cost_siren, cost_normal)

    def test_headless_demo_simulation_execution(self):
        """Assert the entire demo simulation executes cleanly to completion headless."""
        sim = DemoSimulation(rows=6, cols=6, headless=True)
        metrics = sim.run()
        self.assertGreater(metrics["total_sim_time"], 0.0)
        self.assertEqual(metrics["reroute_occurred"], 1.0)
        self.assertEqual(sim.vehicle_node, sim.goal_node)

    def test_osm_road_network_ingestion_and_scc(self):
        """Verify real OpenStreetMap ingestion and Strongly Connected Component extraction."""
        from Aether.core.osm_loader import OSMRoadNetworkLoader
        graph = OSMRoadNetworkLoader.load_preset_map("manhattan")
        self.assertGreater(graph.num_nodes, 1000)
        self.assertGreater(graph.num_edges, 1500)

        # Test reachability between arbitrary nodes in the SCC
        nodes = sorted(list(graph.nodes.keys()))
        res = find_shortest_path(graph, nodes[0], nodes[-1])
        self.assertTrue(res.success)
        self.assertGreater(len(res.path), 1)

    def test_bidirectional_astar_equivalence(self):
        """Assert Bidirectional A* achieves optimal cost identical to Dijkstra and Dynamic A*."""
        from Aether.core.traversal import find_shortest_path_bidirectional, find_shortest_path_dijkstra
        res_dijkstra = find_shortest_path_dijkstra(self.graph, 0, 8)
        res_astar = find_shortest_path(self.graph, 0, 8)
        res_bi = find_shortest_path_bidirectional(self.graph, 0, 8)

        self.assertTrue(res_dijkstra.success)
        self.assertTrue(res_astar.success)
        self.assertTrue(res_bi.success)

        # All algorithms must find the exact same optimal cost
        self.assertAlmostEqual(res_dijkstra.total_cost_seconds, res_astar.total_cost_seconds, places=5)
        self.assertAlmostEqual(res_astar.total_cost_seconds, res_bi.total_cost_seconds, places=5)

    def test_large_scale_simulation_manhattan_headless(self):
        """Verify LargeScaleSimulation executes cleanly on real Manhattan OSM graph."""
        from Aether.simulation.large_scale_demo import LargeScaleSimulation
        sim = LargeScaleSimulation(map_type="manhattan", headless=True)
        res = sim.run()
        self.assertTrue(res["reroute_successful"])
        self.assertTrue(res["invariant_i1_held"])
        self.assertGreater(res["sim_time"], 0.0)


if __name__ == "__main__":
    unittest.main()
