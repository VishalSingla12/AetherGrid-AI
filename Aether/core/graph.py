"""
Aether Directed Graph Engine
Implements the time-varying directed transportation network G_t = (V, E_t).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import math


class TerrainType(Enum):
    """Terrain classification and base impedance multipliers."""
    HIGHWAY = "highway"
    ARTERIAL = "arterial"
    URBAN = "urban"
    ALLEY = "alley"
    OFFROAD = "offroad"

    @property
    def multiplier(self) -> float:
        """Returns the dimensionless terrain multiplier tau_e."""
        multipliers = {
            TerrainType.HIGHWAY: 1.00,
            TerrainType.ARTERIAL: 1.25,
            TerrainType.URBAN: 1.45,
            TerrainType.ALLEY: 1.90,
            TerrainType.OFFROAD: 3.10,
        }
        return multipliers[self]


@dataclass
class NodeData:
    """Represents a topological intersection or facility node in V."""
    id: int
    x: float
    y: float
    label: str = ""
    lat: Optional[float] = None
    lon: Optional[float] = None
    is_depot: bool = False
    is_hospital: bool = False
    is_charging_station: bool = False

    def distance_to(self, other: "NodeData") -> float:
        """Euclidean distance in meters to another node."""
        return math.hypot(self.x - other.x, self.y - other.y)


@dataclass
class EdgeData:
    """Represents a directed road corridor e = (u, v) in E_t."""
    u: int
    v: int
    length_meters: float
    free_flow_time_seconds: float  # ell_e
    terrain: TerrainType = TerrainType.URBAN
    capacity: int = 50  # K_e
    occupancy: int = 0  # n_e(t)
    congestion: float = 0.0  # rho_e(t) in [0.0, 1.0]
    is_open: bool = True
    street_name: str = ""
    closure_reason: str = ""
    is_hazard: bool = False
    hazard_penalty_seconds: float = 0.0  # beta
    hazard_label: str = ""

    @property
    def max_speed_mps(self) -> float:
        """Maximum baseline speed in meters per second."""
        if self.free_flow_time_seconds <= 0:
            return 25.0
        return self.length_meters / self.free_flow_time_seconds


class DirectedGraph:
    """
    High-performance directed transportation graph supporting dynamic
    topological mutations (closures/reopenings) and dynamic attributes.
    """

    def __init__(self, name: str = "AetherGrid"):
        self.name = name
        self.nodes: Dict[int, NodeData] = {}
        # adj[u][v] = EdgeData
        self.adj: Dict[int, Dict[int, EdgeData]] = {}
        # rev_adj[v][u] = EdgeData
        self.rev_adj: Dict[int, Dict[int, EdgeData]] = {}
        self.closed_edges: Set[Tuple[int, int]] = set()
        self.max_network_speed: float = 30.0  # meters per second (approx 108 km/h)

    def add_node(
        self,
        node_id: int,
        x: float,
        y: float,
        label: str = "",
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        is_depot: bool = False,
        is_hospital: bool = False,
        is_charging_station: bool = False,
    ) -> NodeData:
        """Adds a node to the graph."""
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists in graph.")
        node = NodeData(
            id=node_id,
            x=x,
            y=y,
            label=label or f"Node_{node_id}",
            lat=lat,
            lon=lon,
            is_depot=is_depot,
            is_hospital=is_hospital,
            is_charging_station=is_charging_station,
        )
        self.nodes[node_id] = node
        self.adj[node_id] = {}
        self.rev_adj[node_id] = {}
        return node

    def add_edge(
        self,
        u: int,
        v: int,
        length_meters: Optional[float] = None,
        free_flow_speed_mps: float = 16.67,  # ~60 km/h
        terrain: TerrainType = TerrainType.URBAN,
        capacity: int = 50,
        bidirectional: bool = False,
        street_name: str = "",
    ) -> EdgeData:
        """
        Adds a directed edge from u to v. If bidirectional is True, adds v -> u as well.
        """
        if u not in self.nodes or v not in self.nodes:
            raise KeyError(f"Both nodes ({u}, {v}) must exist prior to edge creation.")
        if u == v:
            raise ValueError(f"Self-loops are forbidden: ({u}, {v}).")

        if length_meters is None:
            length_meters = self.nodes[u].distance_to(self.nodes[v])

        if length_meters <= 0:
            raise ValueError(f"Edge length must be strictly positive: {length_meters}")

        free_flow_time = length_meters / max(1.0, free_flow_speed_mps)

        edge = EdgeData(
            u=u,
            v=v,
            length_meters=length_meters,
            free_flow_time_seconds=free_flow_time,
            terrain=terrain,
            capacity=max(1, capacity),
            street_name=street_name,
        )

        self.adj[u][v] = edge
        self.rev_adj[v][u] = edge

        # Track global maximum speed for admissible heuristics
        speed = edge.max_speed_mps
        if speed > self.max_network_speed:
            self.max_network_speed = speed

        if bidirectional:
            self.add_edge(
                u=v,
                v=u,
                length_meters=length_meters,
                free_flow_speed_mps=free_flow_speed_mps,
                terrain=terrain,
                capacity=capacity,
                bidirectional=False,
                street_name=street_name,
            )

        return edge

    def get_edge(self, u: int, v: int) -> Optional[EdgeData]:
        """Returns EdgeData if edge exists, else None."""
        return self.adj.get(u, {}).get(v)

    def close_edge(self, u: int, v: int, reason: str = "Structural Closure") -> bool:
        """
        Removes an edge from the active network E_t (Invariant I1).
        Sets is_open to False and records in closed_edges set.
        """
        edge = self.get_edge(u, v)
        if not edge:
            return False
        edge.is_open = False
        edge.closure_reason = reason
        self.closed_edges.add((u, v))
        return True

    def reopen_edge(self, u: int, v: int) -> bool:
        """Restores a closed edge back to E_t."""
        edge = self.get_edge(u, v)
        if not edge:
            return False
        edge.is_open = True
        edge.closure_reason = ""
        self.closed_edges.discard((u, v))
        return True

    def inject_hazard(
        self,
        u: int,
        v: int,
        penalty_beta: float = 45.0,
        label: str = "Hazmat Hazard",
    ) -> bool:
        """
        Applies a hazard penalty beta to edge (u, v) without removing it from E_t.
        """
        edge = self.get_edge(u, v)
        if not edge:
            return False
        edge.is_hazard = True
        edge.hazard_penalty_seconds = max(0.0, penalty_beta)
        edge.hazard_label = label
        return True

    def remove_hazard(self, u: int, v: int) -> bool:
        """Clears hazard state from edge (u, v)."""
        edge = self.get_edge(u, v)
        if not edge:
            return False
        edge.is_hazard = False
        edge.hazard_penalty_seconds = 0.0
        edge.hazard_label = ""
        return True

    def get_open_out_edges(self, u: int) -> List[Tuple[int, EdgeData]]:
        """
        Returns list of (neighbor_v, edge) for all strictly OPEN outgoing edges.
        Closed edges are excluded, enforcing Invariant I1 at the graph layer.
        """
        if u not in self.adj:
            return []
        return [
            (v, edge)
            for v, edge in self.adj[u].items()
            if edge.is_open and (u, v) not in self.closed_edges
        ]

    def get_all_edges(self) -> List[EdgeData]:
        """Returns a flat list of all edges in the graph."""
        edges = []
        for u in self.adj:
            for v, edge in self.adj[u].items():
                edges.append(edge)
        return edges

    @property
    def num_nodes(self) -> int:
        return len(self.nodes)

    @property
    def num_edges(self) -> int:
        return sum(len(neighbors) for neighbors in self.adj.values())

    @property
    def num_open_edges(self) -> int:
        return self.num_edges - len(self.closed_edges)

    @classmethod
    def generate_grid_network(
        cls,
        rows: int = 8,
        cols: int = 8,
        spacing_meters: float = 200.0,
        highway_rows: Optional[List[int]] = None,
        highway_cols: Optional[List[int]] = None,
        river_col: Optional[int] = None,
        bridge_rows: Optional[List[int]] = None,
    ) -> "DirectedGraph":
        """
        Factory method to generate a rich, realistic urban road grid
        with multi-tier road classes (highways, arterials, urban streets, alleys),
        depots, hospitals, and optional geographic obstacles (river barrier with bridges).
        """
        graph = cls(name=f"UrbanGrid_{rows}x{cols}")
        highway_rows = highway_rows or []
        highway_cols = highway_cols or []
        bridge_rows = bridge_rows or []

        # 1. Create nodes with geodetic mapping
        center_lat = 40.7580
        center_lon = -73.9855
        earth_r = 6371000.0
        grid_w = cols * spacing_meters
        grid_h = rows * spacing_meters

        for r in range(rows):
            for c in range(cols):
                node_id = r * cols + c
                x = c * spacing_meters
                y = r * spacing_meters

                # Geodetic projection around center
                rel_x = x - (grid_w / 2.0)
                rel_y = y - (grid_h / 2.0)
                lat = center_lat + (rel_y / earth_r) * (180.0 / math.pi)
                lon = center_lon + (rel_x / (earth_r * math.cos(math.radians(center_lat)))) * (180.0 / math.pi)

                # Assign facilities to designated intersections
                is_depot = (r == 0 and c == 0) or (r == rows - 1 and c == cols - 1)
                is_hospital = (r == rows // 2 and c == cols // 2) or (r == 0 and c == cols - 1)
                is_charging = (r % 4 == 0 and c % 4 == 0)

                graph.add_node(
                    node_id=node_id,
                    x=x,
                    y=y,
                    label=f"Int_{r}_{c}",
                    lat=lat,
                    lon=lon,
                    is_depot=is_depot,
                    is_hospital=is_hospital,
                    is_charging_station=is_charging,
                )

        # 2. Create edges (horizontal and vertical)
        for r in range(rows):
            for c in range(cols):
                u = r * cols + c

                # East neighbor
                if c + 1 < cols:
                    v_east = r * cols + (c + 1)
                    # Check if river barrier blocks this east-west connection
                    is_river_crossing = (river_col is not None and c == river_col)
                    allow_connection = (not is_river_crossing) or (r in bridge_rows)

                    if allow_connection:
                        # Determine road classification
                        if r in highway_rows:
                            terrain = TerrainType.HIGHWAY
                            speed = 28.0  # ~100 km/h
                            cap = 120
                        elif r % 2 == 0:
                            terrain = TerrainType.ARTERIAL
                            speed = 18.0  # ~65 km/h
                            cap = 70
                        elif r % 3 == 0:
                            terrain = TerrainType.ALLEY
                            speed = 10.0  # ~36 km/h
                            cap = 20
                        else:
                            terrain = TerrainType.URBAN
                            speed = 14.0  # ~50 km/h
                            cap = 45

                        graph.add_edge(
                            u=u,
                            v=v_east,
                            length_meters=spacing_meters,
                            free_flow_speed_mps=speed,
                            terrain=terrain,
                            capacity=cap,
                            bidirectional=True,
                        )

                # South neighbor
                if r + 1 < rows:
                    v_south = (r + 1) * cols + c
                    if c in highway_cols:
                        terrain = TerrainType.HIGHWAY
                        speed = 28.0
                        cap = 120
                    elif c % 2 == 0:
                        terrain = TerrainType.ARTERIAL
                        speed = 18.0
                        cap = 70
                    else:
                        terrain = TerrainType.URBAN
                        speed = 14.0
                        cap = 45

                    graph.add_edge(
                        u=u,
                        v=v_south,
                        length_meters=spacing_meters,
                        free_flow_speed_mps=speed,
                        terrain=terrain,
                        capacity=cap,
                        bidirectional=True,
                    )

        return graph
