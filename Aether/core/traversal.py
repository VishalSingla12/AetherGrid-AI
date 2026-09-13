"""
Aether Path Traversal & Dynamic Routing Engine
Implements deterministic, admissible Dynamic A*, Bidirectional A*, and Dijkstra search
over priced network G_t with rich computational telemetry.
"""

from dataclasses import dataclass, field
import heapq
import math
import time
from typing import Dict, List, Optional, Set, Tuple
from .graph import DirectedGraph, EdgeData
from .pricing import CostModelParameters, calculate_edge_cost, compute_admissible_heuristic


@dataclass
class RouteResult:
    """Encapsulates the outcome and computational metrics of a pathfinding query."""
    success: bool
    path: List[int] = field(default_factory=list)
    total_cost_seconds: float = float("inf")
    nodes_expanded: int = 0
    frontier_peak_size: int = 0
    cost_evaluations: int = 0
    search_time_ms: float = 0.0
    edge_costs: List[float] = field(default_factory=list)
    edges_traversed: List[Tuple[int, int]] = field(default_factory=list)
    street_names: List[str] = field(default_factory=list)
    explored_nodes: List[int] = field(default_factory=list)

    @property
    def search_efficiency(self) -> float:
        """Ratio of path length to expanded nodes (1.0 = perfect direct line search)."""
        if self.nodes_expanded <= 0 or not self.success:
            return 0.0
        return len(self.path) / self.nodes_expanded


def find_shortest_path(
    graph: DirectedGraph,
    start_id: int,
    goal_id: int,
    weather_multiplier: float = 1.0,
    params: Optional[CostModelParameters] = None,
    is_siren: bool = False,
    max_expansions: Optional[int] = None,
) -> RouteResult:
    """
    Dynamic A* search with Euclidean admissible heuristic and deterministic tie-breaking.
    """
    t_start = time.perf_counter()

    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return RouteResult(success=False, total_cost_seconds=float("inf"))

    if start_id == goal_id:
        return RouteResult(success=True, path=[start_id], total_cost_seconds=0.0)

    p = params or CostModelParameters()
    goal_node = graph.nodes[goal_id]
    max_speed = graph.max_network_speed
    expansion_limit = max_expansions or (3 * graph.num_nodes)

    initial_h = compute_admissible_heuristic(graph.nodes[start_id], goal_node, max_speed)
    frontier: List[Tuple[float, float, int]] = [(initial_h, initial_h, start_id)]

    g_score: Dict[int, float] = {start_id: 0.0}
    parent_map: Dict[int, Tuple[int, EdgeData, float]] = {}
    visited: Set[int] = set()
    explored_nodes: List[int] = []
    nodes_expanded = 0
    frontier_peak = 1
    cost_evals = 0

    while frontier:
        f, h, current = heapq.heappop(frontier)

        if current in visited:
            continue
        visited.add(current)
        explored_nodes.append(current)
        nodes_expanded += 1

        if current == goal_id:
            # Path reconstruction
            path = [goal_id]
            edge_costs = []
            edges_traversed = []
            streets = []
            curr = goal_id

            while curr in parent_map:
                prev, edge, cost = parent_map[curr]
                path.append(prev)
                edge_costs.append(cost)
                edges_traversed.append((prev, curr))
                streets.append(edge.closure_reason or "City Street")
                curr = prev

            path.reverse()
            edge_costs.reverse()
            edges_traversed.reverse()
            streets.reverse()

            total_cost = g_score[goal_id]
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0

            # Invariant I1 assertion
            for u_seg, v_seg in edges_traversed:
                assert (u_seg, v_seg) not in graph.closed_edges, (
                    f"Invariant I1 Violation: Path traverses closed edge ({u_seg}, {v_seg})"
                )

            return RouteResult(
                success=True,
                path=path,
                total_cost_seconds=total_cost,
                nodes_expanded=nodes_expanded,
                frontier_peak_size=frontier_peak,
                cost_evaluations=cost_evals,
                search_time_ms=elapsed_ms,
                edge_costs=edge_costs,
                edges_traversed=edges_traversed,
                street_names=streets,
                explored_nodes=explored_nodes,
            )

        if nodes_expanded > expansion_limit:
            break

        for neighbor, edge in graph.get_open_out_edges(current):
            if neighbor in visited:
                continue

            cost_evals += 1
            edge_cost = calculate_edge_cost(
                edge, weather_multiplier=weather_multiplier, params=p, is_siren=is_siren
            )

            if math.isinf(edge_cost):
                continue

            tentative_g = g_score[current] + edge_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                h_neighbor = compute_admissible_heuristic(graph.nodes[neighbor], goal_node, max_speed)
                f_neighbor = tentative_g + h_neighbor
                parent_map[neighbor] = (current, edge, edge_cost)
                heapq.heappush(frontier, (f_neighbor, h_neighbor, neighbor))

        if len(frontier) > frontier_peak:
            frontier_peak = len(frontier)

    elapsed_ms = (time.perf_counter() - t_start) * 1000.0
    return RouteResult(
        success=False,
        total_cost_seconds=float("inf"),
        nodes_expanded=nodes_expanded,
        frontier_peak_size=frontier_peak,
        cost_evaluations=cost_evals,
        search_time_ms=elapsed_ms,
        explored_nodes=explored_nodes,
    )


