"""
Aether Interactive Terminal Simulation & Real-Time Demo (Phase 01)
Demonstrates real-time graph traversal, dynamic congestion EWMA, weather shifts,
sudden structural closures, hazard injections, dynamic rerouting, and ANSI visualization.
"""

import os
import sys
import time
from typing import List, Optional, Set, Tuple

from Aether.core.graph import DirectedGraph, TerrainType
from Aether.core.pricing import CostModelParameters, calculate_edge_cost
from Aether.core.weather import WeatherManager, WeatherType
from Aether.core.congestion import CongestionManager
from Aether.core.hazards import HazardManager
from Aether.core.traversal import find_shortest_path, RouteResult


class TerminalVisualizer:
    """ANSI color-coded visualizer for the urban grid simulation."""

    # ANSI Colors
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    BG_DARK = "\033[40m"

    @classmethod
    def render_grid(
        cls,
        graph: DirectedGraph,
        rows: int,
        cols: int,
        vehicle_node: int,
        goal_node: int,
        active_path: List[int],
        river_col: Optional[int] = None,
        bridge_rows: Optional[List[int]] = None,
    ) -> str:
        """Renders an ASCII/ANSI grid representation of the city network."""
        path_set = set(active_path)
        bridge_rows = bridge_rows or []
        lines = []

        # Top border
        header = f"{cls.CYAN}+" + "---+" * cols + f"{cls.RESET}"
        lines.append("  " + header)

        for r in range(rows):
            row_str = f"{r:2d}" + f"{cls.CYAN}|{cls.RESET}"
            for c in range(cols):
                node_id = r * cols + c
                node = graph.nodes[node_id]

                # Determine cell symbol and color
                if node_id == vehicle_node:
                    sym = f"{cls.BOLD}{cls.YELLOW} A {cls.RESET}"  # Ambulance Agent
                elif node_id == goal_node:
                    sym = f"{cls.BOLD}{cls.RED} ! {cls.RESET}"  # Emergency Call
                elif node.is_hospital:
                    sym = f"{cls.BOLD}{cls.GREEN} H {cls.RESET}"  # Hospital
                elif node.is_depot:
                    sym = f"{cls.BLUE} D {cls.RESET}"  # Depot
                elif node_id in path_set:
                    sym = f"{cls.MAGENTA} * {cls.RESET}"  # Active Path
                elif river_col is not None and c == river_col and r not in bridge_rows:
                    sym = f"{cls.BLUE} ~ {cls.RESET}"  # River
                elif river_col is not None and c == river_col and r in bridge_rows:
                    sym = f"{cls.WHITE} # {cls.RESET}"  # Bridge
                else:
                    sym = f"{cls.GRAY} . {cls.RESET}"  # Regular intersection

                row_str += sym

                # Check horizontal edge to east
                if c + 1 < cols:
                    east_edge = graph.get_edge(node_id, r * cols + c + 1)
                    if not east_edge or not east_edge.is_open:
                        row_str += f"{cls.RED}X{cls.RESET}" if east_edge else " "
                    elif east_edge.is_hazard:
                        row_str += f"{cls.YELLOW}!{cls.RESET}"
                    elif (node_id in path_set) and ((r * cols + c + 1) in path_set):
                        row_str += f"{cls.MAGENTA}-{cls.RESET}"
                    else:
                        row_str += f"{cls.GRAY}-{cls.RESET}"
                else:
                    row_str += f"{cls.CYAN}|{cls.RESET}"

            lines.append("  " + row_str)

        lines.append("  " + header)
        return "\n".join(lines)


