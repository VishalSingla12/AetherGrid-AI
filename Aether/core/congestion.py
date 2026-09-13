"""
Aether Congestion Management & EWMA Filter
Implements the vehicle occupancy tracking and Exponentially Weighted Moving Average
congestion smoothing filter to prevent route-flapping and high-frequency chatter.
"""

import math
from typing import Dict, List, Tuple
from .graph import DirectedGraph, EdgeData


class CongestionManager:
    """
    Manages edge-level vehicle occupancies n_e(t) and updates the smoothed
    congestion densities rho_e(t) using an EWMA temporal filter.
    """

    def __init__(self, graph: DirectedGraph, smoothing_time_constant: float = 15.0):
        self.graph = graph
        self.smoothing_time_constant = max(1.0, smoothing_time_constant)  # T_smooth in seconds

    def update_occupancy(self, u: int, v: int, delta: int) -> int:
        """Modifies instantaneous vehicle count on edge (u, v)."""
        edge = self.graph.get_edge(u, v)
        if not edge:
            return 0
        edge.occupancy = max(0, edge.occupancy + delta)
        return edge.occupancy

    def set_occupancy(self, u: int, v: int, count: int) -> None:
        """Sets exact vehicle count on edge (u, v)."""
        edge = self.graph.get_edge(u, v)
        if edge:
            edge.occupancy = max(0, count)

    def step(self, dt: float = 1.0) -> None:
        """
        Advances the EWMA congestion filter for all edges in the network:
        rho_e(t + dt) = (1 - lambda_ewma) * rho_e(t) + lambda_ewma * min(1.0, n_e / K_e)
        where lambda_ewma = 1.0 - exp(-dt / T_smooth).
        """
        # Calculate smoothing weight lambda_ewma
        lambda_ewma = 1.0 - math.exp(-dt / self.smoothing_time_constant)

        for edge in self.graph.get_all_edges():
            instantaneous_density = min(1.0, float(edge.occupancy) / float(edge.capacity))
            # EWMA update equation
            edge.congestion = (1.0 - lambda_ewma) * edge.congestion + lambda_ewma * instantaneous_density
            # Numerical cleanup
            if edge.congestion < 1e-5:
                edge.congestion = 0.0
            elif edge.congestion > 0.9999:
                edge.congestion = 1.0

    def get_network_statistics(self) -> Dict[str, float]:
        """Returns aggregate congestion metrics for telemetry."""
        edges = self.graph.get_all_edges()
        if not edges:
            return {"mean_congestion": 0.0, "max_congestion": 0.0, "total_vehicles": 0}

        densities = [e.congestion for e in edges]
        total_veh = sum(e.occupancy for e in edges)

        return {
            "mean_congestion": sum(densities) / len(densities),
            "max_congestion": max(densities),
            "total_vehicles": total_veh,
        }

    def get_congested_edges(self, threshold: float = 0.50) -> List[Tuple[int, int, float]]:
        """Returns list of (u, v, rho) for edges exceeding the congestion threshold."""
        congested = []
        for edge in self.graph.get_all_edges():
            if edge.congestion >= threshold:
                congested.append((edge.u, edge.v, edge.congestion))
        return sorted(congested, key=lambda x: x[2], reverse=True)
