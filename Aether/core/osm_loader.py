"""
Aether Real-World OpenStreetMap (OSM) Ingestion Engine
Parses real-world OSM road networks, transforms geographic coordinates (lat, lon)
to metric Cartesian coordinates (x, y), maps highway tags to TerrainType, and builds
production-grade DirectedGraph models from real urban topologies.
"""

from collections import deque
import math
import os
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set, Tuple

from .graph import DirectedGraph, NodeData, TerrainType


# Earth radius in meters for Equirectangular projection
EARTH_RADIUS_METERS = 6371000.0

# Road classifications admitted for vehicular emergency and logistics dispatch
VEHICULAR_HIGHWAYS = {
    "motorway": (TerrainType.HIGHWAY, 28.0, 150),
    "motorway_link": (TerrainType.HIGHWAY, 22.0, 100),
    "trunk": (TerrainType.HIGHWAY, 25.0, 120),
    "trunk_link": (TerrainType.HIGHWAY, 20.0, 90),
    "primary": (TerrainType.ARTERIAL, 18.0, 80),
    "primary_link": (TerrainType.ARTERIAL, 15.0, 60),
    "secondary": (TerrainType.ARTERIAL, 16.0, 70),
    "secondary_link": (TerrainType.ARTERIAL, 13.0, 50),
    "tertiary": (TerrainType.URBAN, 14.0, 50),
    "tertiary_link": (TerrainType.URBAN, 12.0, 40),
    "residential": (TerrainType.URBAN, 11.0, 35),
    "unclassified": (TerrainType.URBAN, 11.0, 35),
    "living_street": (TerrainType.ALLEY, 8.0, 20),
    "service": (TerrainType.ALLEY, 7.0, 15),
}

# Pre-configured City Bounding Boxes: (min_lat, min_lon, max_lat, max_lon)
PRESET_BOUNDING_BOXES = {
    "manhattan_large": (40.700, -74.020, 40.800, -73.940),  # Full Manhattan Island (Battery Park to Central Park North)
    "manhattan": (40.750, -73.995, 40.765, -73.975),  # Midtown Manhattan (Times Sq, 5th Ave)
    "manhattan_financial": (40.702, -74.018, 40.718, -74.000),  # Financial District / Wall St
    "san_francisco_downtown": (37.785, -122.415, 37.798, -122.395),  # Financial Dist / Market St
    "london_city": (51.508, -0.100, 51.520, -0.080),  # City of London (Bank, St Paul's)
}


def geodetic_to_cartesian(
    lat: float, lon: float, center_lat: float, center_lon: float
) -> Tuple[float, float]:
    """
    Projects geodetic (lat, lon) degrees into local Cartesian metric meters (x, y)
    relative to a map center using Equirectangular projection.
    """
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    center_lat_rad = math.radians(center_lat)
    center_lon_rad = math.radians(center_lon)

    x = EARTH_RADIUS_METERS * (lon_rad - center_lon_rad) * math.cos(center_lat_rad)
    y = EARTH_RADIUS_METERS * (lat_rad - center_lat_rad)
    return x, y


def fetch_osm_map(
    bbox: Tuple[float, float, float, float],
    cache_path: str,
    timeout_seconds: int = 30,
) -> str:
    """
    Downloads raw OSM XML data from OpenStreetMap API if not already cached.
    bbox format: (min_lat, min_lon, max_lat, max_lon)
    """
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 1024:
        return cache_path

    os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
    min_lat, min_lon, max_lat, max_lon = bbox
    # OSM API expects: bbox=left,bottom,right,top -> min_lon, min_lat, max_lon, max_lat
    url = f"https://api.openstreetmap.org/api/0.6/map?bbox={min_lon},{min_lat},{max_lon},{max_lat}"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AetherGrid-AI/1.0 (Autonomous Simulation Research)"},
    )

    print(f"[*] Fetching real-world OpenStreetMap data from: {url} ...")
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        content = resp.read()
        with open(cache_path, "wb") as f:
            f.write(content)
    print(f"[+] Downloaded {len(content)} bytes to {cache_path}")
    return cache_path


