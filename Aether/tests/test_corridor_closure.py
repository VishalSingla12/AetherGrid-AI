"""
Aether Corridor Closure & Invariant I1 Verification Test Suite
Verifies that:
1. Corridor block expansion captures all micro-segments between intersections.
2. Closing a corridor forces an immediate, deterministic detour with ZERO closed edge traversals (Invariant I1).
3. Reopening restores all edges and preserves original street names.
4. Severed network condition (destination unreachable) cleanly yields success=False without crashing.
"""

import unittest
from Aether.core.graph import DirectedGraph, TerrainType
from Aether.core.hazards import HazardManager
from Aether.core.traversal import (
    find_shortest_path,
    find_shortest_path_bidirectional,
    find_shortest_path_weighted,
    find_shortest_path_dijkstra,
)
from Aether.web.server import SimulationStateManager


class TestCorridorClosure(unittest.TestCase):
    """Verifies block-level corridor closure and Invariant I1 enforcement."""

    def setUp(self):
        """
        Constructs a grid with a multi-segmented corridor (Avenue) and a parallel detour (Boulevard).
        Nodes:
          0: Origin
          1 -> 2 -> 3: Micro-segments of "Main Avenue" (u=1 to 2, 2 to 3)
          4: Intersection / Destination
          5 -> 6 -> 7: Parallel "Detour Boulevard"
        """
        self.graph = DirectedGraph("CorridorCity")
        # Add nodes
        for nid, (x, y) in {
            0: (0.0, 0.0),
            1: (50.0, 0.0),
            2: (100.0, 0.0),
            3: (150.0, 0.0),
            4: (200.0, 0.0),
            5: (0.0, 100.0),
            6: (100.0, 100.0),
            7: (200.0, 100.0),
        }.items():
            self.graph.add_node(nid, x=x, y=y, lat=40.7 + y * 1e-4, lon=-74.0 + x * 1e-4)

        # Primary route: 0 -> 1 -> 2 -> 3 -> 4 ("Main Avenue", 4 segments)
        self.graph.add_edge(0, 1, length_meters=50.0, street_name="Cross Street", bidirectional=True)
        self.graph.add_edge(1, 2, length_meters=50.0, street_name="Main Avenue", bidirectional=True)
        self.graph.add_edge(2, 3, length_meters=50.0, street_name="Main Avenue", bidirectional=True)
        self.graph.add_edge(3, 4, length_meters=50.0, street_name="Main Avenue", bidirectional=True)

        # Detour route: 0 -> 5 -> 6 -> 7 -> 4 ("Detour Boulevard")
        self.graph.add_edge(0, 5, length_meters=100.0, street_name="Side Connector", bidirectional=True)
        self.graph.add_edge(5, 6, length_meters=100.0, street_name="Detour Boulevard", bidirectional=True)
        self.graph.add_edge(6, 7, length_meters=100.0, street_name="Detour Boulevard", bidirectional=True)
        self.graph.add_edge(7, 4, length_meters=100.0, street_name="Side Connector", bidirectional=True)

    def _create_manager(self):
        mgr = SimulationStateManager(default_map="grid16")
        mgr.graph = self.graph
        mgr.hazard_mgr = HazardManager(self.graph)
        return mgr

    def test_corridor_block_expansion(self):
        """Verify that selecting one micro-segment expands across the entire named block."""
        mgr = self._create_manager()

        # Query corridor block for micro-segment (2, 3)
        block = mgr.get_corridor_block(2, 3, max_meters=300.0)
        block_set = set(block)
        self.assertIn((2, 3), block_set)
        self.assertIn((3, 2), block_set)
        self.assertIn((1, 2), block_set)
        self.assertIn((2, 1), block_set)
        self.assertIn((3, 4), block_set)
        self.assertIn((4, 3), block_set)
        # Should NOT include Cross Street (0, 1) or Detour Boulevard (5, 6)
        self.assertNotIn((0, 1), block_set)
        self.assertNotIn((5, 6), block_set)

    def test_corridor_closure_detour_invariant_i1(self):
        """
        Verify that toggling closure on a micro-segment closes the corridor,
        forcing an immediate detour with strictly 0 closed edge traversals across all algorithms.
        """
        mgr = self._create_manager()

        # Baseline: initial route chooses Main Avenue (shorter: 200m vs 400m)
        r_init = find_shortest_path_bidirectional(mgr.graph, 0, 4)
        self.assertTrue(r_init.success)
        self.assertIn((1, 2), r_init.edges_traversed)

        # Toggle closure on single micro-segment (2, 3)
        res = mgr.toggle_closure(2, 3)
        self.assertTrue(res["success"])
        self.assertFalse(res["is_open"])
        self.assertGreaterEqual(res["active_closures_count"], 4)

        # Test all 4 algorithms under closure
        for name, algo_fn in [
            ("A*", find_shortest_path),
            ("Bidirectional A*", find_shortest_path_bidirectional),
            ("Weighted A*", lambda g, s, d: find_shortest_path_weighted(g, s, d, epsilon=2.0)),
            ("Dijkstra", find_shortest_path_dijkstra),
        ]:
            res_route = algo_fn(mgr.graph, 0, 4)
            self.assertTrue(res_route.success, f"{name} should find detour via Detour Boulevard")
            
            # INVARIANT I1: Zero closed edges traversed
            for u_seg, v_seg in res_route.edges_traversed:
                self.assertNotIn(
                    (u_seg, v_seg),
                    mgr.graph.closed_edges,
                    f"Invariant I1 Violation in {name}: traversed closed edge ({u_seg}, {v_seg})",
                )
            # Must take the detour route (0 -> 5 -> 6 -> 7 -> 4)
            self.assertIn((5, 6), res_route.edges_traversed)
            self.assertIn((6, 7), res_route.edges_traversed)

    def test_corridor_reopen_and_street_name_preservation(self):
        """Verify reopening restores edges and preserves street_name."""
        mgr = self._create_manager()

        # Close
        mgr.toggle_closure(2, 3)
        self.assertIn((2, 3), mgr.graph.closed_edges)

        # Reopen
        res = mgr.toggle_closure(2, 3)
        self.assertTrue(res["is_open"])
        self.assertEqual(len(mgr.graph.closed_edges), 0)

        # Verify street_name intact
        edge = mgr.graph.get_edge(2, 3)
        self.assertEqual(edge.street_name, "Main Avenue")
        self.assertTrue(edge.is_open)

    def test_severed_network_unreachable(self):
        """Verify that if both primary and detour routes are blocked, success=False is cleanly returned."""
        mgr = self._create_manager()

        # Close Main Avenue
        mgr.toggle_closure(2, 3)
        # Close Detour Boulevard
        mgr.toggle_closure(5, 6)

        # Both paths to Node 4 are now blocked
        r_bi = find_shortest_path_bidirectional(mgr.graph, 0, 4)
        self.assertFalse(r_bi.success)
        self.assertEqual(r_bi.total_cost_seconds, float("inf"))

        r_dijk = find_shortest_path_dijkstra(mgr.graph, 0, 4)
        self.assertFalse(r_dijk.success)


