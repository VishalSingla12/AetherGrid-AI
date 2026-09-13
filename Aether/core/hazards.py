"""
Aether Hazard and Closure Management Engine
Manages dynamic corridor closures (excised from E_t) and hazardous environmental
conditions (additive penalty beta) with spatial radius injection and duration timers.
"""

from dataclasses import dataclass
import math
from typing import Dict, List, Optional, Set, Tuple
from .graph import DirectedGraph, EdgeData


@dataclass
class HazardRecord:
    u: int
    v: int
    penalty_beta: float
    label: str
    remaining_duration: float


@dataclass
class ClosureRecord:
    u: int
    v: int
    reason: str
    remaining_duration: float


class HazardManager:
    """
    Coordinates topological disruptions across the transportation network.
    Maintains strict distinction between closures (Invariant I1) and hazards.
    """

    def __init__(self, graph: DirectedGraph):
        self.graph = graph
        self.active_hazards: Dict[Tuple[int, int], HazardRecord] = {}
        self.active_closures: Dict[Tuple[int, int], ClosureRecord] = {}

    def inject_edge_hazard(
        self,
        u: int,
        v: int,
        penalty_beta: float = 45.0,
        label: str = "Hazmat Spill",
        duration_seconds: float = float("inf"),
        bidirectional: bool = True,
    ) -> bool:
        """Applies an additive hazard penalty to edge (u, v)."""
        success = self.graph.inject_hazard(u, v, penalty_beta=penalty_beta, label=label)
        if success:
            self.active_hazards[(u, v)] = HazardRecord(
                u=u, v=v, penalty_beta=penalty_beta, label=label, remaining_duration=duration_seconds
            )
        if bidirectional:
            if self.graph.get_edge(v, u):
                self.inject_edge_hazard(
                    u=v, v=u, penalty_beta=penalty_beta, label=label, duration_seconds=duration_seconds, bidirectional=False
                )
        return success

    def inject_edge_closure(
        self,
        u: int,
        v: int,
        reason: str = "Structural Damage",
        duration_seconds: float = float("inf"),
        bidirectional: bool = True,
    ) -> bool:
        """Removes edge (u, v) from active network E_t (Invariant I1)."""
        success = self.graph.close_edge(u, v, reason=reason)
        if success:
            self.active_closures[(u, v)] = ClosureRecord(
                u=u, v=v, reason=reason, remaining_duration=duration_seconds
            )
        if bidirectional:
            if self.graph.get_edge(v, u):
                self.inject_edge_closure(
                    u=v, v=u, reason=reason, duration_seconds=duration_seconds, bidirectional=False
                )
        return success

    def inject_spatial_hazard(
        self,
        center_x: float,
        center_y: float,
        radius_meters: float,
        penalty_beta: float = 60.0,
        label: str = "Chemical Cloud",
        duration_seconds: float = float("inf"),
    ) -> List[Tuple[int, int]]:
        """Applies hazard to all edges having at least one endpoint within radius."""
        affected_edges = []
        for edge in self.graph.get_all_edges():
            u_node = self.graph.nodes[edge.u]
            v_node = self.graph.nodes[edge.v]
            dist_u = math.hypot(u_node.x - center_x, u_node.y - center_y)
            dist_v = math.hypot(v_node.x - center_x, v_node.y - center_y)
            if dist_u <= radius_meters or dist_v <= radius_meters:
                self.inject_edge_hazard(
                    edge.u, edge.v, penalty_beta=penalty_beta, label=label, duration_seconds=duration_seconds, bidirectional=False
                )
                affected_edges.append((edge.u, edge.v))
        return affected_edges

    def inject_spatial_closure(
        self,
        center_x: float,
        center_y: float,
        radius_meters: float,
        reason: str = "Flooded Zone",
        duration_seconds: float = float("inf"),
    ) -> List[Tuple[int, int]]:
        """Closes all edges inside a geographic hazard perimeter."""
        closed = []
        for edge in self.graph.get_all_edges():
            u_node = self.graph.nodes[edge.u]
            v_node = self.graph.nodes[edge.v]
            dist_u = math.hypot(u_node.x - center_x, u_node.y - center_y)
            dist_v = math.hypot(v_node.x - center_x, v_node.y - center_y)
            if dist_u <= radius_meters and dist_v <= radius_meters:
                self.inject_edge_closure(
                    edge.u, edge.v, reason=reason, duration_seconds=duration_seconds, bidirectional=False
                )
                closed.append((edge.u, edge.v))
        return closed

    def step(self, dt: float = 1.0) -> Dict[str, List[Tuple[int, int]]]:
        """
        Advances timers for hazards and closures.
        Automatically reopens restored edges and removes cleared hazards.
        """
        reopened = []
        cleared_hazards = []

        # Step closures
        for key in list(self.active_closures.keys()):
            rec = self.active_closures[key]
            if rec.remaining_duration != float("inf"):
                rec.remaining_duration -= dt
                if rec.remaining_duration <= 0:
                    self.graph.reopen_edge(rec.u, rec.v)
                    reopened.append(key)
                    del self.active_closures[key]

        # Step hazards
        for key in list(self.active_hazards.keys()):
            rec = self.active_hazards[key]
            if rec.remaining_duration != float("inf"):
                rec.remaining_duration -= dt
                if rec.remaining_duration <= 0:
                    self.graph.remove_hazard(rec.u, rec.v)
                    cleared_hazards.append(key)
                    del self.active_hazards[key]

        return {"reopened_edges": reopened, "cleared_hazards": cleared_hazards}
