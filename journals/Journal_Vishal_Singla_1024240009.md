# Project Journal

**Name:** Vishal Singla
**Roll No.:** 1024240009
**Course:** UCS503P – Software Engineering
**Project:** AetherGrid AI – An Autonomous Logistics and Emergency-Dispatch Simulation
**Presented to:** Dr. Zeelani
**Institute:** Thapar Institute of Engineering and Technology

---

## Log Entry 07 — Data-Flow Compliant Reactive Recalculation, Weather-Corridor Shifts (93.7% Divergence), Weighted A\* Algorithmic Disparity (88.8% Divergence), and Pixel-Accurate Road Disruption Suite

- **Date & Timestamp:** 2026-09-13T20:30:00+05:30
- **Target Directory:** `Aether/core/`, `Aether/web/`, `Aether/tests/`
- **Scope:** Comprehensive architectural resolution of user feedback concerning road closure/hazmat injection interaction, lack of weather-induced path changes, identical algorithmic paths, and reactive recomputation per Data Flow Diagram (DFD) specifications.

### Root Cause Analysis & Engineering Remediation

1. **Interactive Road Closures & Hazmat Spills (Fixed: Screen-Space Pixel Snapping + 1-Click Injection)**:
   - _Root Cause:_ Leaflet's `L.canvas()` has a default click tolerance of 0 pixels. At zoom level 13 on the wide Manhattan map, a 60-meter threshold translated to only ~3 screen pixels, causing user clicks to miss the microscopic hit target.
   - _Remediation:_
     - Configured `canvasRenderer = L.canvas({ padding: 0.5, tolerance: 15 })` and bound direct click handlers to all edge polylines with event propagation stops.
     - Implemented screen-space pixel projection `map.latLngToContainerPoint()` with a generous 35-pixel hit target (`findNearestEdge(latlng, maxPixels=35)`), enabling effortless road selection at any zoom level.
     - Added visual glowing red closure barriers (`🚧 ROAD CLOSED`) and amber biohazard icons (`☣️ HAZMAT SPILL`) placed at the exact midpoint of affected corridors.
     - Added dedicated 1-click disruption buttons ("🚧 Block Active Route" and "☣️ Hazmat On Route") in the floating palette that instantly target the active route midpoint for immediate demonstration of Invariant I1 compliance.

2. **Weather-Induced Route Corridor Shifts (Fixed: 93.7% Path Divergence)**:
   - _Root Cause:_ Applying a uniform scalar $\omega(t)$ across all edges scaled costs proportionally without altering the optimal corridor topology (since Columbus Ave and Central Park West are both arterial class).
   - _Remediation:_
     - Formulated `_weather_corridor_factor(edge, weather_multiplier)` in `Aether/core/pricing.py`. Modeled real-world urban emergency management dynamics:
       - **Snow / Blizzard ($\omega \ge 1.60$)**: Designated **NYC Priority Snow Emergency Routes** (Central Park West, Broadway, 5th Ave, 57th St) are continuously salted and plowed ($\omega_{\text{eff}} = 1.10\times$), while secondary avenues (Columbus Ave) accumulate heavy slush and ice ($\omega_{\text{eff}} = 2.15\times$), and exposed bridges/highways freeze over ($\omega_{\text{eff}} = 2.50\times$).
       - **Rain / Flood ($\omega \in (1.15, 1.35)$)**: Low-lying avenues (Columbus Ave, river roads) experience flash ponding ($\omega_{\text{eff}} = 1.85\times$), routing traffic toward high-ridge well-drained avenues.
     - _Empirical Verification:_ Clear weather route uses Columbus Avenue (166 segments, $314.9\,\text{s}$). Snow weather immediately shifts the entire corridor to Central Park West (148 segments, $450.0\,\text{s}$), achieving **$93.7\%$ path divergence**!

3. **Algorithmic Path Diversity (Fixed: Weighted A\* with 88.8% Divergence & 5.5x Speedup)**:
   - _Root Cause:_ With an admissible heuristic and deterministic costs, Dijkstra, Dynamic A*, and Bidirectional A* all mathematically converge to the single optimal shortest path.
   - _Remediation:_
     - Implemented `find_shortest_path_weighted(..., epsilon=2.5)` in `Aether/core/traversal.py`. Uses an inflated heuristic $f(n) = g(n) + \epsilon \cdot h(n)$ that aggressively favors direct "as-the-crow-flies" shortcuts.
     - The 3-way shootout now displays genuine path and strategy differentiation:
       - 🟠 **Dijkstra**: Uninformed exhaustive search ($3,701$ nodes expanded, $26.04\,\text{ms}$, optimal cost $314.9\,\text{s}$, speedup $1.0\times$).
       - 🔵 **Weighted A\* ($\epsilon=2.5$)**: Greedy directional heuristic ($584$ nodes expanded, $4.75\,\text{ms}$, cost $343.1\,\text{s}$, speedup **$5.5\times$**, **$88.8\%$ path divergence**).
       - 🟢 **Bidirectional A\***: Wavefront meeting search ($1,508$ nodes expanded, $9.90\,\text{ms}$, optimal cost $314.9\,\text{s}$, speedup **$2.6\times$**).
     - Added live "Path Divergence: 88.8%" telemetry badge and clickable rows to inspect each algorithm's distinct path.