class TestHazMatExposureEvaluation(unittest.TestCase):
    """
    Verifies that hazardous materials exposure evaluation correctly clusters
    contiguous micro-segments into distinct incident sites and applies
    appropriate emergency PPE severity tiers.
    """

    def setUp(self):
        self.mgr = SimulationStateManager(default_map="grid16")

    def test_single_block_multisegment_spill_classified_as_level_1(self):
        """
        A single physical spill site spanning 9 micro-segments of Park Avenue South
        must be evaluated as 1 Incident Site (Level 1 Low Exposure, Level C PPE),
        NOT artificially inflated to Level 3 Critical Hot Zone.
        """
        g = DirectedGraph("HazMatTestCity")
        # Build 10 nodes (9 micro-segments of 10m each) along "Park Avenue South"
        for i in range(10):
            g.add_node(i, x=float(i * 10), y=0.0)
        edges = []
        for i in range(9):
            g.add_edge(i, i + 1, length_meters=10.0, street_name="Park Avenue South")
            edges.append((i, i + 1))
            # Mark all 9 micro-segments as hazardous
            edge = g.get_edge(i, i + 1)
            edge.is_hazard = True
            edge.hazard_penalty_beta = 45.0

        self.mgr.graph = g
        res = self.mgr._evaluate_hazmat_exposure(edges)

        self.assertTrue(res["has_hazmat"])
        self.assertEqual(res["incident_sites_count"], 1)
        self.assertEqual(res["segments_count"], 9)
        self.assertEqual(res["count"], 1)
        self.assertEqual(res["severity_code"], 1)
        self.assertEqual(res["severity_level"], "LEVEL 1 (LOW EXPOSURE)")
        self.assertIn("Level C PPE", res["ppe_gear"])
        self.assertIn("Park Avenue South", res["affected_streets"])
        self.assertIn("9 segments", res["crew_directive"])

    def test_multi_site_spill_classified_as_level_2(self):
        """
        Two distinct spill sites separated by a clean arterial road (> 50m)
        must be evaluated as 2 Incident Sites (Level 2 Elevated Toxicity, Level B SCBA).
        """
        g = DirectedGraph("HazMatMultiCity")
        # Site 1: nodes 0->1->2 (Park Ave S, 2 segments)
        # Clean road: nodes 2->3 (50m clean)
        # Site 2: nodes 3->4->5 (Broadway, 2 segments)
        for i in range(6):
            g.add_node(i, x=float(i * 30), y=0.0)

        g.add_edge(0, 1, length_meters=15.0, street_name="Park Avenue South")
        g.add_edge(1, 2, length_meters=15.0, street_name="Park Avenue South")
        g.add_edge(2, 3, length_meters=60.0, street_name="Clean Corridor")
        g.add_edge(3, 4, length_meters=15.0, street_name="Broadway")
        g.add_edge(4, 5, length_meters=15.0, street_name="Broadway")

        for u, v in [(0, 1), (1, 2), (3, 4), (4, 5)]:
            e = g.get_edge(u, v)
            e.is_hazard = True
            e.hazard_penalty_beta = 45.0

        self.mgr.graph = g
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
        res = self.mgr._evaluate_hazmat_exposure(edges)

        self.assertTrue(res["has_hazmat"])
        self.assertEqual(res["incident_sites_count"], 2)
        self.assertEqual(res["segments_count"], 4)
        self.assertEqual(res["count"], 2)
        self.assertEqual(res["severity_code"], 2)
        self.assertEqual(res["severity_level"], "LEVEL 2 (ELEVATED TOXICITY)")
        self.assertIn("Level B PPE", res["ppe_gear"])
        self.assertIn("2 incident sites", res["crew_directive"])

    def test_four_distinct_sites_classified_as_level_3(self):
        """
        Four separate spill sites across town must escalate to Level 3 Critical Hot Zone (Level A PPE).
        """
        g = DirectedGraph("HazMatFourCity")
        # Pre-populate nodes 0 to 30
        for i in range(30):
            g.add_node(i, x=float(i * 20), y=0.0)

        # Build 4 separate sites with clean connectors in between
        edges = []
        curr = 0
        for site_idx in range(4):
            # 2 haz segments
            for _ in range(2):
                nxt = curr + 1
                g.add_edge(curr, nxt, length_meters=20.0, street_name=f"Avenue {site_idx}")
                e = g.get_edge(curr, nxt)
                e.is_hazard = True
                edges.append((curr, nxt))
                curr = nxt
            if site_idx < 3:
                # Clean connector of 80m
                nxt = curr + 1
                g.add_edge(curr, nxt, length_meters=80.0, street_name="Clean Buffer")
                edges.append((curr, nxt))
                curr = nxt

        self.mgr.graph = g
        res = self.mgr._evaluate_hazmat_exposure(edges)

        self.assertTrue(res["has_hazmat"])
        self.assertEqual(res["incident_sites_count"], 4)
        self.assertEqual(res["severity_code"], 3)
        self.assertEqual(res["severity_level"], "LEVEL 3 (CRITICAL BIOHAZARD HOT ZONE)")
        self.assertIn("Level A PPE", res["ppe_gear"])


if __name__ == "__main__":
    unittest.main()