def find_shortest_path_dijkstra(
    graph: DirectedGraph,
    start_id: int,
    goal_id: int,
    weather_multiplier: float = 1.0,
    params: Optional[CostModelParameters] = None,
    is_siren: bool = False,
) -> RouteResult:
    """
    Uninformed Dijkstra baseline (h = 0.0). Used as comparator to prove A* heuristic speedup.
    """
    t_start = time.perf_counter()
    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return RouteResult(success=False)

    p = params or CostModelParameters()
    frontier: List[Tuple[float, int]] = [(0.0, start_id)]
    g_score: Dict[int, float] = {start_id: 0.0}
    parent_map: Dict[int, Tuple[int, EdgeData, float]] = {}
    visited: Set[int] = set()
    explored_nodes: List[int] = []
    nodes_expanded = 0
    cost_evals = 0

    while frontier:
        cost, current = heapq.heappop(frontier)

        if current in visited:
            continue
        visited.add(current)
        explored_nodes.append(current)
        nodes_expanded += 1

        if current == goal_id:
            path = [goal_id]
            edge_costs = []
            edges_traversed = []
            curr = goal_id
            while curr in parent_map:
                prev, edge, c = parent_map[curr]
                path.append(prev)
                edge_costs.append(c)
                edges_traversed.append((prev, curr))
                curr = prev

            path.reverse()
            edge_costs.reverse()
            edges_traversed.reverse()
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0

            return RouteResult(
                success=True,
                path=path,
                total_cost_seconds=g_score[goal_id],
                nodes_expanded=nodes_expanded,
                cost_evaluations=cost_evals,
                search_time_ms=elapsed_ms,
                edge_costs=edge_costs,
                edges_traversed=edges_traversed,
                explored_nodes=explored_nodes,
            )

        for neighbor, edge in graph.get_open_out_edges(current):
            if neighbor in visited:
                continue

            cost_evals += 1
            edge_cost = calculate_edge_cost(edge, weather_multiplier=weather_multiplier, params=p, is_siren=is_siren)
            if math.isinf(edge_cost):
                continue

            tentative_g = g_score[current] + edge_cost
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                parent_map[neighbor] = (current, edge, edge_cost)
                heapq.heappush(frontier, (tentative_g, neighbor))

    elapsed_ms = (time.perf_counter() - t_start) * 1000.0
    return RouteResult(success=False, nodes_expanded=nodes_expanded, cost_evaluations=cost_evals, search_time_ms=elapsed_ms, explored_nodes=explored_nodes)