class OSMRoadNetworkLoader:
    """
    Fast streaming parser for OSM XML road networks.
    Converts raw geometries into optimized DirectedGraph instances.
    """

    @classmethod
    def load_from_osm_file(
        cls,
        file_path: str,
        graph_name: str = "RealWorldOSM",
        extract_largest_component: bool = True,
    ) -> DirectedGraph:
        """
        Parses an OSM XML file using streaming iterparse to minimize memory footprint.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"OSM file not found: {file_path}")

        print(f"[*] Parsing OpenStreetMap network from {file_path} ...")
        raw_nodes: Dict[int, Tuple[float, float]] = {}
        ways: List[Dict] = []
        referenced_node_ids: Set[int] = set()

        # Phase 1: Stream extract nodes and vehicular ways
        for _, elem in ET.iterparse(file_path, events=("end",)):
            if elem.tag == "node":
                nid = int(elem.attrib["id"])
                lat = float(elem.attrib["lat"])
                lon = float(elem.attrib["lon"])
                raw_nodes[nid] = (lat, lon)
                elem.clear()

            elif elem.tag == "way":
                tags = {tag.attrib["k"]: tag.attrib["v"] for tag in elem.findall("tag")}
                hw = tags.get("highway")
                if hw in VEHICULAR_HIGHWAYS:
                    nd_refs = [int(nd.attrib["ref"]) for nd in elem.findall("nd")]
                    if len(nd_refs) >= 2:
                        ways.append({
                            "id": int(elem.attrib["id"]),
                            "name": tags.get("name", "City Street"),
                            "highway": hw,
                            "oneway": tags.get("oneway", "no").lower(),
                            "nodes": nd_refs,
                        })
                        referenced_node_ids.update(nd_refs)
                elem.clear()

        # Compute map centroid for metric projection
        active_coords = [raw_nodes[nid] for nid in referenced_node_ids if nid in raw_nodes]
        if not active_coords:
            raise ValueError("No valid vehicular road nodes discovered in OSM dataset.")

        center_lat = sum(c[0] for c in active_coords) / len(active_coords)
        center_lon = sum(c[1] for c in active_coords) / len(active_coords)

        # Phase 2: Instantiate DirectedGraph
        graph = DirectedGraph(name=graph_name)

        # Add nodes with metric Cartesian coordinates (x, y)
        node_id_remap: Dict[int, int] = {}
        for new_idx, osm_nid in enumerate(sorted(referenced_node_ids)):
            if osm_nid not in raw_nodes:
                continue
            lat, lon = raw_nodes[osm_nid]
            x, y = geodetic_to_cartesian(lat, lon, center_lat, center_lon)
            node_id_remap[osm_nid] = new_idx
            graph.add_node(
                node_id=new_idx,
                x=x,
                y=y,
                label=f"OSM_{osm_nid}",
                lat=lat,
                lon=lon,
            )

        # Phase 3: Construct directed edges
        edge_count = 0
        for way in ways:
            hw_type, base_speed, base_cap = VEHICULAR_HIGHWAYS[way["highway"]]
            street_name = way["name"]
            oneway_tag = way["oneway"]
            is_oneway = oneway_tag in ("yes", "true", "1")
            is_reverse_oneway = oneway_tag in ("-1", "reverse")

            way_nodes = [node_id_remap[nid] for nid in way["nodes"] if nid in node_id_remap]

            for i in range(len(way_nodes) - 1):
                u = way_nodes[i]
                v = way_nodes[i + 1]
                if u == v:
                    continue

                length_m = graph.nodes[u].distance_to(graph.nodes[v])
                if length_m < 0.5:
                    length_m = 0.5  # Bounded below to prevent 0-cost edges

                # Forward edge
                if not is_reverse_oneway:
                    if not graph.get_edge(u, v):
                        edge = graph.add_edge(
                            u=u,
                            v=v,
                            length_meters=length_m,
                            free_flow_speed_mps=base_speed,
                            terrain=hw_type,
                            capacity=base_cap,
                            bidirectional=False,
                            street_name=street_name,
                        )
                        edge.closure_reason = street_name  # fallback legacy
                        edge_count += 1

                # Backward edge
                if not is_oneway:
                    if not graph.get_edge(v, u):
                        edge = graph.add_edge(
                            u=v,
                            v=u,
                            length_meters=length_m,
                            free_flow_speed_mps=base_speed,
                            terrain=hw_type,
                            capacity=base_cap,
                            bidirectional=False,
                            street_name=street_name,
                        )
                        edge.closure_reason = street_name
                        edge_count += 1

        print(f"[+] Loaded raw OSM graph: {graph.num_nodes} nodes, {graph.num_edges} directed edges.")

        # Phase 4: Extract largest connected component to ensure 100% reachability
        if extract_largest_component:
            graph = cls._extract_largest_connected_component(graph)
            print(f"[+] Extracted Largest Component: {graph.num_nodes} nodes, {graph.num_edges} edges.")

        return graph

    @classmethod
    def _extract_largest_connected_component(cls, graph: DirectedGraph) -> DirectedGraph:
        """
        Finds and extracts the largest Strongly Connected Component (SCC) using
        an iterative Tarjan's algorithm. Guarantees that all node pairs have a valid directed path.
        """
        index = 0
        indices: Dict[int, int] = {}
        lowlink: Dict[int, int] = {}
        stack: List[int] = []
        on_stack: Set[int] = set()
        sccs: List[Set[int]] = []

        for root in graph.nodes:
            if root in indices:
                continue
            call_stack = [(root, iter(graph.adj.get(root, {}).keys()))]
            indices[root] = lowlink[root] = index
            index += 1
            stack.append(root)
            on_stack.add(root)

            while call_stack:
                u, it = call_stack[-1]
                try:
                    v = next(it)
                    if v not in indices:
                        indices[v] = lowlink[v] = index
                        index += 1
                        stack.append(v)
                        on_stack.add(v)
                        call_stack.append((v, iter(graph.adj.get(v, {}).keys())))
                    elif v in on_stack:
                        lowlink[u] = min(lowlink[u], indices[v])
                except StopIteration:
                    call_stack.pop()
                    if call_stack:
                        p, _ = call_stack[-1]
                        lowlink[p] = min(lowlink[p], lowlink[u])
                    if lowlink[u] == indices[u]:
                        scc = set()
                        while True:
                            w = stack.pop()
                            on_stack.remove(w)
                            scc.add(w)
                            if w == u:
                                break
                        sccs.append(scc)

        if not sccs:
            return graph

        largest = max(sccs, key=len)
        pruned_graph = DirectedGraph(name=f"{graph.name}_SCC")

        # Remap nodes
        remap: Dict[int, int] = {}
        for new_id, old_id in enumerate(sorted(largest)):
            remap[old_id] = new_id
            old_node = graph.nodes[old_id]
            pruned_graph.add_node(
                node_id=new_id,
                x=old_node.x,
                y=old_node.y,
                label=old_node.label,
                lat=old_node.lat,
                lon=old_node.lon,
                is_depot=(new_id == 0),
                is_hospital=(new_id == len(largest) - 1),
            )

        for old_u in largest:
            new_u = remap[old_u]
            for old_v, edge in graph.adj.get(old_u, {}).items():
                if old_v in largest:
                    new_v = remap[old_v]
                    new_edge = pruned_graph.add_edge(
                        u=new_u,
                        v=new_v,
                        length_meters=edge.length_meters,
                        free_flow_speed_mps=edge.max_speed_mps,
                        terrain=edge.terrain,
                        capacity=edge.capacity,
                        bidirectional=False,
                        street_name=getattr(edge, 'street_name', '') or edge.closure_reason,
                    )
                    new_edge.closure_reason = edge.closure_reason  # street name

        return pruned_graph

    @classmethod
    def load_preset_map(cls, preset_name: str = "manhattan") -> DirectedGraph:
        """
        Loads a pre-configured real-world urban map.
        Uses local cache in Aether/data/maps/ if available, or downloads from OSM.
        """
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "maps")
        os.makedirs(cache_dir, exist_ok=True)

        # Check for Manhattan large cache first
        large_cache = os.path.join(cache_dir, "manhattan_large.osm")
        if preset_name in ("manhattan_large", "manhattan_wide", "manhattan_full", "large") and os.path.exists(large_cache):
            return cls.load_from_osm_file(large_cache, graph_name="Manhattan_Island_Large_NYC")

        # Check for Manhattan midtown local cache
        midtown_cache = os.path.join(cache_dir, "manhattan_midtown.osm")
        if preset_name in ("manhattan", "midtown", "manhattan_midtown") and os.path.exists(midtown_cache):
            return cls.load_from_osm_file(midtown_cache, graph_name="Manhattan_Midtown_NYC")

        if preset_name in PRESET_BOUNDING_BOXES:
            bbox = PRESET_BOUNDING_BOXES[preset_name]
            cache_file = os.path.join(cache_dir, f"{preset_name}.osm")
            fetched_path = fetch_osm_map(bbox, cache_file)
            return cls.load_from_osm_file(fetched_path, graph_name=f"OSM_{preset_name.title()}")

        raise ValueError(f"Unknown preset map: '{preset_name}'. Options: large, manhattan, {list(PRESET_BOUNDING_BOXES.keys())}")