4. **DFD-Compliant Reactive Recomputation Pipeline**:
   - _Implementation:_ Synchronized the data flow cascade across processes $P_1 \to P_2 \to P_3$:
     - Environmental mutations (`POST /api/weather`, `POST /api/traffic_surge`, `POST /api/closure`, `POST /api/hazard`, `POST /api/reset`) immediately trigger edge recoloring via `refreshEdgesStatus()` and re-execute `recalculateAndShootout()`.
     - Traffic surge targets realistic bottleneck corridors with severe saturation ($\rho = 0.92$), causing routes to immediately divert around Columbus Avenue to parallel corridors (**$93.7\%$ surge divergence**).

5. **Automated Verification**:
   - Full test suite execution (`python3 -m unittest discover Aether/tests`): **11/11 tests passing** ($100\%$ pass rate) with exact analytical cost matching.

---

## Log Entry 08 — Operational HazMat Incident Command Protocol & Dynamic PPE Gear Directive Engine

- **Date & Timestamp:** 2026-09-13T20:50:00+05:30
- **Target Directory:** `Aether/web/`, `Aether/web/static/`
- **Scope:** Architectural implementation of real-world HazMat incident command notifications. Preserves pure mathematical cost routing while actively alerting mission control to equip responding crews with appropriate PPE gear based on contamination severity.

### Architecture & Protocol Implementation

1. **Mathematical Tenet Preservation**:
   - Maintained the baseline risk penalty formulation ($c(e, t) = \text{base} + \beta$) without artificial penalty inflation, ensuring optimal time-to-incident dispatch decisions are not distorted when long detours threaten life safety.

2. **Multi-Tier Severity & PPE Gear Classification (`SimulationStateManager._evaluate_hazmat_exposure`)**:
   - Evaluates all traversed edges along candidate routes across all search algorithms:
     - **Level 0 (Clear, 0 spills)**: Standard EMT Uniform. Normal operating procedure.
     - **Level 1 (Low Exposure, 1 spill)**: Level C PPE (N95/P100 Particulate Respirator + Splash Suit). Directive: Don respirators, switch ambulance HVAC to internal air recirculation.
     - **Level 2 (Elevated Toxicity, 2–3 spills)**: Level B PPE (SCBA Self-Contained Breathing Apparatus + Chemical Suit). Directive: Mandatory SCBA donning, seal cabin intakes, notify receiving hospital decontamination unit.
     - **Level 3 (Critical Biohazard Hot Zone, 4+ spills)**: Level A PPE (Vapor-Tight Fully Encapsulated Suit + SCBA). Directive: Mandatory full encapsulation, request HazMat decontamination escort vehicle.

3. **Mission Control Center Visual Alerts & Real-Time Telemetry**:
   - Added a glowing alert banner (`#hazmat-alert-banner`) in the HUD displaying:
     - Protocol severity badge with dynamic color-coding (Amber $\to$ Orange $\to$ Crimson).
     - Active contaminated segment count and affected street names.
     - Crew operational directive and mandatory PPE equipment tag.
   - Dispatch button dynamically adapts: `🚑 Dispatch (☣️ SCBA Equipped)` or `🚑 Dispatch (☣️ Level A Equipped)`.
   - Mission operations feed logs timestamped alert directives for operational accountability.

---

## Log Entry 09 — Corridor/Block Closure Propagation (Intersection-to-Intersection) & Strict Invariant I1 Detour Enforcement

- **Date & Timestamp:** 2026-09-13T22:05:00+05:30
- **Target Directory:** `Aether/core/`, `Aether/web/`, `Aether/tests/`
- **Scope:** Root cause diagnosis and architectural remediation of road closure visualization, OSM micro-segmentation leaks, and severed network handling.

### Root Cause Analysis & Resolution Architecture

