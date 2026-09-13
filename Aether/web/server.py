"""
Aether Mission Control HTTP & API Server
Zero-dependency high-performance server providing real-time OpenStreetMap visualization,
dynamic routing APIs, disruption controls, and algorithmic comparison telemetry.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import math
import os
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from Aether.core.graph import DirectedGraph, TerrainType
from Aether.core.pricing import CostModelParameters, calculate_edge_cost
from Aether.core.weather import WeatherManager, WeatherType
from Aether.core.congestion import CongestionManager
from Aether.core.hazards import HazardManager
from Aether.core.osm_loader import OSMRoadNetworkLoader
from Aether.core.traversal import (
    find_shortest_path,
    find_shortest_path_bidirectional,
    find_shortest_path_dijkstra,
    find_shortest_path_weighted,
    RouteResult,
)


class SimulationStateManager:
    """Thread-safe state container for the active simulation and map topology."""

    def __init__(self, default_map: str = "manhattan"):
        self.lock = threading.Lock()
        self.map_name = default_map
        self.graph: DirectedGraph = self._load_graph(default_map)
        self.weather_mgr = WeatherManager(WeatherType.CLEAR)
        self.congestion_mgr = CongestionManager(self.graph, smoothing_time_constant=15.0)
        self.hazard_mgr = HazardManager(self.graph)

        # Active mission state
        self.start_node: int = 0
        self.goal_node: int = len(self.graph.nodes) - 1
        self._ensure_valid_mission_endpoints()

    def _load_graph(self, map_type: str) -> DirectedGraph:
        map_type = map_type.lower()
        if map_type in ("manhattan_large", "manhattan_wide", "manhattan_full", "large", "manhattan"):
            return OSMRoadNetworkLoader.load_preset_map("manhattan_large")
        elif map_type in ("manhattan_midtown", "midtown"):
            return OSMRoadNetworkLoader.load_preset_map("manhattan_midtown")
        elif map_type in ("grid50", "megacity"):
            return DirectedGraph.generate_grid_network(
                rows=50, cols=50, spacing_meters=150.0, highway_rows=[12, 37], highway_cols=[12, 37],
                river_col=25, bridge_rows=[6, 18, 30, 42]
            )
        elif map_type in ("grid32", "metro"):
            return DirectedGraph.generate_grid_network(
                rows=32, cols=32, spacing_meters=180.0, highway_rows=[8, 24], highway_cols=[8, 24],
                river_col=16, bridge_rows=[4, 12, 20, 28]
            )
        elif map_type in ("grid16", "small"):
            return DirectedGraph.generate_grid_network(
                rows=16, cols=16, spacing_meters=200.0, highway_rows=[4, 11], highway_cols=[4, 11],
                river_col=8, bridge_rows=[3, 12]
            )
        else:
            return OSMRoadNetworkLoader.load_preset_map("manhattan_large")

    def _ensure_valid_mission_endpoints(self) -> None:
        nodes = sorted(list(self.graph.nodes.keys()))
        if nodes:
            self.start_node = nodes[0]
            # Select distant node (~70% of network diameter) for realistic urban journeys
            dest_idx = int(len(nodes) * 0.70)
            self.goal_node = nodes[min(len(nodes) - 1, max(1, dest_idx))]

    def switch_map(self, map_type: str) -> Dict[str, Any]:
        with self.lock:
            self.map_name = map_type
            self.graph = self._load_graph(map_type)
            self.congestion_mgr = CongestionManager(self.graph)
            self.hazard_mgr = HazardManager(self.graph)
            self._ensure_valid_mission_endpoints()
            return {
                "name": self.graph.name,
                "num_nodes": self.graph.num_nodes,
                "num_edges": self.graph.num_edges,
            }

    def get_network_payload(self) -> Dict[str, Any]:
        with self.lock:
            nodes_data = []
            lats = []
            lons = []

            for n in self.graph.nodes.values():
                lat = n.lat if n.lat is not None else 40.7580
                lon = n.lon if n.lon is not None else -73.9855
                lats.append(lat)
                lons.append(lon)
                nodes_data.append({
                    "id": n.id,
                    "lat": lat,
                    "lon": lon,
                    "label": n.label,
                    "is_depot": n.is_depot,
                    "is_hospital": n.is_hospital,
                })

            edges_data = []
            for edge in self.graph.get_all_edges():
                c = calculate_edge_cost(edge, weather_multiplier=self.weather_mgr.multiplier)
                edges_data.append({
                    "u": edge.u,
                    "v": edge.v,
                    "cost": round(c, 2) if not math.isinf(c) else -1,
                    "length": round(edge.length_meters, 1),
                    "terrain": edge.terrain.value,
                    "street": getattr(edge, "street_name", None) or edge.closure_reason or "City Street",
                    "is_open": edge.is_open and (edge.u, edge.v) not in self.graph.closed_edges,
                    "is_hazard": edge.is_hazard,
                    "congestion": round(edge.congestion, 3),
                })

            center = [
                sum(lats) / max(1, len(lats)),
                sum(lons) / max(1, len(lons)),
            ]
            bounds = [
                [min(lats), min(lons)],
                [max(lats), max(lons)],
            ]

            return {
                "name": self.graph.name,
                "num_nodes": self.graph.num_nodes,
                "num_edges": self.graph.num_edges,
                "center": center,
                "bounds": bounds,
                "weather": {
                    "type": self.weather_mgr.current_weather.name,
                    "multiplier": self.weather_mgr.multiplier,
                },
                "nodes": nodes_data,
                "edges": edges_data,
                "start_node": self.start_node,
                "goal_node": self.goal_node,
            }

    def _evaluate_hazmat_exposure(self, edges_traversed: List[Tuple[int, int]]) -> Dict[str, Any]:
        """
        Evaluates hazardous materials exposure along a route and derives
        the operational PPE gear level and mission command directive.
        
        Distinguishes between distinct incident sites (contiguous hazardous corridor
        zones or distinct affected street corridors) and raw microscopic OSM segments.
        
        Tiers based on distinct incident sites and exposure extent:
        - CLEAR (0 sites): Standard Uniform
        - LEVEL 1 (1 localized spill site, <= 450m and <= 20 micro-segments): Level C PPE (N95/P100 Respirator + Splash Suit, Recirc Cabin Air)
        - LEVEL 2 (2-3 distinct spill sites OR extended corridor > 450m): Level B PPE (Mandatory SCBA + Chemical Suit, Alert ER Decon)
        - LEVEL 3 (4+ distinct spill sites OR extreme systemic exposure > 1000m): Level A PPE (Vapor-Tight Encapsulation + HazMat Escort)
        """
        hazmat_edges = []
        affected_streets = []
        total_hazmat_meters = 0.0

        raw_clusters: List[List[Tuple[int, int, Any]]] = []
        current_cluster: List[Tuple[int, int, Any]] = []
        path_edge_data: List[Tuple[int, int, bool, float, str]] = []

        for u, v in edges_traversed:
            edge = self.graph.get_edge(u, v)
            if not edge:
                continue
            is_haz = bool(edge.is_hazard)
            length = float(edge.length_meters)
            st = getattr(edge, "street_name", None) or edge.closure_reason or f"Corridor ({u}↔{v})"
            path_edge_data.append((u, v, is_haz, length, st))

            if is_haz:
                hazmat_edges.append((u, v))
                current_cluster.append((u, v, edge))
                total_hazmat_meters += length
                if st not in affected_streets:
                    affected_streets.append(st)
            else:
                if current_cluster:
                    raw_clusters.append(current_cluster)
                    current_cluster = []
        if current_cluster:
            raw_clusters.append(current_cluster)

        segments_count = len(hazmat_edges)
        if segments_count == 0:
            return {
                "has_hazmat": False,
                "incident_sites_count": 0,
                "segments_count": 0,
                "total_meters": 0.0,
                "count": 0,
                "severity_level": "CLEAR",
                "severity_code": 0,
                "ppe_gear": "Standard EMT Uniform",
                "crew_directive": "Standard operating protocol. Corridor is clean.",
                "affected_streets": [],
            }

        # Bridge micro-gaps (e.g. 1 non-hazardous intersection connector <= 35m) between clusters
        # to prevent artificial inflation of incident site count across micro-edges
        distinct_sites = len(raw_clusters)
        if len(raw_clusters) > 1:
            haz_indices = [i for i, data in enumerate(path_edge_data) if data[2]]
            counted_sites = 1
            for k in range(1, len(haz_indices)):
                prev_idx = haz_indices[k - 1]
                curr_idx = haz_indices[k]
                gap_len = curr_idx - prev_idx - 1
                if gap_len > 0:
                    gap_dist = sum(path_edge_data[g][3] for g in range(prev_idx + 1, curr_idx))
                    if gap_len > 1 or gap_dist > 35.0:
                        counted_sites += 1
            distinct_sites = counted_sites

        incident_sites_count = max(1, distinct_sites)

        # Severity calibration:
        # 1 incident site within standard corridor length (<= 450m and <= 20 micro-segments) -> LEVEL 1
        # 2-3 incident sites OR continuous extended corridor (> 450m) -> LEVEL 2
        # 4+ incident sites OR massive multi-kilometer hot zone (> 1000m) -> LEVEL 3
        if incident_sites_count == 1 and total_hazmat_meters <= 450.0 and segments_count <= 20:
            severity = "LEVEL 1 (LOW EXPOSURE)"
            code = 1
            ppe = "Level C PPE: N95/P100 Respirator + Splash Suit"
            dist_str = f"{int(round(total_hazmat_meters))}m"
            directive = (
                f"Single incident corridor ({segments_count} segments, {dist_str}). "
                f"Don Level C respirators and switch ambulance HVAC to internal recirculation."
            )
        elif incident_sites_count <= 3 and total_hazmat_meters <= 1000.0:
            severity = "LEVEL 2 (ELEVATED TOXICITY)"
            code = 2
            ppe = "Level B PPE: SCBA (Self-Contained Breathing Apparatus) + Chemical Suit"
            dist_str = f"{int(round(total_hazmat_meters))}m"
            site_label = f"{incident_sites_count} incident sites" if incident_sites_count > 1 else "extended corridor"
            directive = (
                f"Elevated contamination ({site_label}, {segments_count} segments, {dist_str}). "
                f"Mandatory SCBA donning. Seal cabin and notify receiving ER decontamination."
            )
        else:
            severity = "LEVEL 3 (CRITICAL BIOHAZARD HOT ZONE)"
            code = 3
            ppe = "Level A PPE: Vapor-Tight Encapsulated Suit + SCBA"
            dist_str = f"{int(round(total_hazmat_meters))}m"
            site_label = f"{incident_sites_count} incident sites" if incident_sites_count > 1 else "massive hot zone"
            directive = (
                f"CRITICAL CONTAMINATION ({site_label}, {segments_count} segments, {dist_str}). "
                f"Level A full encapsulation required. Request HazMat decontamination escort."
            )

        return {
            "has_hazmat": True,
            "incident_sites_count": incident_sites_count,
            "segments_count": segments_count,
            "total_meters": round(total_hazmat_meters, 1),
            "count": incident_sites_count,
            "severity_level": severity,
            "severity_code": code,
            "ppe_gear": ppe,
            "crew_directive": directive,
            "affected_streets": affected_streets[:6],
        }

    def compute_route(
        self,
        start_id: int,
        goal_id: int,
        algorithm: str = "bi_astar",
        is_siren: bool = False,
    ) -> Dict[str, Any]:
        with self.lock:
            algo = algorithm.lower()
            t0 = time.perf_counter()

            if algo in ("dijkstra",):
                res = find_shortest_path_dijkstra(
                    self.graph, start_id, goal_id, weather_multiplier=self.weather_mgr.multiplier, is_siren=is_siren
                )
                algo_name = "Dijkstra (Uninformed)"
            elif algo in ("astar", "dynamic_astar"):
                res = find_shortest_path(
                    self.graph, start_id, goal_id, weather_multiplier=self.weather_mgr.multiplier, is_siren=is_siren
                )
                algo_name = "Dynamic A*"
            else:
                res = find_shortest_path_bidirectional(
                    self.graph, start_id, goal_id, weather_multiplier=self.weather_mgr.multiplier, is_siren=is_siren
                )
                algo_name = "Bidirectional Dynamic A*"

            elapsed_ms = (time.perf_counter() - t0) * 1000.0

            if not res.success:
                return {
                    "success": False,
                    "algorithm": algo_name,
                    "search_time_ms": elapsed_ms,
                    "nodes_expanded": res.nodes_expanded,
                    "error": "Destination unreachable under current topological constraints.",
                }

            # Build coordinate array for Leaflet polyline
            path_coords = []
            for nid in res.path:
                node = self.graph.nodes.get(nid)
                if node:
                    lat = node.lat if node.lat is not None else 40.7580
                    lon = node.lon if node.lon is not None else -73.9855
                    path_coords.append([round(lat, 6), round(lon, 6)])

            street_names = []
            for u, v in res.edges_traversed:
                e = self.graph.get_edge(u, v)
                street_names.append(getattr(e, "street_name", None) or (e.closure_reason if e and e.closure_reason else "City Corridor"))

            # Pruning ratio relative to graph size
            pruned_pct = max(0.0, (1.0 - (res.nodes_expanded / max(1, self.graph.num_nodes))) * 100.0)

            # Sample explored frontier coordinates
            explored_coords = []
            if res.explored_nodes:
                sample_step = max(1, len(res.explored_nodes) // 350)
                for nid in res.explored_nodes[::sample_step][:350]:
                    node = self.graph.nodes.get(nid)
                    if node and node.lat is not None and node.lon is not None:
                        explored_coords.append([round(node.lat, 6), round(node.lon, 6)])

            hazmat_status = self._evaluate_hazmat_exposure(res.edges_traversed)

            return {
                "success": True,
                "algorithm": algo_name,
                "total_cost_seconds": round(res.total_cost_seconds, 2),
                "search_time_ms": round(elapsed_ms, 3),
                "nodes_expanded": res.nodes_expanded,
                "frontier_peak": res.frontier_peak_size,
                "search_efficiency": round(res.search_efficiency, 3),
                "pruned_pct": round(pruned_pct, 1),
                "cost_evals": res.cost_evaluations,
                "path_node_ids": res.path,
                "path_coords": path_coords,
                "explored_coords": explored_coords,
                "streets": street_names[:15],
                "total_waypoints": len(res.path),
                "hazmat_status": hazmat_status,
            }

    def compare_all_algorithms(self, start_id: int, goal_id: int) -> Dict[str, Any]:
        with self.lock:
            def _coords_from_path(p_ids):
                coords = []
                for nid in p_ids:
                    node = self.graph.nodes.get(nid)
                    if node and node.lat is not None and node.lon is not None:
                        coords.append([round(node.lat, 6), round(node.lon, 6)])
                return coords

            def _sample_coords(node_ids, max_pts=350):
                if not node_ids:
                    return []
                step = max(1, len(node_ids) // max_pts)
                coords = []
                for nid in node_ids[::step][:max_pts]:
                    node = self.graph.nodes.get(nid)
                    if node and node.lat is not None and node.lon is not None:
                        coords.append([round(node.lat, 6), round(node.lon, 6)])
                return coords

            # Dijkstra (exhaustive optimal baseline)
            t0 = time.perf_counter()
            d_res = find_shortest_path_dijkstra(self.graph, start_id, goal_id, weather_multiplier=self.weather_mgr.multiplier)
            d_time = (time.perf_counter() - t0) * 1000.0

            # Weighted A* (epsilon=2.5, greedy near-optimal — DIFFERENT PATH)
            t0 = time.perf_counter()
            w_res = find_shortest_path_weighted(self.graph, start_id, goal_id, weather_multiplier=self.weather_mgr.multiplier, epsilon=2.5)
            w_time = (time.perf_counter() - t0) * 1000.0

            # Bidirectional A* (efficient optimal)
            t0 = time.perf_counter()
            b_res = find_shortest_path_bidirectional(self.graph, start_id, goal_id, weather_multiplier=self.weather_mgr.multiplier)
            b_time = (time.perf_counter() - t0) * 1000.0

            d_exp = max(1, d_res.nodes_expanded)
            w_pruned = max(0.0, ((d_exp - w_res.nodes_expanded) / d_exp) * 100.0)
            b_pruned = max(0.0, ((d_exp - b_res.nodes_expanded) / d_exp) * 100.0)

            # Calculate path divergence metric (how different are the paths)
            if d_res.success and w_res.success:
                d_set = set(d_res.path)
                w_set = set(w_res.path)
                shared = len(d_set & w_set)
                total = len(d_set | w_set)
                divergence_pct = round((1.0 - shared / max(1, total)) * 100.0, 1) if total > 0 else 0.0
            else:
                divergence_pct = 0.0

            d_hazmat = self._evaluate_hazmat_exposure(d_res.edges_traversed)
            w_hazmat = self._evaluate_hazmat_exposure(w_res.edges_traversed)
            b_hazmat = self._evaluate_hazmat_exposure(b_res.edges_traversed)
            active_hazmat = b_hazmat if b_res.success else (w_hazmat if w_res.success else d_hazmat)

            return {
                "success": b_res.success or w_res.success or d_res.success,
                "cost_seconds": round(b_res.total_cost_seconds, 2) if b_res.success else (round(w_res.total_cost_seconds, 2) if w_res.success else round(d_res.total_cost_seconds, 2)),
                "path_divergence_pct": divergence_pct,
                "hazmat_status": active_hazmat,
                "comparison": [
                    {
                        "key": "dijkstra",
                        "name": "Dijkstra (Uninformed Baseline)",
                        "time_ms": round(d_time, 3),
                        "nodes_expanded": d_res.nodes_expanded,
                        "pruned_pct": 0.0,
                        "speedup": 1.0,
                        "cost_seconds": round(d_res.total_cost_seconds, 2) if d_res.success else -1,
                        "path_coords": _coords_from_path(d_res.path),
                        "explored_coords": _sample_coords(d_res.explored_nodes, 400),
                        "hazmat_status": d_hazmat,
                    },
                    {
                        "key": "weighted_astar",
                        "name": "Weighted A* (ε=2.5 Greedy)",
                        "time_ms": round(w_time, 3),
                        "nodes_expanded": w_res.nodes_expanded,
                        "pruned_pct": round(w_pruned, 1),
                        "speedup": round(d_time / max(0.001, w_time), 2),
                        "cost_seconds": round(w_res.total_cost_seconds, 2) if w_res.success else -1,
                        "path_coords": _coords_from_path(w_res.path),
                        "explored_coords": _sample_coords(w_res.explored_nodes, 400),
                        "hazmat_status": w_hazmat,
                    },
                    {
                        "key": "bi_astar",
                        "name": "Bidirectional A* (Optimal)",
                        "time_ms": round(b_time, 3),
                        "nodes_expanded": b_res.nodes_expanded,
                        "pruned_pct": round(b_pruned, 1),
                        "speedup": round(d_time / max(0.001, b_time), 2),
                        "cost_seconds": round(b_res.total_cost_seconds, 2) if b_res.success else -1,
                        "path_coords": _coords_from_path(b_res.path),
                        "explored_coords": _sample_coords(b_res.explored_nodes, 400),
                        "hazmat_status": b_hazmat,
                    },
                ],
            }

    def get_corridor_block(self, u: int, v: int, max_meters: float = 250.0) -> List[Tuple[int, int]]:
        """
        Expands an edge (u, v) into a full contiguous street block between major intersections.
        Prevents micro-segmentation leakage where closing one 10-meter edge leaves parallel
        or adjacent sub-edges open.
        """
        edge = self.graph.get_edge(u, v)
        if not edge:
            return []
        st_name = getattr(edge, "street_name", None) or edge.closure_reason or ""
        st_clean = st_name.strip().lower()

        visited_edges: Set[Tuple[int, int]] = set([(u, v)])
        if self.graph.get_edge(v, u):
            visited_edges.add((v, u))

        def _node_streets(nid: int) -> Set[str]:
            sts = set()
            for _, e in self.graph.adj.get(nid, {}).items():
                s = (getattr(e, "street_name", None) or e.closure_reason or "").strip().lower()
                if s:
                    sts.add(s)
            for _, e in self.graph.rev_adj.get(nid, {}).items():
                s = (getattr(e, "street_name", None) or e.closure_reason or "").strip().lower()
                if s:
                    sts.add(s)
            return sts

        # Forward propagation from v
        q_fwd: List[Tuple[int, float]] = [(v, 0.0)]
        seen_fwd: Set[int] = {u, v}
        while q_fwd:
            curr, cum_dist = q_fwd.pop(0)
            streets = _node_streets(curr)
            if len(streets) > 1 and curr != v:
                continue
            if cum_dist >= max_meters:
                continue

            for nxt_v, nxt_e in self.graph.adj.get(curr, {}).items():
                nxt_st = (getattr(nxt_e, "street_name", None) or nxt_e.closure_reason or "").strip().lower()
                if (nxt_st == st_clean or not nxt_st) and (curr, nxt_v) not in visited_edges:
                    visited_edges.add((curr, nxt_v))
                    if self.graph.get_edge(nxt_v, curr):
                        visited_edges.add((nxt_v, curr))
                    if nxt_v not in seen_fwd:
                        seen_fwd.add(nxt_v)
                        q_fwd.append((nxt_v, cum_dist + nxt_e.length_meters))

        # Backward propagation from u
        q_bwd: List[Tuple[int, float]] = [(u, 0.0)]
        seen_bwd: Set[int] = {u, v}
        while q_bwd:
            curr, cum_dist = q_bwd.pop(0)
            streets = _node_streets(curr)
            if len(streets) > 1 and curr != u:
                continue
            if cum_dist >= max_meters:
                continue

            for prev_u, prev_e in self.graph.rev_adj.get(curr, {}).items():
                prev_st = (getattr(prev_e, "street_name", None) or prev_e.closure_reason or "").strip().lower()
                if (prev_st == st_clean or not prev_st) and (prev_u, curr) not in visited_edges:
                    visited_edges.add((prev_u, curr))
                    if self.graph.get_edge(curr, prev_u):
                        visited_edges.add((curr, prev_u))
                    if prev_u not in seen_bwd:
                        seen_bwd.add(prev_u)
                        q_bwd.append((prev_u, cum_dist + prev_e.length_meters))

        return list(visited_edges)

    def toggle_closure(self, u: int, v: int) -> Dict[str, Any]:
        with self.lock:
            edge = self.graph.get_edge(u, v)
            if not edge:
                return {"success": False, "error": f"Edge ({u}, {v}) does not exist"}

            block = self.get_corridor_block(u, v)
            if not block:
                block = [(u, v)]

            st_name = getattr(edge, "street_name", None) or edge.closure_reason or "City Corridor"

            if edge.is_open:
                for cu, cv in block:
                    self.hazard_mgr.inject_edge_closure(cu, cv, reason=f"Closed Block: {st_name}", duration_seconds=1800.0, bidirectional=True)
                is_open = False
            else:
                for cu, cv in block:
                    self.graph.reopen_edge(cu, cv)
                    if (cu, cv) in self.hazard_mgr.active_closures:
                        del self.hazard_mgr.active_closures[(cu, cv)]
                    if self.graph.get_edge(cv, cu):
                        self.graph.reopen_edge(cv, cu)
                        if (cv, cu) in self.hazard_mgr.active_closures:
                            del self.hazard_mgr.active_closures[(cv, cu)]
                is_open = True

            return {
                "success": True,
                "u": u,
                "v": v,
                "is_open": is_open,
                "active_closures_count": len(self.graph.closed_edges),
                "corridor_street": st_name,
                "affected_edges": [{"u": cu, "v": cv} for cu, cv in block],
            }

    def inject_hazard(self, u: int, v: int, penalty_beta: float = 45.0) -> Dict[str, Any]:
        with self.lock:
            edge = self.graph.get_edge(u, v)
            if not edge:
                return {"success": False, "error": f"Edge ({u}, {v}) does not exist"}

            block = self.get_corridor_block(u, v)
            if not block:
                block = [(u, v)]

            st_name = getattr(edge, "street_name", None) or edge.closure_reason or "City Corridor"
            for cu, cv in block:
                self.hazard_mgr.inject_edge_hazard(cu, cv, penalty_beta=penalty_beta, label=f"Hazmat: {st_name}", bidirectional=True)

            return {
                "success": True,
                "u": u,
                "v": v,
                "penalty": penalty_beta,
                "active_hazards_count": len(self.hazard_mgr.active_hazards),
                "corridor_street": st_name,
                "affected_edges": [{"u": cu, "v": cv} for cu, cv in block],
            }

    def set_weather(self, weather_str: str) -> Dict[str, Any]:
        with self.lock:
            w_map = {
                "clear": WeatherType.CLEAR,
                "rain": WeatherType.RAIN,
                "fog": WeatherType.FOG,
                "snow": WeatherType.SNOW,
            }
            w_type = w_map.get(weather_str.lower(), WeatherType.CLEAR)
            self.weather_mgr.set_weather(w_type)
            return {
                "weather": w_type.name,
                "multiplier": w_type.multiplier,
            }

    def inject_traffic_surge(self, delta_vehicles: int = 50) -> Dict[str, Any]:
        with self.lock:
            # Primary urban bottlenecks and transit arteries that jam during rush-hour
            rush_bottlenecks = (
                "columbus", "11th", "fdr", "7th avenue", "seventh avenue",
                "34th", "42nd", "canal", "lexington", "2nd avenue", "second avenue"
            )
            affected_count = 0
            for edge in self.graph.get_all_edges():
                st = (getattr(edge, "street_name", None) or edge.closure_reason or "").lower()
                if any(b in st for b in rush_bottlenecks):
                    edge.congestion = 0.92
                    edge.occupancy = int(edge.capacity * 1.85)
                    affected_count += 1
                elif edge.terrain in (TerrainType.HIGHWAY, TerrainType.ARTERIAL):
                    if (edge.u + edge.v) % 3 == 0:
                        edge.congestion = 0.80
                        edge.occupancy = int(edge.capacity * 1.3)
                        affected_count += 1
                    else:
                        edge.congestion = 0.22
                        edge.occupancy = int(edge.capacity * 0.3)
                else:
                    edge.congestion = 0.10
                    edge.occupancy = int(edge.capacity * 0.15)
            
            # Step EWMA to synchronize state
            self.congestion_mgr.step(dt=1.0)
            stats = self.congestion_mgr.get_network_statistics()
            return {
                "success": True,
                "mean_congestion": round(stats["mean_congestion"], 3),
                "total_vehicles": stats["total_vehicles"],
                "affected_corridors": affected_count,
            }

    def reset_disruptions(self) -> Dict[str, Any]:
        with self.lock:
            for u, v in list(self.graph.closed_edges):
                self.graph.reopen_edge(u, v)
            self.hazard_mgr.active_closures.clear()
            self.hazard_mgr.active_hazards.clear()
            for edge in self.graph.get_all_edges():
                edge.is_hazard = False
                edge.hazard_penalty_seconds = 0.0
                edge.occupancy = 0
                edge.congestion = 0.05
            self.congestion_mgr.step(dt=1.0)
            stats = self.congestion_mgr.get_network_statistics()
            return {
                "success": True,
                "mean_congestion": round(stats["mean_congestion"], 3),
                "active_closures": 0,
                "active_hazards": 0,
            }

    def get_edges_status(self) -> Dict[str, Any]:
        with self.lock:
            edges_update = []
            for edge in self.graph.get_all_edges():
                c = calculate_edge_cost(edge, weather_multiplier=self.weather_mgr.multiplier)
                edges_update.append({
                    "u": edge.u,
                    "v": edge.v,
                    "cost": round(c, 2) if not math.isinf(c) else -1,
                    "congestion": round(edge.congestion, 3),
                    "is_open": edge.is_open and (edge.u, edge.v) not in self.graph.closed_edges,
                    "is_hazard": edge.is_hazard,
                })
            return {
                "weather_multiplier": self.weather_mgr.multiplier,
                "edges": edges_update,
            }


# Global state manager instance
STATE = SimulationStateManager(default_map="manhattan_large")


class AetherHTTPRequestHandler(BaseHTTPRequestHandler):
    """Processes REST API queries and serves the Mission Control web interface."""

    def log_message(self, format, *args):
        # Suppress routine GET logging for high-frequency polling
        if "GET /api/" in format % args:
            return
        super().log_message(format, *args)

    def _set_headers(self, content_type: str = "application/json", status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed_path = self.path.split("?")[0]

        if parsed_path in ("/", "/index.html"):
            html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
            if os.path.exists(html_path):
                with open(html_path, "rb") as f:
                    content = f.read()
                self._set_headers("text/html; charset=utf-8")
                self.wfile.write(content)
            else:
                self._set_headers("text/plain", 404)
                self.wfile.write(b"Static interface not found.")
            return

        elif parsed_path == "/api/network":
            payload = STATE.get_network_payload()
            self._set_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        elif parsed_path == "/api/status":
            con = STATE.congestion_mgr.get_network_statistics()
            data = {
                "map": STATE.graph.name,
                "num_nodes": STATE.graph.num_nodes,
                "num_edges": STATE.graph.num_edges,
                "weather": STATE.weather_mgr.current_weather.name,
                "weather_multiplier": STATE.weather_mgr.multiplier,
                "active_closures": len(STATE.graph.closed_edges),
                "active_hazards": len(STATE.hazard_mgr.active_hazards),
                "mean_congestion": round(con["mean_congestion"], 3),
            }
            self._set_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        elif parsed_path == "/api/edges_status":
            payload = STATE.get_edges_status()
            self._set_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        else:
            self._set_headers("text/plain", 404)
            self.wfile.write(b"Resource not found.")

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            req_data = json.loads(body)
        except Exception:
            req_data = {}

        parsed_path = self.path.split("?")[0]

        if parsed_path == "/api/route":
            start_id = req_data.get("start_id", STATE.start_node)
            goal_id = req_data.get("goal_id", STATE.goal_node)
            algorithm = req_data.get("algorithm", "bi_astar")
            is_siren = req_data.get("is_siren", False)

            res = STATE.compute_route(start_id, goal_id, algorithm=algorithm, is_siren=is_siren)
            self._set_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))

        elif parsed_path == "/api/compare_routes":
            start_id = req_data.get("start_id", STATE.start_node)
            goal_id = req_data.get("goal_id", STATE.goal_node)

            res = STATE.compare_all_algorithms(start_id, goal_id)
            self._set_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))

        elif parsed_path == "/api/closure":
            u = int(req_data.get("u", 0))
            v = int(req_data.get("v", 1))
            res = STATE.toggle_closure(u, v)
            self._set_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))

        elif parsed_path == "/api/hazard":
            u = int(req_data.get("u", 0))
            v = int(req_data.get("v", 1))
            penalty = float(req_data.get("penalty", 45.0))
            res = STATE.inject_hazard(u, v, penalty_beta=penalty)
            self._set_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))

        elif parsed_path == "/api/weather":
            w_str = req_data.get("weather", "clear")
            res = STATE.set_weather(w_str)
            self._set_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))

        elif parsed_path == "/api/traffic_surge":
            delta = int(req_data.get("delta", 35))
            res = STATE.inject_traffic_surge(delta)
            self._set_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))

        elif parsed_path == "/api/reset":
            res = STATE.reset_disruptions()
            self._set_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))

        elif parsed_path == "/api/load_map":
            map_name = req_data.get("map", "manhattan_large")
            res = STATE.switch_map(map_name)
            self._set_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))

        else:
            self._set_headers("text/plain", 404)
            self.wfile.write(b"Endpoint not found.")


def start_mission_control_server(
    port: int = 8080,
    host: str = "0.0.0.0",
    initial_map: str = "manhattan_large",
    block: bool = True,
) -> HTTPServer:
    """Instantiates and launches the Aether Mission Control web server."""
    global STATE
    STATE = SimulationStateManager(default_map=initial_map)

    server_address = (host, port)
    httpd = HTTPServer(server_address, AetherHTTPRequestHandler)

    print(f"\n" + "=" * 76)
    print(f"  AETHERGRID-AI MISSION CONTROL & OPENSTREETMAP VISUALIZATION SERVER")
    print(f"=" * 76)
    print(f"  [+] Server Listening on: http://localhost:{port}")
    print(f"  [+] OpenStreetMap Layer: Live CartoDB & Standard OSM Tiles Enabled")
    print(f"  [+] Active Network Topology: {STATE.graph.name}")
    print(f"  [+] Total Intersections/Nodes: {STATE.graph.num_nodes}")
    print(f"  [+] Total Directed Corridors: {STATE.graph.num_edges}")
    print(f"  [+] Live Routing Suite: Dynamic A*, Bidirectional A*, Dijkstra")
    print(f"=" * 76 + "\n")

    if block:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Shutting down Mission Control server...")
            httpd.server_close()
    else:
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()
        print(f"[+] Server running in background thread on port {port}")

    return httpd


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    map_arg = sys.argv[2] if len(sys.argv) > 2 else "manhattan"
    start_mission_control_server(port=port_arg, initial_map=map_arg, block=True)