def find_shortest_path_bidirectional(
    graph: DirectedGraph,
    start_id: int,
    goal_id: int,
    weather_multiplier: float = 1.0,
    params: Optional[CostModelParameters] = None,
    is_siren: bool = False,
) -> RouteResult:
    """
    Bidirectional search: explores forward from start and backward from goal simultaneously.
    Reduces the search space radius from R to R/2, yielding up to 4x node expansion savings on large networks.
    """
    t_start = time.perf_counter()
    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return RouteResult(success=False)

    if start_id == goal_id:
        return RouteResult(success=True, path=[start_id], total_cost_seconds=0.0)

    p = params or CostModelParameters()
    max_speed = graph.max_network_speed
    goal_node = graph.nodes[goal_id]
    start_node = graph.nodes[start_id]

    # Forward search structures
    f_frontier: List[Tuple[float, float, int]] = []
    f_h_init = compute_admissible_heuristic(start_node, goal_node, max_speed)
    heapq.heappush(f_frontier, (f_h_init, f_h_init, start_id))
    f_g: Dict[int, float] = {start_id: 0.0}
    f_parent: Dict[int, Tuple[int, EdgeData, float]] = {}
    f_visited: Set[int] = set()

    # Backward search structures
    b_frontier: List[Tuple[float, float, int]] = []
    b_h_init = compute_admissible_heuristic(goal_node, start_node, max_speed)
    heapq.heappush(b_frontier, (b_h_init, b_h_init, goal_id))
    b_g: Dict[int, float] = {goal_id: 0.0}
    b_parent: Dict[int, Tuple[int, EdgeData, float]] = {}  # forward edge along incoming
    b_visited: Set[int] = set()

    best_cost = float("inf")
    meeting_node: Optional[int] = None
    nodes_expanded = 0
    cost_evals = 0
    explored_nodes: List[int] = []

    while f_frontier and b_frontier:
        # Check termination condition
        min_f = f_frontier[0][0]
        min_b = b_frontier[0][0]
        if min_f + min_b >= best_cost * 1.5 and meeting_node is not None:
            break

        # Expand forward step
        if f_frontier:
            _, _, u = heapq.heappop(f_frontier)
            if u not in f_visited:
                f_visited.add(u)
                explored_nodes.append(u)
                nodes_expanded += 1

                if u in b_visited:
                    total = f_g[u] + b_g[u]
                    if total < best_cost:
                        best_cost = total
                        meeting_node = u

                for v, edge in graph.get_open_out_edges(u):
                    if v in f_visited:
                        continue
                    cost_evals += 1
                    c = calculate_edge_cost(edge, weather_multiplier=weather_multiplier, params=p, is_siren=is_siren)
                    if math.isinf(c):
                        continue
                    tentative = f_g[u] + c
                    if v not in f_g or tentative < f_g[v]:
                        f_g[v] = tentative
                        h_v = compute_admissible_heuristic(graph.nodes[v], goal_node, max_speed)
                        f_parent[v] = (u, edge, c)
                        heapq.heappush(f_frontier, (tentative + h_v, h_v, v))
                        if v in b_visited and tentative + b_g[v] < best_cost:
                            best_cost = tentative + b_g[v]
                            meeting_node = v

        # Expand backward step
        if b_frontier:
            _, _, v = heapq.heappop(b_frontier)
            if v not in b_visited:
                b_visited.add(v)
                explored_nodes.append(v)
                nodes_expanded += 1

                if v in f_visited:
                    total = f_g[v] + b_g[v]
                    if total < best_cost:
                        best_cost = total
                        meeting_node = v

                # Examine incoming edges u -> v
                if v in graph.rev_adj:
                    for u, edge in graph.rev_adj[v].items():
                        if not edge.is_open or (u, v) in graph.closed_edges:
                            continue
                        if u in b_visited:
                            continue
                        cost_evals += 1
                        c = calculate_edge_cost(edge, weather_multiplier=weather_multiplier, params=p, is_siren=is_siren)
                        if math.isinf(c):
                            continue
                        tentative = b_g[v] + c
                        if u not in b_g or tentative < b_g[u]:
                            b_g[u] = tentative
                            h_u = compute_admissible_heuristic(graph.nodes[u], start_node, max_speed)
                            b_parent[u] = (v, edge, c)
                            heapq.heappush(b_frontier, (tentative + h_u, h_u, u))
                            if u in f_visited and f_g[u] + tentative < best_cost:
                                best_cost = f_g[u] + tentative
                                meeting_node = u

    if meeting_node is None:
        return find_shortest_path(graph, start_id, goal_id, weather_multiplier, params, is_siren)

    # Reconstruct combined bidirectional path
    # Forward half: start -> meeting_node
    f_path = []
    f_costs = []
    f_edges = []
    curr = meeting_node
    while curr in f_parent:
        prev, edge, c = f_parent[curr]
        f_path.append(curr)
        f_costs.append(c)
        f_edges.append((prev, curr))
        curr = prev
    f_path.append(start_id)
    f_path.reverse()
    f_costs.reverse()
    f_edges.reverse()

    # Backward half: meeting_node -> goal
    b_path = []
    b_costs = []
    b_edges = []
    curr = meeting_node
    while curr in b_parent:
        nxt, edge, c = b_parent[curr]
        b_costs.append(c)
        b_edges.append((curr, nxt))
        curr = nxt
        b_path.append(curr)

    full_path = f_path + b_path
    full_costs = f_costs + b_costs
    full_edges = f_edges + b_edges
    elapsed_ms = (time.perf_counter() - t_start) * 1000.0

    return RouteResult(
        success=True,
        path=full_path,
        total_cost_seconds=sum(full_costs),
        nodes_expanded=nodes_expanded,
        cost_evaluations=cost_evals,
        search_time_ms=elapsed_ms,
        edge_costs=full_costs,
        edges_traversed=full_edges,
        explored_nodes=explored_nodes,
    )


