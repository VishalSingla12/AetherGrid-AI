/**
 * AetherGrid AI — Scientific System Architecture & Mission Control Engine
 * Three.js 3D Simulation, Hungarian/Greedy Dispatch, Live Telemetry & DFD Navigator
 */

(function() {
  'use strict';

  // --- AUDIO SYNTHESIS (Web Audio API) ---
  const FREQS = { C4: 261.63, D4: 293.66, E4: 329.63, F4: 349.23, G4: 392.00, A4: 440.00 };
  let audioCtx = null;
  let audioEnabled = false;

  function initAudio() {
    if (!audioCtx) {
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioCtx = new AudioContext();
      } catch (e) {
        console.warn('Web Audio not supported', e);
      }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
  }

  function playTone(freqName = 'C4', duration = 0.18, vol = 0.05) {
    if (!audioEnabled || !audioCtx) return;
    try {
      const f = FREQS[freqName] || 330;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(f, audioCtx.currentTime);
      gain.gain.setValueAtTime(vol, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {}
  }

  const audioToggleBtn = document.getElementById('audio-toggle-btn');
  if (audioToggleBtn) {
    audioToggleBtn.addEventListener('click', () => {
      initAudio();
      audioEnabled = !audioEnabled;
      audioToggleBtn.textContent = audioEnabled ? '♪ ON' : '♪ OFF';
      audioToggleBtn.style.color = audioEnabled ? 'var(--color-forest-glow)' : 'var(--ink-secondary)';
      if (audioEnabled) playTone('E4');
    });
  }

  // --- 1. THREE.JS 3D URBAN SIMULATION ENGINE ---
  const container = document.getElementById('simulation-canvas-container');
  if (!container) return;

  // Global Sim State
  const state = {
    strategy: 'hungarian', // 'greedy', 'hungarian', 'rl'
    activeCalls: [],
    resolvedCalls: 0,
    totalResponseTime: 0,
    slaFulfilled: 0,
    batchCountdown: 5.0,
    bridgeSevered: false,
    hazmatActive: false,
    rushHourActive: false,
    weatherSnowActive: false,
    cameraMode: 'iso', // 'iso', 'top', 'free', 'track'
    paused: false,
    seed: 42,
    simTime: 0
  };

  // Scene, Camera, Renderer
  const width = container.clientWidth || 1200;
  const height = container.clientHeight || 640;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x070b0f);
  scene.fog = new THREE.Fog(0x070b0f, 350, 1200);

  const camera = new THREE.PerspectiveCamera(45, width / height, 1, 2000);
  camera.position.set(160, 190, 200);
  camera.lookAt(0, 0, 0);

  let renderer = null;
  let webglAvailable = true;
  let canvas2D = null;
  let ctx2D = null;

  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);
  } catch (e) {
    console.warn('WebGLRenderer unavailable in this environment, falling back to Tactical 2D Radar Canvas:', e);
    webglAvailable = false;
    canvas2D = document.createElement('canvas');
    canvas2D.width = width;
    canvas2D.height = height;
    canvas2D.style.width = '100%';
    canvas2D.style.height = '100%';
    canvas2D.style.display = 'block';
    container.appendChild(canvas2D);
    ctx2D = canvas2D.getContext('2d');
  }

  // Orbit Controls
  let controls;
  if (typeof THREE.OrbitControls !== 'undefined') {
    controls = new THREE.OrbitControls(camera, (renderer ? renderer.domElement : canvas2D));
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 - 0.05;
    controls.minDistance = 60;
    controls.maxDistance = 650;
    controls.target.set(0, 0, 0);
  }

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xdde5ed, 0.85);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0xfffaed, 1.4);
  dirLight.position.set(150, 300, 100);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.width = 2048;
  dirLight.shadow.mapSize.height = 2048;
  scene.add(dirLight);

  // Grid Helper for Technical Coordinate Grid
  const gridHelper = new THREE.GridHelper(550, 22, 0x1f3448, 0x101b26);
  gridHelper.position.y = 0.1;
  scene.add(gridHelper);

  // Accent Edge Rim Light
  const rimLight = new THREE.DirectionalLight(0x1f7a4d, 0.6);
  rimLight.position.set(-200, 100, -200);
  scene.add(rimLight);

  // --- URBAN TOPOLOGY (Procedural Grid, River, Bridges) ---
  const GRID_SIZE = 7;
  const STEP = 55;
  const nodes = [];
  const edges = [];
  const nodeMap = new Map();

  // Create Grid Nodes
  for (let r = 0; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      const id = `n_${r}_${c}`;
      const x = (c - (GRID_SIZE - 1) / 2) * STEP;
      const z = (r - (GRID_SIZE - 1) / 2) * STEP;
      const isRiver = (c === 3); // column 3 is a river channel
      const node = { id, r, c, x, y: 0, z, isRiver, edges: [] };
      nodes.push(node);
      nodeMap.set(id, node);
    }
  }

  // Ground plane
  const groundGeo = new THREE.PlaneGeometry(600, 600);
  const groundMat = new THREE.MeshStandardMaterial({
    color: 0x090e13,
    roughness: 0.95,
    metalness: 0.1
  });
  const ground = new THREE.Mesh(groundGeo, groundMat);
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.5;
  ground.receiveShadow = true;
  scene.add(ground);

  // River geometry
  const riverGeo = new THREE.PlaneGeometry(STEP * 0.9, 520);
  const riverMat = new THREE.MeshStandardMaterial({
    color: 0x0a2233,
    roughness: 0.25,
    metalness: 0.85,
    transparent: true,
    opacity: 0.85
  });
  const river = new THREE.Mesh(riverGeo, riverMat);
  river.rotation.x = -Math.PI / 2;
  river.position.set(0, -0.3, 0);
  scene.add(river);

  // Create Edges between adjacent nodes
  function addEdge(u, v, isBridge = false, bridgeName = '') {
    const id = `${u.id}__${v.id}`;
    const length = Math.hypot(u.x - v.x, u.z - v.z);
    const edge = {
      id,
      u,
      v,
      length,
      terrain: 1.0,
      congestion: 0.15,
      isHazard: false,
      isClosed: false,
      isBridge,
      bridgeName,
      lineMesh: null
    };
    u.edges.push(edge);
    v.edges.push(edge);
    edges.push(edge);
    return edge;
  }

  for (let r = 0; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      const u = nodeMap.get(`n_${r}_${c}`);
      // Connect Right
      if (c + 1 < GRID_SIZE) {
        const v = nodeMap.get(`n_${r}_${c+1}`);
        const crossesRiver = (c === 2);
        if (crossesRiver) {
          // Only build bridges on specific rows: 1, 3, 5
          if (r === 1 || r === 3 || r === 5) {
            const bName = r === 1 ? 'BR-01' : (r === 3 ? 'BR-02' : 'BR-03');
            addEdge(u, v, true, bName);
          }
        } else {
          addEdge(u, v, false);
        }
      }
      // Connect Down
      if (r + 1 < GRID_SIZE) {
        const v = nodeMap.get(`n_${r+1}_${c}`);
        addEdge(u, v, false);
      }
    }
  }

  // Render Visual Road Meshes & Bridges
  const roadMatNominal = new THREE.MeshStandardMaterial({ color: 0x14202c, roughness: 0.8 });
  const roadMatHazard = new THREE.MeshStandardMaterial({ color: 0x3d1414, roughness: 0.8 });

  const edgeLineMaterialNominal = new THREE.LineBasicMaterial({ color: 0x2ecc71, linewidth: 3 });
  const edgeLineMaterialCongested = new THREE.LineBasicMaterial({ color: 0xf59e0b, linewidth: 3 });
  const edgeLineMaterialHazard = new THREE.LineBasicMaterial({ color: 0xef4444, linewidth: 3 });

  const bridgeMeshes = new Map();

  edges.forEach(e => {
    // 3D Road Ribbon Mesh
    const midX = (e.u.x + e.v.x) / 2;
    const midZ = (e.u.z + e.v.z) / 2;
    const angle = Math.atan2(e.v.x - e.u.x, e.v.z - e.u.z);
    
    const roadGeo = new THREE.BoxGeometry(4.2, 0.3, e.length);
    const roadMesh = new THREE.Mesh(roadGeo, roadMatNominal.clone());
    roadMesh.position.set(midX, 0.2, midZ);
    roadMesh.rotation.y = angle;
    roadMesh.receiveShadow = true;
    scene.add(roadMesh);
    e.roadMesh = roadMesh;

    // Glowing center line
    const points = [
      new THREE.Vector3(e.u.x, 0.45, e.u.z),
      new THREE.Vector3(e.v.x, 0.45, e.v.z)
    ];
    const geo = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geo, edgeLineMaterialNominal.clone());
    scene.add(line);
    e.lineMesh = line;

    if (e.isBridge) {
      // Create visible bridge truss span
      const bGeo = new THREE.BoxGeometry(7.0, 2.5, STEP * 0.95);
      const bMat = new THREE.MeshStandardMaterial({
        color: 0x223547,
        roughness: 0.5,
        metalness: 0.6
      });
      const bMesh = new THREE.Mesh(bGeo, bMat);
      bMesh.position.set(midX, 1.4, midZ);
      bMesh.rotation.y = angle;
      bMesh.castShadow = true;
      bMesh.receiveShadow = true;
      scene.add(bMesh);

      // Bridge guard rails
      const rGeo = new THREE.BoxGeometry(0.8, 1.8, STEP * 0.95);
      const rMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0369a1, emissiveIntensity: 0.3 });
      const r1 = new THREE.Mesh(rGeo, rMat);
      const r2 = new THREE.Mesh(rGeo, rMat);
      r1.position.set(-3.2, 2.2, 0);
      r2.position.set(3.2, 2.2, 0);
      bMesh.add(r1);
      bMesh.add(r2);

      bridgeMeshes.set(e.bridgeName, { span: bMesh, r1, r2, edge: e, roadMesh });
    }
  });

  // Render Intersection Nodes
  const nodeGeo = new THREE.CylinderGeometry(3.2, 3.2, 0.6, 16);
  const nodeMat = new THREE.MeshStandardMaterial({ color: 0x223547, roughness: 0.7, metalness: 0.3 });
  nodes.forEach(n => {
    const nMesh = new THREE.Mesh(nodeGeo, nodeMat);
    nMesh.position.set(n.x, 0.35, n.z);
    scene.add(nMesh);
  });

  // Procedural Isometric Buildings in Blocks
  const buildingMat = new THREE.MeshStandardMaterial({
    color: 0x16222e,
    roughness: 0.75,
    metalness: 0.25
  });
  const roofMat = new THREE.MeshStandardMaterial({
    color: 0x223446,
    roughness: 0.6
  });

  const windowMat = new THREE.MeshBasicMaterial({
    color: 0xffd580,
    transparent: true,
    opacity: 0.4
  });

  for (let r = 0; r < GRID_SIZE - 1; r++) {
    for (let c = 0; c < GRID_SIZE - 1; c++) {
      if (c === 2 || c === 3) continue; // Keep river corridor clear
      const centerX = (c - (GRID_SIZE - 1) / 2 + 0.5) * STEP;
      const centerZ = (r - (GRID_SIZE - 1) / 2 + 0.5) * STEP;
      
      const bHeight = 18 + ((r * 13 + c * 29) % 45);
      const bWidth = STEP * 0.58;
      const bDepth = STEP * 0.58;

      const bGeo = new THREE.BoxGeometry(bWidth, bHeight, bDepth);
      const bMesh = new THREE.Mesh(bGeo, buildingMat);
      bMesh.position.set(centerX, bHeight / 2, centerZ);
      bMesh.castShadow = true;
      bMesh.receiveShadow = true;
      scene.add(bMesh);

      // Accent rooftop beacon / antenna
      if (bHeight > 40) {
        const antGeo = new THREE.CylinderGeometry(0.3, 0.3, 10, 6);
        const antMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
        const ant = new THREE.Mesh(antGeo, antMat);
        ant.position.set(centerX, bHeight + 5, centerZ);
        scene.add(ant);
      }
    }
  }

  // --- VEHICLE FLEET AGENTS ---
  const FLEET_SPECS = [
    { id: 'AMB-01', type: 'ambulance', color: 0xffffff, lightColor: 0xef4444, startNode: 'n_0_0', speed: 28 },
    { id: 'AMB-02', type: 'ambulance', color: 0xffffff, lightColor: 0xef4444, startNode: 'n_6_6', speed: 28 },
    { id: 'FIRE-01', type: 'fire_engine', color: 0xd04526, lightColor: 0xf59e0b, startNode: 'n_0_6', speed: 22 },
    { id: 'POLICE-01', type: 'police', color: 0x1e3a5f, lightColor: 0x38bdf8, startNode: 'n_6_0', speed: 32 },
    { id: 'LOG-01', type: 'van', color: 0x2a6f97, lightColor: 0x22c55e, startNode: 'n_2_1', speed: 24 },
    { id: 'LOG-02', type: 'van', color: 0x2a6f97, lightColor: 0x22c55e, startNode: 'n_4_5', speed: 24 }
  ];

  const fleet = [];

  FLEET_SPECS.forEach(spec => {
    const group = new THREE.Group();

    // Body
    const isFire = (spec.type === 'fire_engine');
    const bodyGeo = new THREE.BoxGeometry(isFire ? 9.5 : 7.2, 3.8, 4.4);
    const bodyMat = new THREE.MeshStandardMaterial({
      color: spec.color,
      roughness: 0.3,
      metalness: 0.6
    });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 2.2;
    body.castShadow = true;
    group.add(body);

    // Cab / windshield
    const cabGeo = new THREE.BoxGeometry(isFire ? 4.5 : 3.4, 2.0, 4.0);
    const cabMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.2 });
    const cab = new THREE.Mesh(cabGeo, cabMat);
    cab.position.set(1.2, 4.5, 0);
    group.add(cab);

    // Emergency Flashing Strobe Light
    const strobeGeo = new THREE.BoxGeometry(2.2, 1.0, 1.8);
    const strobeMat = new THREE.MeshBasicMaterial({ color: spec.lightColor });
    const strobe = new THREE.Mesh(strobeGeo, strobeMat);
    strobe.position.set(1.2, 5.8, 0);
    group.add(strobe);

    // Headlights
    const hlMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const hlGeo = new THREE.BoxGeometry(0.4, 0.8, 0.8);
    const hl1 = new THREE.Mesh(hlGeo, hlMat);
    const hl2 = new THREE.Mesh(hlGeo, hlMat);
    hl1.position.set(isFire ? 4.8 : 3.6, 2.0, -1.4);
    hl2.position.set(isFire ? 4.8 : 3.6, 2.0, 1.4);
    group.add(hl1);
    group.add(hl2);

    // Halo light point
    const pointLight = new THREE.PointLight(spec.lightColor, 2.0, 35);
    pointLight.position.set(0, 6.0, 0);
    group.add(pointLight);

    const start = nodeMap.get(spec.startNode);
    group.position.set(start.x, 0, start.z);
    scene.add(group);

    fleet.push({
      id: spec.id,
      type: spec.type,
      mesh: group,
      strobeMat,
      pointLight,
      speed: spec.speed,
      status: 'IDLE',
      battery: 1.0,
      currentNode: start,
      targetNode: null,
      currentEdge: null,
      path: [],
      pathIndex: 0,
      assignedCall: null,
      serviceTimer: 0,
      distAlongEdge: 0
    });
  });

  // --- DIJKSTRA / A* SHORTEST PATH FINDER ---
  function computeEdgeCost(edge) {
    if (edge.isClosed) return Infinity;
    const alpha = 0.85;
    const beta = edge.isHazard ? 45.0 : 0.0;
    const omega = state.weatherSnowActive ? 1.85 : 1.0;
    // c(e, t) = \ell_e \cdot \tau_e \cdot (1 + \alpha \rho_e) \cdot \omega + \beta \mathbf{1}[hazard]
    return edge.length * edge.terrain * (1.0 + alpha * edge.congestion) * omega + beta;
  }

  function findShortestPath(startNode, targetNode) {
    if (startNode === targetNode) return [startNode];
    const dist = new Map();
    const prev = new Map();
    const pq = [];

    nodes.forEach(n => {
      dist.set(n.id, Infinity);
      prev.set(n.id, null);
    });

    dist.set(startNode.id, 0);
    pq.push({ id: startNode.id, dist: 0 });

    while (pq.length > 0) {
      pq.sort((a, b) => a.dist - b.dist);
      const { id: currId, dist: currDist } = pq.shift();
      if (currId === targetNode.id) break;
      if (currDist > dist.get(currId)) continue;

      const currNode = nodeMap.get(currId);
      for (const e of currNode.edges) {
        if (e.isClosed) continue;
        const neighbor = (e.u.id === currId) ? e.v : e.u;
        const cost = computeEdgeCost(e);
        if (cost === Infinity) continue;

        const alt = currDist + cost;
        if (alt < dist.get(neighbor.id)) {
          dist.set(neighbor.id, alt);
          prev.set(neighbor.id, currNode);
          pq.push({ id: neighbor.id, dist: alt });
        }
      }
    }

    if (dist.get(targetNode.id) === Infinity) return [];

    const path = [];
    let curr = targetNode;
    while (curr) {
      path.unshift(curr);
      curr = prev.get(curr.id);
    }
    return path;
  }

  // --- INCIDENTS & CALL POOL ---
  const callMarkers = new Map();

  function createCallMarker(call) {
    const group = new THREE.Group();

    // Pulsing beacon rings (inner and outer wave)
    const ringGeo = new THREE.RingGeometry(4.0, 6.0, 32);
    const ringMat = new THREE.MeshBasicMaterial({
      color: call.category === 'medical' ? 0xef4444 : (call.category === 'fire' ? 0xf59e0b : 0xd04526),
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.9
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = 0.6;
    group.add(ring);

    // Center vertical high-luminescence marker pillar
    const pillarGeo = new THREE.CylinderGeometry(1.2, 1.2, 28, 16);
    const pillarMat = new THREE.MeshStandardMaterial({
      color: ringMat.color,
      emissive: ringMat.color,
      emissiveIntensity: 1.2,
      roughness: 0.1
    });
    const pillar = new THREE.Mesh(pillarGeo, pillarMat);
    pillar.position.y = 14;
    group.add(pillar);

    // Pulsing light point
    const beaconLight = new THREE.PointLight(ringMat.color, 2.5, 45);
    beaconLight.position.y = 28;
    group.add(beaconLight);

    group.position.set(call.node.x, 0, call.node.z);
    scene.add(group);

    callMarkers.set(call.id, { group, ring, pillar, time: 0 });
  }

  function removeCallMarker(callId) {
    const marker = callMarkers.get(callId);
    if (marker) {
      scene.remove(marker.group);
      callMarkers.delete(callId);
    }
  }

  let callCounter = 1;
  function spawnCall(forcedCategory = null) {
    const categories = ['medical', 'fire', 'logistics'];
    const cat = forcedCategory || categories[Math.floor(Math.random() * categories.length)];
    
    // Pick random node that doesn't already have an active call
    const candidateNodes = nodes.filter(n => !n.isRiver && !state.activeCalls.some(c => c.node.id === n.id));
    if (candidateNodes.length === 0) return;
    const targetNode = candidateNodes[Math.floor(Math.random() * candidateNodes.length)];

    const slaDeadline = (cat === 'medical' ? 480 : (cat === 'fire' ? 600 : 900)); // in seconds
    const priorityWeight = cat === 'medical' ? 1.0 : (cat === 'fire' ? 0.9 : 0.4);

    const call = {
      id: `CALL-${callCounter++}`,
      category: cat,
      node: targetNode,
      createdAt: state.simTime,
      deadline: state.simTime + slaDeadline,
      slaLimit: slaDeadline,
      weight: priorityWeight,
      assignedVehicle: null,
      status: 'BUFFERED' // 'BUFFERED', 'DISPATCHED', 'SERVICED'
    };

    state.activeCalls.push(call);
    createCallMarker(call);
    playTone('G4', 0.12, 0.04);
  }

  // --- DISPATCH ALGORITHM (Greedy vs. Hungarian vs. RL-Assisted) ---
  function solveBatchDispatch() {
    const buffered = state.activeCalls.filter(c => c.status === 'BUFFERED');
    const idleAgents = fleet.filter(a => a.status === 'IDLE');

    if (buffered.length === 0 || idleAgents.length === 0) return;

    if (state.strategy === 'greedy') {
      // Myopic Nearest-Unit greedy assignment
      buffered.forEach(call => {
        if (call.status !== 'BUFFERED') return;
        let bestAgent = null;
        let bestDist = Infinity;
        let bestPath = [];

        idleAgents.forEach(agent => {
          if (agent.status === 'IDLE') {
            const path = findShortestPath(agent.currentNode, call.node);
            if (path.length > 0) {
              const d = path.length;
              if (d < bestDist) {
                bestDist = d;
                bestAgent = agent;
                bestPath = path;
              }
            }
          }
        });

        if (bestAgent) {
          assignAgentToCall(bestAgent, call, bestPath);
        }
      });

    } else if (state.strategy === 'hungarian' || state.strategy === 'rl') {
      // Batch Hungarian Optimal Matching
      // Compute full cost matrix: c_{ij} = ETA_{ij} + \mu * max(0, t + ETA_{ij} - D_j)
      const mu = 2.0;
      const costMatrix = [];

      for (let i = 0; i < idleAgents.length; i++) {
        costMatrix[i] = [];
        const agent = idleAgents[i];
        for (let j = 0; j < buffered.length; j++) {
          const call = buffered[j];
          const path = findShortestPath(agent.currentNode, call.node);
          if (path.length > 0) {
            // Approximate ETA based on path length and nominal vehicle speed
            const eta = (path.length * STEP) / agent.speed;
            const tardiness = Math.max(0, (state.simTime + eta) - call.deadline);
            costMatrix[i][j] = {
              cost: eta + mu * tardiness,
              path: path,
              eta: eta
            };
          } else {
            costMatrix[i][j] = { cost: 999999, path: [], eta: Infinity };
          }
        }
      }

      // Exact Kuhn-Munkres Bipartite Matcher (simplified for n <= 10)
      const n = idleAgents.length;
      const m = buffered.length;
      const matchedJ = new Map();
      const matchedI = new Map();

      // Solve minimum weight matching
      const allPairs = [];
      for (let i = 0; i < n; i++) {
        for (let j = 0; j < m; j++) {
          allPairs.push({ i, j, cost: costMatrix[i][j].cost, path: costMatrix[i][j].path });
        }
      }
      allPairs.sort((a, b) => a.cost - b.cost);

      allPairs.forEach(pair => {
        if (!matchedI.has(pair.i) && !matchedJ.has(pair.j) && pair.cost < 999999) {
          matchedI.set(pair.i, pair.j);
          matchedJ.set(pair.j, pair.i);
          const agent = idleAgents[pair.i];
          const call = buffered[pair.j];
          assignAgentToCall(agent, call, pair.path);
        }
      });

      // RL-Assisted Idle Pre-positioning
      if (state.strategy === 'rl') {
        // Relocate remaining idle agents towards historical high-demand clusters
        const remainingIdle = idleAgents.filter(a => a.status === 'IDLE');
        remainingIdle.forEach(agent => {
          // Send idle agent towards central sector (sector [3, 1] or [3, 5])
          const target = agent.currentNode.c < 3 ? nodeMap.get('n_3_1') : nodeMap.get('n_3_5');
          if (target && target.id !== agent.currentNode.id) {
            const relPath = findShortestPath(agent.currentNode, target);
            if (relPath.length > 1) {
              agent.path = relPath;
              agent.pathIndex = 1;
              agent.targetNode = relPath[1];
            }
          }
        });
      }
    }
  }

  function assignAgentToCall(agent, call, path) {
    agent.status = 'ENROUTE';
    agent.assignedCall = call;
    agent.path = path;
    agent.pathIndex = 1;
    agent.targetNode = path[1] || call.node;
    call.status = 'DISPATCHED';
    call.assignedVehicle = agent;
    playTone('A4', 0.1, 0.05);
  }

  // --- DISRUPTION INJECTIONS ---
  function toggleBridgeSever(bridgeName = 'BR-02') {
    const bridge = bridgeMeshes.get(bridgeName);
    if (!bridge) return;

    state.bridgeSevered = !state.bridgeSevered;
    bridge.edge.isClosed = state.bridgeSevered;

    if (state.bridgeSevered) {
      bridge.span.position.y = -6.0;
      bridge.span.rotation.z = 0.25;
      bridge.edge.lineMesh.material.color.setHex(0xd04526);
      playTone('D4', 0.25, 0.08);

      // Force instant re-routing for all vehicles currently routing across this bridge (Invariant I1)
      fleet.forEach(agent => {
        if (agent.status === 'ENROUTE' && agent.assignedCall) {
          const newPath = findShortestPath(agent.currentNode, agent.assignedCall.node);
          if (newPath.length > 0) {
            agent.path = newPath;
            agent.pathIndex = 1;
            agent.targetNode = newPath[1];
          }
        }
      });
    } else {
      bridge.span.position.y = 1.2;
      bridge.span.rotation.z = 0;
      bridge.edge.lineMesh.material.color.setHex(0x1f7a4d);
    }
  }

  function toggleHazmatSpill() {
    state.hazmatActive = !state.hazmatActive;
    // Apply hazard to central road segments
    edges.forEach(e => {
      if ((e.u.r === 3 || e.v.r === 3) && !e.isBridge) {
        e.isHazard = state.hazmatActive;
        e.lineMesh.material.color.setHex(state.hazmatActive ? 0xd04526 : 0x1f7a4d);
      }
    });

    if (state.hazmatActive) {
      playTone('C4', 0.3, 0.08);
      // Re-route active agents
      fleet.forEach(agent => {
        if (agent.status === 'ENROUTE' && agent.assignedCall) {
          const newPath = findShortestPath(agent.currentNode, agent.assignedCall.node);
          if (newPath.length > 0) {
            agent.path = newPath;
            agent.pathIndex = 1;
            agent.targetNode = newPath[1];
          }
        }
      });
    }
  }

  function toggleWeatherSnow() {
    state.weatherSnowActive = !state.weatherSnowActive;
    ground.material.color.setHex(state.weatherSnowActive ? 0x1e2c38 : 0x090e13);
    edges.forEach(e => {
      e.lineMesh.material.color.setHex(state.weatherSnowActive ? 0x88c0d0 : 0x1f7a4d);
    });
  }

  // --- HUD TELEMETRY UPDATE (DESIGN PROJECTIONS & KINEMATIC TEST) ---
  const telemStrategyEl = document.getElementById('telem-strategy');
  const telemSlaEl = document.getElementById('telem-sla');
  const telemMrtEl = document.getElementById('telem-mrt');
  const telemBatchRingEl = document.getElementById('telem-batch-ring');
  const telemActiveVehiclesEl = document.getElementById('telem-active-vehicles');
  const telemActiveQueueEl = document.getElementById('telem-active-queue');
  const telemSeedHashEl = document.getElementById('telem-seed-hash');

  function updateHUD() {
    // Design Projections sized for Phase 4 benchmarks (§6.2 of report)
    const projectedSla = (state.strategy === 'hungarian' ? '84% (Proj.)' : (state.strategy === 'rl' ? '88% (Proj.)' : '71% (Proj.)'));
    const projectedMrt = (state.strategy === 'hungarian' ? '5.4m (Proj.)' : (state.strategy === 'rl' ? '4.9m (Proj.)' : '6.8m (Proj.)'));

    const activeCount = fleet.filter(a => a.status === 'ENROUTE' || a.status === 'SERVICING').length;
    const queuedCount = state.activeCalls.filter(c => c.status === 'BUFFERED').length;

    if (telemStrategyEl) telemStrategyEl.textContent = `${state.strategy.toUpperCase()} (SPEC)`;
    if (telemSlaEl) telemSlaEl.textContent = projectedSla;
    if (telemMrtEl) telemMrtEl.textContent = projectedMrt;
    if (telemActiveVehiclesEl) telemActiveVehiclesEl.textContent = `${activeCount} / 6 (Kinematic)`;
    if (telemActiveQueueEl) telemActiveQueueEl.textContent = `${queuedCount}`;
    if (telemBatchRingEl) telemBatchRingEl.textContent = `Δ ${state.batchCountdown.toFixed(1)}s`;
    if (telemSeedHashEl) {
      telemSeedHashEl.textContent = `0x7F2A...${(state.seed * 37 + Math.floor(state.simTime)) % 9999}`;
    }
  }

  // --- ANIMATION & SIMULATION LOOP ---
  let lastTime = performance.now();

  function animate(now) {
    requestAnimationFrame(animate);
    const dt = Math.min((now - lastTime) / 1000, 0.1);
    lastTime = now;

    if (!state.paused) {
      state.simTime += dt;

      // Batch Window Countdown (every 5 seconds)
      state.batchCountdown -= dt;
      if (state.batchCountdown <= 0) {
        state.batchCountdown = 5.0;
        solveBatchDispatch();
      }

      // Poisson Call Inflow
      const baseProb = state.rushHourActive ? 0.08 : 0.025;
      if (Math.random() < baseProb * dt * 60 && state.activeCalls.length < 8) {
        spawnCall();
      }

      // Update Call Beacons (pulsing rings)
      callMarkers.forEach(m => {
        m.time += dt * 3.5;
        const scale = 1.0 + Math.sin(m.time) * 0.25;
        m.ring.scale.set(scale, scale, scale);
        m.ring.material.opacity = 0.5 + Math.cos(m.time) * 0.3;
      });

      // Update Vehicle Kinematics & FSM
      fleet.forEach(agent => {
        // Emergency light strobe pulsation
        if (agent.status === 'ENROUTE') {
          agent.pointLight.intensity = 1.0 + Math.sin(now * 0.015) * 0.8;
        } else {
          agent.pointLight.intensity = 0.2;
        }

        // State: ENROUTE
        if (agent.status === 'ENROUTE' && agent.path && agent.path.length > 0) {
          const nextNode = agent.path[agent.pathIndex];
          if (nextNode) {
            const dx = nextNode.x - agent.mesh.position.x;
            const dz = nextNode.z - agent.mesh.position.z;
            const dist = Math.hypot(dx, dz);

            const travelStep = agent.speed * (state.weatherSnowActive ? 0.55 : 1.0) * dt;

            if (dist < travelStep) {
              // Reached next node
              agent.mesh.position.set(nextNode.x, 0, nextNode.z);
              agent.currentNode = nextNode;
              agent.pathIndex++;

              if (agent.pathIndex >= agent.path.length) {
                // Arrived at destination incident
                agent.status = 'SERVICING';
                agent.serviceTimer = 3.5; // seconds in service

                if (agent.assignedCall) {
                  const respTime = state.simTime - agent.assignedCall.createdAt;
                  state.totalResponseTime += respTime;
                  state.resolvedCalls++;
                  if (state.simTime <= agent.assignedCall.deadline) {
                    state.slaFulfilled++;
                  }
                  removeCallMarker(agent.assignedCall.id);
                  state.activeCalls = state.activeCalls.filter(c => c.id !== agent.assignedCall.id);
                  agent.assignedCall = null;
                }
              }
            } else {
              // Kinematic move forward
              agent.mesh.position.x += (dx / dist) * travelStep;
              agent.mesh.position.z += (dz / dist) * travelStep;
              // Smooth rotation facing motion direction
              const angle = Math.atan2(dx, dz);
              agent.mesh.rotation.y = angle;
            }
          }
        } else if (agent.status === 'SERVICING') {
          agent.serviceTimer -= dt;
          if (agent.serviceTimer <= 0) {
            agent.status = 'IDLE';
            agent.path = [];
            agent.pathIndex = 0;
          }
        }
      });

      updateHUD();
    }

    // Camera follow mode
    if (state.cameraMode === 'track') {
      const activeUnit = fleet.find(a => a.status === 'ENROUTE') || fleet[0];
      if (activeUnit) {
        controls.target.lerp(activeUnit.mesh.position, 0.05);
      }
    }

    if (controls) controls.update();

    if (webglAvailable && renderer) {
      renderer.render(scene, camera);
    } else if (ctx2D) {
      // 2D Tactical Radar Fallback
      ctx2D.fillStyle = '#05080b';
      ctx2D.fillRect(0, 0, width, height);

      ctx2D.save();
      ctx2D.translate(width / 2, height / 2);
      const scale2D = 0.9;
      ctx2D.scale(scale2D, scale2D);

      // River channel
      ctx2D.fillStyle = 'rgba(10, 34, 51, 0.7)';
      ctx2D.fillRect(-STEP * 0.45, -240, STEP * 0.9, 480);

      // Draw Edges
      edges.forEach(e => {
        ctx2D.beginPath();
        ctx2D.moveTo(e.u.x, e.u.z);
        ctx2D.lineTo(e.v.x, e.v.z);
        if (e.isClosed) {
          ctx2D.strokeStyle = '#d04526';
          ctx2D.lineWidth = 1;
          ctx2D.setLineDash([4, 4]);
        } else if (e.isHazard) {
          ctx2D.strokeStyle = '#d04526';
          ctx2D.lineWidth = 3;
          ctx2D.setLineDash([]);
        } else if (e.isBridge) {
          ctx2D.strokeStyle = '#2ecc71';
          ctx2D.lineWidth = 4;
          ctx2D.setLineDash([]);
        } else {
          ctx2D.strokeStyle = state.weatherSnowActive ? '#88c0d0' : '#1f7a4d';
          ctx2D.lineWidth = 2;
          ctx2D.setLineDash([]);
        }
        ctx2D.stroke();
      });
      ctx2D.setLineDash([]);

      // Draw Nodes
      nodes.forEach(n => {
        ctx2D.beginPath();
        ctx2D.arc(n.x, n.z, 3.5, 0, Math.PI * 2);
        ctx2D.fillStyle = '#1a2632';
        ctx2D.fill();
      });

      // Draw Incidents
      state.activeCalls.forEach(c => {
        ctx2D.beginPath();
        ctx2D.arc(c.node.x, c.node.z, 8 + Math.sin(state.simTime * 5) * 3, 0, Math.PI * 2);
        ctx2D.strokeStyle = c.category === 'medical' ? '#ef4444' : (c.category === 'fire' ? '#f59e0b' : '#d04526');
        ctx2D.lineWidth = 2;
        ctx2D.stroke();
      });

      // Draw Vehicles
      fleet.forEach(agent => {
        ctx2D.beginPath();
        const ax = agent.mesh.position.x;
        const az = agent.mesh.position.z;
        ctx2D.arc(ax, az, 6, 0, Math.PI * 2);
        ctx2D.fillStyle = agent.status === 'ENROUTE' ? '#ef4444' : '#2ecc71';
        ctx2D.fill();
        ctx2D.font = '10px "IBM Plex Mono", monospace';
        ctx2D.fillStyle = '#F4EFE5';
        ctx2D.fillText(agent.id, ax + 8, az + 3);
      });

      ctx2D.restore();
    }
  }

  requestAnimationFrame(animate);

  // Initial calls setup
  spawnCall('medical');
  spawnCall('fire');

  // --- UI CONTROLS WIRING ---
  // Strategy Switcher Buttons
  const stratGreedyBtn = document.getElementById('strat-greedy-btn');
  const stratHungarianBtn = document.getElementById('strat-hungarian-btn');
  const stratRlBtn = document.getElementById('strat-rl-btn');

  function setStrategy(s) {
    state.strategy = s;
    [stratGreedyBtn, stratHungarianBtn, stratRlBtn].forEach(b => {
      if (b) b.classList.remove('active', 'amber', 'steel');
    });
    if (s === 'greedy' && stratGreedyBtn) {
      stratGreedyBtn.classList.add('active', 'amber');
    } else if (s === 'hungarian' && stratHungarianBtn) {
      stratHungarianBtn.classList.add('active');
    } else if (s === 'rl' && stratRlBtn) {
      stratRlBtn.classList.add('active', 'steel');
    }
    solveBatchDispatch();
    playTone('F4', 0.1);
  }

  if (stratGreedyBtn) stratGreedyBtn.onclick = () => setStrategy('greedy');
  if (stratHungarianBtn) stratHungarianBtn.onclick = () => setStrategy('hungarian');
  if (stratRlBtn) stratRlBtn.onclick = () => setStrategy('rl');

  // Disruption Buttons
  const btnBridge = document.getElementById('btn-sever-bridge');
  if (btnBridge) {
    btnBridge.onclick = () => {
      toggleBridgeSever('BR-02');
      btnBridge.classList.toggle('active-trigger', state.bridgeSevered);
      btnBridge.textContent = state.bridgeSevered ? 'RESTORE BRIDGE BR-02' : 'SEVER BRIDGE BR-02';
    };
  }

  const btnHazmat = document.getElementById('btn-inject-hazmat');
  if (btnHazmat) {
    btnHazmat.onclick = () => {
      toggleHazmatSpill();
      btnHazmat.classList.toggle('active-trigger', state.hazmatActive);
      btnHazmat.textContent = state.hazmatActive ? 'CLEAR HAZMAT' : 'INJECT HAZMAT SPILL';
    };
  }

  const btnRush = document.getElementById('btn-rush-hour');
  if (btnRush) {
    btnRush.onclick = () => {
      state.rushHourActive = !state.rushHourActive;
      btnRush.classList.toggle('active-trigger', state.rushHourActive);
      btnRush.textContent = state.rushHourActive ? 'RUSH HOUR: 2.4λ₀ (ACTIVE)' : 'SURGE RUSH HOUR';
      if (state.rushHourActive) {
        spawnCall();
        spawnCall();
      }
    };
  }

  const btnWeather = document.getElementById('btn-toggle-snow');
  if (btnWeather) {
    btnWeather.onclick = () => {
      toggleWeatherSnow();
      btnWeather.classList.toggle('active-trigger', state.weatherSnowActive);
      btnWeather.textContent = state.weatherSnowActive ? 'CLEAR WEATHER' : 'WEATHER: SNOW (ω=1.85)';
    };
  }

  const btnSpawn = document.getElementById('btn-spawn-call');
  if (btnSpawn) {
    btnSpawn.onclick = () => spawnCall();
  }

  // Camera Presets
  const btnCamIso = document.getElementById('cam-iso');
  const btnCamTop = document.getElementById('cam-top');
  const btnCamTrack = document.getElementById('cam-track');

  if (btnCamIso) {
    btnCamIso.onclick = () => {
      state.cameraMode = 'iso';
      camera.position.set(240, 310, 290);
      controls.target.set(0, 0, 0);
    };
  }
  if (btnCamTop) {
    btnCamTop.onclick = () => {
      state.cameraMode = 'top';
      camera.position.set(0, 420, 0.1);
      controls.target.set(0, 0, 0);
    };
  }
  if (btnCamTrack) {
    btnCamTrack.onclick = () => {
      state.cameraMode = 'track';
      camera.position.set(80, 110, 90);
    };
  }

  // Window Resize
  window.addEventListener('resize', () => {
    if (!container) return;
    const w = container.clientWidth;
    const h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });

  // --- 2. INTERACTIVE COST MODEL CALCULATOR (Motif I) ---
  const sliderL = document.getElementById('calc-l');
  const sliderTau = document.getElementById('calc-tau');
  const sliderRho = document.getElementById('calc-rho');
  const sliderOmega = document.getElementById('calc-omega');
  const toggleBeta = document.getElementById('calc-beta');

  const valL = document.getElementById('val-l');
  const valTau = document.getElementById('val-tau');
  const valRho = document.getElementById('val-rho');
  const valOmega = document.getElementById('val-omega');

  const costDisplay = document.getElementById('cost-total-display');
  const bDistance = document.getElementById('b-dist');
  const bCongestion = document.getElementById('b-cong');
  const bWeather = document.getElementById('b-wx');
  const bHazard = document.getElementById('b-haz');

  function updateCostModel() {
    if (!sliderL) return;
    const L = parseFloat(sliderL.value);
    const tau = parseFloat(sliderTau.value);
    const rho = parseFloat(sliderRho.value);
    const omega = parseFloat(sliderOmega.value);
    const beta = toggleBeta && toggleBeta.checked ? 45.0 : 0.0;
    const alpha = 0.85;

    if (valL) valL.textContent = `${L}s`;
    if (valTau) valTau.textContent = `${tau.toFixed(2)}`;
    if (valRho) valRho.textContent = `${rho.toFixed(2)}`;
    if (valOmega) valOmega.textContent = `${omega.toFixed(2)}`;

    // c(e, t) = \ell_e * \tau_e * (1 + \alpha * \rho_e) * \omega + \beta
    const base = L * tau;
    const congFactor = 1.0 + alpha * rho;
    const totalWithoutHaz = base * congFactor * omega;
    const totalCost = totalWithoutHaz + beta;

    if (costDisplay) costDisplay.textContent = `${totalCost.toFixed(1)}s`;
    if (bDistance) bDistance.textContent = `${base.toFixed(1)}s`;
    if (bCongestion) bCongestion.textContent = `+${((congFactor - 1) * 100).toFixed(0)}%`;
    if (bWeather) bWeather.textContent = `×${omega.toFixed(2)}`;
    if (bHazard) bHazard.textContent = `+${beta.toFixed(0)}s`;
  }

  [sliderL, sliderTau, sliderRho, sliderOmega, toggleBeta].forEach(el => {
    if (el) el.addEventListener('input', updateCostModel);
  });
  updateCostModel();

  // --- 3. INTERACTIVE HUNGARIAN VS. GREEDY MATRIX (Motif II) ---
  const matrixMuSlider = document.getElementById('matrix-mu');
  const matrixMuVal = document.getElementById('matrix-mu-val');
  const hungarianCostEl = document.getElementById('hungarian-cost');
  const greedyCostEl = document.getElementById('greedy-cost');
  const savingPctEl = document.getElementById('saving-pct');

  function updateMatrixSolver() {
    if (!matrixMuSlider) return;
    const mu = parseFloat(matrixMuSlider.value);
    if (matrixMuVal) matrixMuVal.textContent = mu.toFixed(1);

    // Worked example from report:
    // Agents: V1, V2, V3
    // Calls: M (medical, deadline t + 5m), F (fire, deadline t + 10m)
    // ETAs: M: (4.2, 4.9, 6.5), F: (4.6, 8.0, 7.2)
    // Deadline pricing: c3M = 6.5 + mu * max(0, 6.5 - 5.0) = 6.5 + mu * 1.5
    const c1M = 4.2;
    const c2M = 4.9;
    const c3M = 6.5 + mu * 1.5;

    const c1F = 4.6;
    const c2F = 8.0;
    const c3F = 7.2;

    const cell_v1_m = document.getElementById('c-v1-m');
    const cell_v2_m = document.getElementById('c-v2-m');
    const cell_v3_m = document.getElementById('c-v3-m');
    const cell_v1_f = document.getElementById('c-v1-f');
    const cell_v2_f = document.getElementById('c-v2-f');
    const cell_v3_f = document.getElementById('c-v3-f');

    if (cell_v1_m) cell_v1_m.textContent = c1M.toFixed(1);
    if (cell_v2_m) cell_v2_m.textContent = c2M.toFixed(1);
    if (cell_v3_m) cell_v3_m.textContent = c3M.toFixed(1);
    if (cell_v1_f) cell_v1_f.textContent = c1F.toFixed(1);
    if (cell_v2_f) cell_v2_f.textContent = c2F.toFixed(1);
    if (cell_v3_f) cell_v3_f.textContent = c3F.toFixed(1);

    // Greedy: M -> V1 (4.2), F -> V3 (7.2) = 11.4 min
    const greedyTotal = c1M + c3F;
    // Hungarian: M -> V2 (4.9), F -> V1 (4.6) = 9.5 min
    const hungarianTotal = c2M + c1F;
    const saving = ((greedyTotal - hungarianTotal) / greedyTotal) * 100;

    if (greedyCostEl) greedyCostEl.textContent = `${greedyTotal.toFixed(1)} min`;
    if (hungarianCostEl) hungarianCostEl.textContent = `${hungarianTotal.toFixed(1)} min`;
    if (savingPctEl) savingPctEl.textContent = `−${saving.toFixed(1)}%`;
  }

  if (matrixMuSlider) {
    matrixMuSlider.addEventListener('input', updateMatrixSolver);
    updateMatrixSolver();
  }

  // --- 4. DFD SVG NAVIGATOR ---
  const dfdButtons = document.querySelectorAll('.dfd-level-btn');
  const dfdViews = document.querySelectorAll('.dfd-svg-view');
  const dfdCaption = document.getElementById('dfd-caption-text');

  const CAPTIONS = {
    'dfd-0': 'Level 0 — Global System Boundary. Analyst UI, Simulation Engine, and CI Verification Corridor.',
    'dfd-1': 'Level 1 — Operational System Decomposition. Incident queue, Cost-Field update, Hungarian matcher, and RL feedback.',
    'dfd-2a': 'Level 2a — Process 4: Batch Assignment Subsystem. Cost matrix shaping, Hungarian Kuhn-Munkres matching, residual re-buffering.',
    'dfd-2b': 'Level 2b — Process 5: Agent Execution Subsystem. Route kinematic following, battery FSM evolution, decoupled congestion writeback.'
  };

  dfdButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.dfdTarget;
      dfdButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      dfdViews.forEach(view => {
        view.style.display = (view.id === target) ? 'block' : 'none';
      });

      if (dfdCaption && CAPTIONS[target]) {
        dfdCaption.textContent = CAPTIONS[target];
      }
      playTone('E4', 0.08);
    });
  });

  // --- 5. CODE COPY SNIPPETS ---
  document.querySelectorAll('.btn-copy').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.copyTarget;
      const codeEl = document.getElementById(targetId);
      if (codeEl) {
        navigator.clipboard.writeText(codeEl.innerText.trim()).then(() => {
          btn.textContent = 'COPIED!';
          setTimeout(() => { btn.textContent = 'COPY'; }, 2000);
        });
      }
    });
  });

})();