1. **OSM Micro-Segmentation vs. Single Micro-Edge Click**:
   - _Phenomenon Diagnosed:_ In OpenStreetMap networks, physical street blocks between intersections are decomposed into 6–15 microscopic directed edges (between pedestrian crosswalks, traffic signals, and geometric curvature nodes).
   - _Previous Failure Mode:_ Clicking a road closed only ONE 10-meter directed sub-segment (`15794 -> 15333`). Adjacent sub-segments (`15333 -> 1040`, `15334 -> 18805`) remained open, allowing the router to enter or bypass the closed sub-segment or creating visual overlaps where the green route polyline masked the road line.
   - _Remediation (`SimulationStateManager.get_corridor_block`)_:
     - Implemented bidirectional BFS block expansion: starting from the clicked edge `(u, v)`, traversal propagates forward and backward along edges sharing the same street name until reaching major cross-street intersections (where $\ge 2$ distinct street names intersect or degree $> 2$) or reaching block distance limits ($\le 250\,\text{m}$).
     - `STATE.toggle_closure(u, v)` now closes the **entire contiguous street block** (both directions if bidirectional) and returns `affected_edges` list (typically 6–14 micro-segments per block).
     - Visual result: the entire street block turns bold red on the map with a single centered barrier marker, completely sealing the block against any traversal.

2. **Network Severing & Frontend Stale State Display (`success: false`)**:
   - _Phenomenon Diagnosed:_ When multiple corridors (e.g. Central Park West AND Columbus Avenue) were simultaneously walled off, all valid paths between Origin and Destination were severed.
   - _Previous Failure Mode:_ All 3 pathfinding algorithms mathematically returned `success: false` (strictly upholding Invariant I1: 0 closed edges traversed). However, the frontend did not display a severed status banner; it left stale telemetry numbers (69.92 ms, 6,270 nodes, 723.6 s) and stale HazMat alerts visible in the sidebar, giving the illusion that the previous route through the closed street was still being chosen.
   - _Remediation_:
     - Created `#route-severed-banner` in HUD with pulsing red glow:
       `"🚫 DESTINATION UNREACHABLE — ALL ROUTES SEVERED | Invariant I1 Upheld: Zero closed roads traversed."`
     - Telemetry HUD updates: Latency `N/A`, Expanded `--`, Pruned `0.0%`, Travel Cost `SEVERED (∞)`.
     - Shootout comparison table updates all rows to `UNREACHABLE`.
     - HazMat alert banner is cleanly hidden (since no route is traversing it).
     - Dispatch button switches to `🚫 Path Severed` (disabled).

3. **Data Integrity & Street Name Preservation (`EdgeData.street_name`)**:
   - _Bug Identified:_ Previously, `DirectedGraph.close_edge` overwrote `edge.closure_reason` with the closure message (e.g., `"Structural Closure"`), destroying the original street name and preventing weather corridors (Snow Emergency Routes, Flood Basins) and HazMat notifications from identifying the street name after reopen.
   - _Resolution:_ Added dedicated `street_name: str` field on `EdgeData`, populated during OSM ingestion and preserved immutably through all closure and reopening lifecycles.

4. **Automated Verification**:
   - Added `Aether/tests/test_corridor_closure.py`:
     - `test_corridor_block_expansion`: Verifies all micro-segments of a named street block are captured.
     - `test_corridor_closure_detour_invariant_i1`: Verifies that when a corridor is closed, pathfinding immediately detours around it with **strictly 0 closed edge traversals** ($0 / 4$ algorithms).
     - `test_corridor_reopen_and_street_name_preservation`: Verifies 100% edge restoration and street name preservation.
     - `test_severed_network_unreachable`: Verifies clean failure reporting (`success=False`, `cost=inf`) when all corridors are cut off.
   - Test suite execution: **15/15 tests passing** ($100\%$ green).

---

## Log Entry 10 — HazMat Incident Site Clustering & Microscopic Segment Aggregation

- **Date & Timestamp:** 2026-09-13T22:31:00+05:30
- **Target Directory:** `Aether/web/`, `Aether/web/static/`, `Aether/tests/`
- **Scope:** Root cause diagnosis and architectural remediation of HazMat spill site over-counting and false Level 3 escalation.

### Root Cause Analysis

1. **The Phenomenon**:
   - The user injected 1 single HazMat spill on Park Avenue South.
   - The mission control UI escalated the incident to:
     `☣️ LEVEL 3 (CRITICAL BIOHAZARD HOT ZONE) [9 SPILL(S) ON ACTIVE ROUTE]`
     `CRITICAL CONTAMINATION (9 segments). Level A full encapsulation required... (Affects: Park Avenue South)`