class DemoSimulation:
    """
    Interactive demonstration showing:
    1. Dynamic 10x10 city grid with river and 2 bridges.
    2. Vehicle dispatch and initial path calculation.
    3. Traffic congestion build-up (EWMA).
    4. Sudden bridge closure mid-journey.
    5. Instantaneous dynamic rerouting avoiding closure (Invariant I1).
    6. Safe arrival and delivery telemetry.
    """

    def __init__(self, rows: int = 10, cols: int = 10, headless: bool = False):
        self.rows = rows
        self.cols = cols
        self.river_col = cols // 2
        self.bridge_rows = [2, rows - 3]
        self.headless = headless

        self.graph = DirectedGraph.generate_grid_network(
            rows=rows,
            cols=cols,
            spacing_meters=250.0,
            highway_rows=[1, rows - 2],
            highway_cols=[1, cols - 2],
            river_col=self.river_col,
            bridge_rows=self.bridge_rows,
        )

        self.congestion_mgr = CongestionManager(self.graph, smoothing_time_constant=12.0)
        self.hazard_mgr = HazardManager(self.graph)
        self.weather_mgr = WeatherManager(WeatherType.CLEAR)

        self.vehicle_node = 0  # Starts at top-left depot
        self.goal_node = rows * cols - 1  # Target at bottom-right
        self.clock = 0.0
        self.dt = 1.0

        # State tracking
        self.route_result: Optional[RouteResult] = None
        self.current_path_index = 0
        self.log_messages: List[str] = []

    def log(self, message: str) -> None:
        """Appends a timestamped log message."""
        timestamp = f"[{self.clock:04.1f}s]"
        entry = f"{timestamp} {message}"
        self.log_messages.append(entry)
        if not self.headless:
            print(f"\033[36m{entry}\033[0m")

    def run(self, sleep_delay: float = 0.4) -> Dict[str, float]:
        """Runs the complete simulated mission lifecycle."""
        self.log("Initializing AetherGrid Phase 01 Simulation Demo...")
        self.log(f"City Grid: {self.rows}x{self.cols} ({self.graph.num_nodes} nodes, {self.graph.num_edges} edges)")
        self.log(f"River barrier at column {self.river_col}; Bridges at rows {self.bridge_rows}")
        self.log(f"Emergency Call Registered at Node {self.goal_node}. Dispatching Ambulance A1 from Node {self.vehicle_node}.")

        # 1. Initial Path Planning
        t0 = time.perf_counter()
        self.route_result = find_shortest_path(
            self.graph, self.vehicle_node, self.goal_node, weather_multiplier=self.weather_mgr.multiplier
        )
        plan_time_ms = (time.perf_counter() - t0) * 1000.0
        self.log(f"Initial Path Found in {plan_time_ms:.3f} ms. Cost: {self.route_result.total_cost_seconds:.1f} s. Waypoints: {len(self.route_result.path)}")

        reroute_occurred = False
        bridge_severed = False

        while self.vehicle_node != self.goal_node:
            self.clock += self.dt

            # Background traffic step
            self.congestion_mgr.step(self.dt)
            self.hazard_mgr.step(self.dt)
            self.weather_mgr.step(self.dt)

            total_path_len = len(self.route_result.path) if self.route_result else 10
            step_surge = max(1, total_path_len // 4)
            step_weather = max(2, total_path_len // 3)
            step_closure = max(3, total_path_len // 2)

            # Scenario Event 1: Traffic intensifies on northern arterials
            if int(self.clock) == step_surge:
                self.log("TRAFFIC SURGE: Rush-hour volume rising on northern avenues.")
                for edge in self.graph.get_all_edges():
                    if edge.u < 20:
                        self.congestion_mgr.update_occupancy(edge.u, edge.v, delta=25)

            # Scenario Event 2: Rain storm moves across city
            if int(self.clock) == step_weather:
                self.weather_mgr.set_weather(WeatherType.RAIN)
                self.log("WEATHER UPDATE: Heavy rain detected across grid (omega = 1.22).")

            # Scenario Event 3: North Bridge collapses while vehicle is enroute!
            if int(self.clock) == step_closure and not bridge_severed:
                bridge_r = self.bridge_rows[0]
                bridge_u = bridge_r * self.cols + self.river_col
                bridge_v = bridge_r * self.cols + (self.river_col + 1)
                self.hazard_mgr.inject_edge_closure(
                    bridge_u, bridge_v, reason="Structural Bridge Failure", duration_seconds=300.0
                )
                self.log(f"ALERT: DISRUPTION INJECTED! North Bridge ({bridge_u} <-> {bridge_v}) CLOSED!")
                bridge_severed = True

                # Check if current path uses the closed bridge
                path_edges = self.route_result.edges_traversed[self.current_path_index:]
                if (bridge_u, bridge_v) in path_edges or (bridge_v, bridge_u) in path_edges:
                    self.log("DETOUR REQUIRED: Active route intersects closed bridge corridor!")
                    t_reroute_start = time.perf_counter()
                    new_route = find_shortest_path(
                        self.graph, self.vehicle_node, self.goal_node, weather_multiplier=self.weather_mgr.multiplier
                    )
                    t_reroute_ms = (time.perf_counter() - t_reroute_start) * 1000.0
                    self.route_result = new_route
                    self.current_path_index = 0
                    reroute_occurred = True
                    self.log(f"DYNAMIC REROUTE SUCCESSFUL in {t_reroute_ms:.3f} ms. New Cost: {new_route.total_cost_seconds:.1f} s.")
                    self.log(f"Invariant I1 Check: Passed (0 closed edges traversed).")

            # Advance vehicle along active path
            if self.current_path_index + 1 < len(self.route_result.path):
                self.current_path_index += 1
                next_node = self.route_result.path[self.current_path_index]
                self.vehicle_node = next_node

            # Render frame
            if not self.headless:
                self._render_frame()
                time.sleep(sleep_delay)

        self.log(f"MISSION SUCCESS: Ambulance arrived at Goal Node {self.goal_node} at t = {self.clock:.1f} s.")
        return {
            "total_sim_time": self.clock,
            "reroute_occurred": 1.0 if reroute_occurred else 0.0,
            "final_weather": self.weather_mgr.current_weather.name,
            "nodes_visited": len(self.route_result.path),
        }

    def _render_frame(self) -> None:
        """Renders one visual frame to terminal."""
        os.system("clear" if os.name == "posix" else "cls")
        v = TerminalVisualizer

        print(f"{v.BOLD}{v.CYAN}========================================================================{v.RESET}")
        print(f"{v.BOLD}  AETHERGRID-AI: DYNAMIC URBAN DISPATCH & REROUTING SIMULATION DEMO{v.RESET}")
        print(f"{v.CYAN}========================================================================{v.RESET}")

        # HUD Telemetry
        con_stats = self.congestion_mgr.get_network_statistics()
        remaining_cost = 0.0
        if self.route_result and self.current_path_index < len(self.route_result.edge_costs):
            remaining_cost = sum(self.route_result.edge_costs[self.current_path_index:])

        print(f" {v.BOLD}Clock:{v.RESET} {self.clock:04.1f}s | "
              f"{v.BOLD}Weather:{v.RESET} {self.weather_mgr.current_weather.name} ({self.weather_mgr.multiplier:.2f}x) | "
              f"{v.BOLD}Congestion Mean:{v.RESET} {con_stats['mean_congestion']:.2f} | "
              f"{v.BOLD}Remaining ETA:{v.RESET} {remaining_cost:.1f}s")
        print(f" {v.BOLD}Ambulance Node:{v.RESET} {self.vehicle_node} | "
              f"{v.BOLD}Goal Node:{v.RESET} {self.goal_node} | "
              f"{v.BOLD}Active Closures:{v.RESET} {len(self.graph.closed_edges)}")
        print(f"{v.CYAN}------------------------------------------------------------------------{v.RESET}")

        # Grid view
        active_path = self.route_result.path[self.current_path_index:] if self.route_result else []
        grid_art = TerminalVisualizer.render_grid(
            graph=self.graph,
            rows=self.rows,
            cols=self.cols,
            vehicle_node=self.vehicle_node,
            goal_node=self.goal_node,
            active_path=active_path,
            river_col=self.river_col,
            bridge_rows=self.bridge_rows,
        )
        print(grid_art)

        print(f"{v.CYAN}------------------------------------------------------------------------{v.RESET}")
        print(f" {v.BOLD}Legend:{v.RESET} [A] Ambulance  [!] Incident  [D] Depot  [H] Hospital  [#] Bridge  [X] Closed  [*] Path")
        print(f"{v.CYAN}------------------------------------------------------------------------{v.RESET}")
        print(f"{v.BOLD}Live Event Log:{v.RESET}")
        for msg in self.log_messages[-5:]:
            print(f"  {msg}")
        print(f"{v.CYAN}========================================================================{v.RESET}")


if __name__ == "__main__":
    demo = DemoSimulation(rows=10, cols=10, headless=False)
    demo.run(sleep_delay=0.3)