def find_shortest_path_weighted(
    graph: DirectedGraph,
    start_id: int,
    goal_id: int,
    weather_multiplier: float = 1.0,
    params: Optional[CostModelParameters] = None,
    is_siren: bool = False,
    epsilon: float = 2.5,
) -> RouteResult:
    """
    Weighted A* search with inflated heuristic: f(n) = g(n) + epsilon * h(n).
    
    With epsilon > 1.0, the search becomes more greedy — it aggressively follows
    the heuristic direction, expanding fewer nodes but potentially finding a
    suboptimal path. This produces VISIBLY DIFFERENT routes from standard A* 
    (which is optimal) because:
    - Standard A* balances cost-so-far vs estimated-remaining equally
    - Weighted A* overweights the estimate, making it prefer "as-the-crow-flies" shortcuts
    - This causes it to prefer direct corridors even when slightly more expensive
    
    Path quality guarantee: cost(weighted) <= epsilon * cost(optimal)
    """
    t_start = time.perf_counter()

    if start_id not in graph.nodes or goal_id not in graph.nodes:
        return RouteResult(success=False, total_cost_seconds=float("inf"))

    if start_id == goal_id:
        return RouteResult(success=True, path=[start_id], total_cost_seconds=0.0)

    p = params or CostModelParameters()
    goal_node = graph.nodes[goal_id]
    max_speed = graph.max_network_speed
    expansion_limit = 3 * graph.num_nodes

    initial_h = compute_admissible_heuristic(graph.nodes[start_id], goal_node, max_speed)
    frontier: List[Tuple[float, float, int]] = [(epsilon * initial_h, initial_h, start_id)]

    g_score: Dict[int, float] = {start_id: 0.0}
    parent_map: Dict[int, Tuple[int, EdgeData, float]] = {}
    visited: Set[int] = set()
    explored_nodes: List[int] = []
    nodes_expanded = 0
    frontier_peak = 1
    cost_evals = 0

    while frontier:
        f, h, current = heapq.heappop(frontier)

        if current in visited:
            continue
        visited.add(current)
        explored_nodes.append(current)
        nodes_expanded += 1

        if current == goal_id:
            path = [goal_id]
            edge_costs = []
            edges_traversed = []
            streets = []
            curr = goal_id

            while curr in parent_map:
                prev, edge, cost = parent_map[curr]
                path.append(prev)
                edge_costs.append(cost)
                edges_traversed.append((prev, curr))
                streets.append(edge.closure_reason or "City Street")
                curr = prev

            path.reverse()
            edge_costs.reverse()
            edges_traversed.reverse()
            streets.reverse()

            total_cost = g_score[goal_id]
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0

            return RouteResult(
                success=True,
                path=path,
                total_cost_seconds=total_cost,
                nodes_expanded=nodes_expanded,
                frontier_peak_size=frontier_peak,
                cost_evaluations=cost_evals,
                search_time_ms=elapsed_ms,
                edge_costs=edge_costs,
                edges_traversed=edges_traversed,
                street_names=streets,
                explored_nodes=explored_nodes,
            )

        if nodes_expanded > expansion_limit:
            break

        for neighbor, edge in graph.get_open_out_edges(current):
            if neighbor in visited:
                continue

            cost_evals += 1
            edge_cost = calculate_edge_cost(
                edge, weather_multiplier=weather_multiplier, params=p, is_siren=is_siren
            )

            if math.isinf(edge_cost):
                continue

            tentative_g = g_score[current] + edge_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                h_neighbor = compute_admissible_heuristic(graph.nodes[neighbor], goal_node, max_speed)
                # KEY DIFFERENCE: inflate heuristic by epsilon for greedy bias
                f_neighbor = tentative_g + epsilon * h_neighbor
                parent_map[neighbor] = (current, edge, edge_cost)
                heapq.heappush(frontier, (f_neighbor, h_neighbor, neighbor))

        if len(frontier) > frontier_peak:
            frontier_peak = len(frontier)

    elapsed_ms = (time.perf_counter() - t_start) * 1000.0
    return RouteResult(
        success=False,
        total_cost_seconds=float("inf"),
        nodes_expanded=nodes_expanded,
        frontier_peak_size=frontier_peak,
        cost_evaluations=cost_evals,
        search_time_ms=elapsed_ms,
        explored_nodes=explored_nodes,
    )


def compute_eta_matrix(
    graph: DirectedGraph,
    origins: List[int],
    destinations: List[int],
    weather_multiplier: float = 1.0,
) -> Tuple[List[List[float]], float]:
    """
    Computes an |I| x |B| travel time cost matrix across all origins and destinations.
    Returns (matrix, compute_time_ms).
    """
    t0 = time.perf_counter()
    matrix: List[List[float]] = []

    for u in origins:
        row: List[float] = []
        for v in destinations:
            res = find_shortest_path(graph, u, v, weather_multiplier=weather_multiplier)
            row.append(res.total_cost_seconds if res.success else 1e5)
        matrix.append(row)

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return matrix, elapsed_ms

