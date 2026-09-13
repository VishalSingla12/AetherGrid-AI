"""
Aether Cost Pricing Engine
Implements the dynamic edge cost model c(e, t) and admissible lower-bound heuristics.
"""

from dataclasses import dataclass
import math
from typing import Optional
from .graph import EdgeData, NodeData


@dataclass(frozen=True)
class CostModelParameters:
    """
    Standard calibrated cost parameters for AetherGrid AI.
    All temporal values in seconds.
    """
    alpha: float = 0.85            # Congestion sensitivity factor
    default_beta: float = 45.0     # Hazard time penalty (seconds)
    siren_multiplier: float = 0.35 # Congestion attenuation under siren mode
    min_cost_epsilon: float = 1e-4 # Minimum positive cost bound to prevent zero-weight cycles


# Designated NYC / Urban Priority Emergency Routes (salted, plowed continuously during winter storms)
_SNOW_PRIORITY_CORRIDORS = (
    "central park west", "broadway", "5th avenue", "fifth avenue",
    "8th avenue", "eighth avenue", "park avenue", "madison avenue",
    "west 57th street", "west 96th street", "125th street", "canal street"
)

# Flood-prone low-lying corridors (poor drainage, water ponding during heavy rain)
_RAIN_FLOOD_CORRIDORS = (
    "columbus avenue", "11th avenue", "12th avenue", "fdr drive",
    "west street", "water street", "south street", "west street"
)


def _weather_corridor_factor(edge: 'EdgeData', weather_multiplier: float) -> float:
    """
    Computes the corridor-specific weather impedance factor omega_eff(edge, weather).
    
    In real urban transportation networks:
    - SNOW / BLIZZARD: Emergency Management prioritizes plowing and salting on designated
      primary transit spines (e.g. Central Park West, Broadway, 5th Ave), keeping them
      relatively clear (~1.10x impedance). Secondary avenues (Columbus Ave) and exposed
      highways (FDR, West Side) accumulate heavy snow drifts and ice sheets (2.1x - 2.5x).
    - RAIN / HEAVY STORM: Low-lying avenues and riverfront roads suffer flash ponding and
      drainage overflow (1.8x), whereas high-ridge avenues drain cleanly (1.10x).
    - FOG: High-speed highways experience severe visibility reductions and speed limits (1.8x),
      while signalized urban streets remain steady (1.15x).
    
    This produces genuine corridor shifts on both real-world OSM maps and synthetic grids.
    """
    from .graph import TerrainType
    
    omega_base = max(1.0, weather_multiplier)
    if omega_base <= 1.01:
        return 1.0  # Clear weather: baseline
        
    st_name = (getattr(edge, "street_name", None) or edge.closure_reason or "").lower()
    
    # 1. Snow / Blizzard condition (omega_base >= 1.60)
    if omega_base >= 1.60:
        if any(p in st_name for p in _SNOW_PRIORITY_CORRIDORS):
            return 1.10  # Priority snow routes stay salted & plowed
        elif edge.terrain == TerrainType.HIGHWAY:
            return 2.50  # Highways & bridges freeze severely
        elif st_name:
            return 2.15  # Unplowed secondary avenues accumulate slush
        else:
            return omega_base  # Default analytical baseline
            
    # 2. Rain / Heavy Storm condition (1.15 < omega_base < 1.35)
    elif 1.15 < omega_base < 1.35:
        if any(p in st_name for p in _RAIN_FLOOD_CORRIDORS):
            return 1.85  # Low-lying flood zone
        elif edge.terrain in (TerrainType.ALLEY, TerrainType.OFFROAD):
            return 1.90  # Mud / pooling
        elif edge.terrain == TerrainType.HIGHWAY:
            return 1.15  # Grade-separated highways drain well
        else:
            return omega_base  # Default analytical baseline (e.g. 1.22)
            
    # 3. Dense Fog condition (1.35 <= omega_base < 1.60)
    else:
        if edge.terrain == TerrainType.HIGHWAY:
            return 1.85  # Speed hazard on fast roads
        else:
            return omega_base
            
    return omega_base


def calculate_edge_cost(
    edge: 'EdgeData',
    weather_multiplier: float = 1.0,
    params: Optional[CostModelParameters] = None,
    is_siren: bool = False,
) -> float:
    """
    Computes the instantaneous temporal cost c(e, t) in seconds:
    c(e, t) = ell_e * tau_e * (1 + alpha_eff * rho_e(t)) * omega_eff(terrain, weather) + beta * 1[hazard]
    if edge is open; returns float('inf') if closed.
    
    Weather-terrain interaction: omega_eff varies by terrain type so that different
    weather conditions produce genuinely different optimal routes (not just scaled costs).
    """
    if not edge.is_open:
        return float("inf")

    p = params or CostModelParameters()

    # Free flow traversal time ell_e (seconds)
    ell_e = max(p.min_cost_epsilon, edge.free_flow_time_seconds)

    # Terrain multiplier tau_e >= 1.0
    tau_e = edge.terrain.multiplier

    # Congestion density rho_e in [0.0, 1.0]
    rho_e = max(0.0, min(1.0, edge.congestion))

    # Effective alpha under standard vs siren mode
    alpha_eff = p.alpha * (p.siren_multiplier if is_siren else 1.0)

    # Weather-corridor interaction factor
    omega_eff = _weather_corridor_factor(edge, weather_multiplier)

    # Base dynamic traversal time
    dynamic_travel_time = ell_e * tau_e * (1.0 + alpha_eff * rho_e) * omega_eff

    # Additive hazard penalty
    hazard_cost = 0.0
    if edge.is_hazard:
        hazard_cost = max(0.0, edge.hazard_penalty_seconds or p.default_beta)

    total_cost = dynamic_travel_time + hazard_cost
    return max(p.min_cost_epsilon, total_cost)


def compute_admissible_heuristic(
    node_u: NodeData,
    node_goal: NodeData,
    max_network_speed_mps: float,
) -> float:
    """
    Computes the admissible, monotonic Euclidean lower bound heuristic:
    h(u, goal) = EuclideanDistance(u, goal) / max_network_speed

    Mathematical Guarantee:
    Since tau_e >= 1.0, (1 + alpha * rho) >= 1.0, omega >= 1.0, and beta >= 0,
    the actual dynamic cost along any edge is strictly greater than or equal
    to distance / max_speed. Thus h(u, goal) <= c*(u, goal) always holds.
    """
    dist = node_u.distance_to(node_goal)
    safe_speed = max(1.0, max_network_speed_mps)
    return dist / safe_speed