2. **The Mechanism**:
   - In Log Entry 09, `inject_hazard(u, v)` was upgraded to call `get_corridor_block(u, v)` to prevent micro-segment bypass leakage. This marked all 9 microscopic OSM segments (~7–10 meters each) along Park Avenue South as hazardous (23 edges total counting reverse).
   - In `_evaluate_hazmat_exposure`, the severity evaluation previously computed:
     ```python
     count = len(hazmat_edges)  # Evaluated to 9!
     if count >= 4:
         severity = "LEVEL 3 (CRITICAL BIOHAZARD HOT ZONE)"
     ```
   - It treated each microscopic 7-meter OSM edge as a separate independent spill site across the city, resulting in $9 \ge 4$ triggering Level 3 biohazard hot zone status requiring Level A spacesuits for what was physically only 68 meters of road on a single street block.

### Architectural Remediation

1. **Contiguous Incident Clustering & Micro-Gap Bridging**:
   - Implemented cluster-aware corridor traversal analysis in `_evaluate_hazmat_exposure`:
     - Consecutive hazardous edges traversed along the active route are grouped into contiguous incident clusters.
     - Micro-gaps (e.g., a single 5–15 meter non-hazardous intersection connector or crosswalk node) between adjacent hazardous segments of the same corridor are bridged so that 1 physical spill is not split into multiple sites.
     - Reports both `incident_sites_count` (distinct physical spill locations) and `segments_count` (total microscopic OSM segments contaminated), along with `total_meters` (physical corridor distance contaminated).
2. **Operational HazMat PPE Severity Calibration**:
   - **LEVEL 1 (LOW EXPOSURE, Code 1)**:
     - Conditions: 1 distinct incident site ($\le 450\,\text{m}$ and $\le 20$ micro-segments).
     - PPE: Level C PPE (N95/P100 Respirator + Splash Suit).
     - Directive: _"Single incident corridor ({segments} segments, {meters}m). Don Level C respirators and switch ambulance HVAC to internal recirculation."_
   - **LEVEL 2 (ELEVATED TOXICITY, Code 2)**:
     - Conditions: 2–3 distinct incident sites OR extended corridor ($> 450\,\text{m}$).
     - PPE: Level B PPE (SCBA Self-Contained Breathing Apparatus + Chemical Suit).
     - Directive: _"Elevated contamination ({sites} incident sites, {segments} segments, {meters}m). Mandatory SCBA donning. Seal cabin and notify receiving ER decontamination."_
   - **LEVEL 3 (CRITICAL BIOHAZARD HOT ZONE, Code 3)**:
     - Conditions: 4+ distinct incident sites OR severe systemic multi-kilometer contamination ($> 1000\,\text{m}$).
     - PPE: Level A PPE (Vapor-Tight Encapsulated Suit + SCBA).
     - Directive: _"CRITICAL CONTAMINATION ({sites} incident sites, {segments} segments, {meters}m). Level A full encapsulation required. Request HazMat decontamination escort."_
3. **Frontend UI Badge & Telemetry Update**:
   - Updated `#hazmat-count-badge` in `Aether/web/static/index.html`:
     - Displays `[1 INCIDENT SITE (9 SEGMENTS)]` instead of `[9 SPILL(S) ON ACTIVE ROUTE]`.
     - Alert title rendered in amber `#fbbf24` (Level 1) instead of critical red `#ef4444`.
     - Dispatch button displays `🚑 Dispatch (☣️ PPE Equipped)` for Level 1, `🚑 Dispatch (☣️ SCBA Equipped)` for Level 2, and `🚑 Dispatch (☣️ Level A Equipped)` for Level 3.
4. **Verification & Test Coverage**:
   - Added `TestHazMatExposureEvaluation` to `Aether/tests/test_corridor_closure.py`:
     - `test_single_block_multisegment_spill_classified_as_level_1`: Verifies that a 9-micro-segment block on Park Avenue South evaluates to 1 Incident Site, Level 1 Low Exposure, Level C PPE.
     - `test_multi_site_spill_classified_as_level_2`: Verifies 2 separate spill sites evaluate to 2 Incident Sites, Level 2 Elevated Toxicity, Level B SCBA.
     - `test_four_distinct_sites_classified_as_level_3`: Verifies 4 separate sites across town escalate to Level 3 Critical Hot Zone, Level A PPE.
   - Test suite execution: **18/18 tests passing** ($100\%$ green).
   - Live server verification: Live injection on Park Avenue South confirmed returning `incident_sites_count: 1`, `segments_count: 14`, `severity_level: "LEVEL 1 (LOW EXPOSURE)"`, `severity_code: 1`, `ppe_gear: "Level C PPE: N95/P100 Respirator + Splash Suit"`.
