# DIRECTIVE — aethergrid-editorial-presentation

## 0 ROUTING / ANCESTORS / LOAD LIST
- concept: Kinetic Editorial Presentation — Monumental floating typography and continuous 3D camera trajectory where information directly manifests on scroll, stripping away all chunky box cards and terminal emulators in favor of an academic keynote presentation.
- routing per element: STRICT (Pure scroll-driven typography reveals, frameless media exhibition stages, continuous 3D spline camera flight, direct numeric milestones)
- ancestors (≤3, separate jobs):
  - awwwards-winner-14-com → COMPOSITION (12-column asymmetric editorial layout, monumental display typography, borderless media bleeds)
  - hellomonday-com → MOTION (Line-mask reveals, scrubbed text opacities, velocity transitions)
  - awwwards-winner-33-com → TOKEN (Refined architectural finish, crisp typography, clean ivory canvas)
- SIGNATURE MOVE: Direct Scroll-Manifest Engine — Information directly emerges on scroll without chunky container cards, paired with a borderless proof-of-work stage and synchronized 3D camera waypoints.
- SKILLS TO LOAD: 3d-web-experience, art-direction-editorial, gsap-core, threejs-fundamentals
- R&D FLAGS: Stylization ladder L2 (clean procedural 3D urban topology, animated routing beams, frameless screenshot stage)

## COORDINATE & LAYER TOPOLOGY
- Canvas layer: z-index 0 | pointer-events none (flight mode) / pointer-events auto (tactical orbit mode)
- Content layer: z-index 10 | pointer-events none (containers) / pointer-events auto (buttons, interactive pills, upload triggers)
- Ambient HUD/Marginalia: z-index 20 | pointer-events none (status tickers) / pointer-events auto (waypoint pill dock, sound toggle, orbit toggle)
- Modal / Fullscreen Lightbox: z-index 50 | pointer-events auto

## SCENE 1 — PHASE 1 THRESHOLD (Act I: Threshold / Overture)
- act role: THRESHOLD
- pin spine: pin length 140vh | pinSpacing true | anticipatePin 1
- rest state: camera pos [0, 460, 500], lookAt [0, 0, 0], fov 45deg, title y 110%, subtitle opacity 0.0, stats y 40px, opacity 0.0
- entry: title y 110% -> 0%, opacity 0.0 -> 1.0, expo.out, duration 1.15s, stagger 0.08s, badge scale 0.85 -> 1.00 duration 0.70s
- scrub: camera pos [0, 460, 500] -> [110, 270, 290], lookAt [0, 0, 0] -> [20, -10, 10], progress 0.0 to 1.0, scrub smoothing 1.20s
- hover/pointer: quickTo target tilt max 3.5deg, mouse lerp 0.06, button scale 1.03 spring stiffness 220 damping 24
- exit/handoff: title opacity 1.0 -> 0.0, y 0% -> -30%, power3.in, duration 0.85s
- type hierarchy: display Space Grotesk clamp(3.2rem, 7.5vw, 6.6rem) leading 0.94, body Plus Jakarta Sans 1.1rem, micro JetBrains Mono 10px tracking 0.24em
- palette role: background #FCFCF9, ink #0A1128, accent #FF4400 (Solar Flame)
- degrade <768px: static unpinned flow, min-height 100vh, canvas dpr 1.0 clamped, camera fixed at [0, 400, 450]
- reduced-motion: static final state, progress 1.0, pins killed, opacity 1.0, camera fixed at [110, 270, 290]

## SCENE 2 — DUAL GRAPH ENGINE & TOPOLOGY (Act II: Spatial Shift / Exposition)
- act role: EXPOSITION
- pin spine: pin length 160vh | pinSpacing true | anticipatePin 1
- rest state: camera pos [110, 270, 290], lookAt [20, -10, 10], fov 45deg, headline y 80px, metrics opacity 0.0, col 1-8 text, col 9-12 media stage
- entry: headline y 80px -> 0px, opacity 0.0 -> 1.0, duration 1.30s power4.out, numeric counters 0 -> 18912 nodes and 0 -> 24164 edges duration 1.40s
- scrub: camera dives into street canyon pos [110, 270, 290] -> [-55, 75, 95], lookAt [10, 15, -25], fov 45deg -> 52deg, progress 0.0 to 1.0, scrub smoothing 1.40s
- hover/pointer: interactive highway friction chips hover scale 1.08 spring stiffness 240 damping 22
- exit/handoff: headline y 0% -> -40% opacity 1.0 -> 0.0, camera transition power3.in duration 0.90s
- type hierarchy: display Space Grotesk clamp(2.6rem, 5.5vw, 4.8rem), body Plus Jakarta Sans 1.05rem, micro JetBrains Mono 10px tracking 0.22em
- palette role: background #FAF9F6, ink #0A1128, accent #0047FF (Electric Azure)
- degrade <768px: vertical single column stack, 100% width, camera idle canyon orbit radius 120px, touch scroll native
- reduced-motion: progress 1.0, static metric display, no camera dive, pins deactivated, duration 0.0s, opacity 1.0

## SCENE 3 — ALGORITHM SHOOTOUT & SEARCH ENVELOPES (Act III: The Climax / Core Phenomenon)
- act role: CLIMAX
- pin spine: pin length 180vh | pinSpacing true | anticipatePin 1
- rest state: camera pos [-55, 75, 95], lookAt [10, 15, -25], fov 52deg, headline y 80px, comparison matrix opacity 0.0, col 1-12
- entry: 4 wavefront beams ignite simultaneously, speed 2.00 units/s, duration 1.60s expo.out, metrics cascade y 40px -> 0px duration 0.80s, stagger 0.08s
- scrub: camera pans to tactical isometric vantage pos [-55, 75, 95] -> [150, 190, 175], lookAt [0, 10, 0], fov 52deg -> 40deg, progress 0.0 to 1.0, scrub smoothing 1.50s
- hover/pointer: algorithm switcher button click switches active 3D path beam, camera lerp 0.08, pulse intensity boost 2.00
- exit/handoff: wavefronts resolve into finished gold path line, unselected paths fade opacity 1.0 -> 0.15, transition duration 1.00s
- type hierarchy: display Space Grotesk clamp(2.8rem, 6.0vw, 5.2rem), body Plus Jakarta Sans 1.05rem, micro JetBrains Mono 10px tracking 0.24em
- palette role: background #FCFCF9, ink #0A1128, accent #00B37E (Emerald Optimal)
- degrade <768px: vertical stacked comparison, camera locked at isometric [130, 180, 160], fov 45deg, no scrubbed wavefronts
- reduced-motion: static benchmark matrix, completed paths pre-drawn 100%, camera stationary, opacity 1.0, duration 0.0s

## SCENE 4 — DYNAMIC PRICING & WEATHER SPINES (Act IV: Deceleration / Deep Inspection)
- act role: DECELERATION
- pin spine: pin length 160vh | pinSpacing true | anticipatePin 1
- rest state: camera pos [150, 190, 175], lookAt [0, 10, 0], fov 40deg, formula banner y 50px, terms opacity 0.0, col 1-12
- entry: master formula sweeps in y 50px -> 0px, duration 1.10s expo.out, term callouts cascade duration 0.70s, stagger 0.07s
- scrub: camera slides along priority snow spine pos [150, 190, 175] -> [-130, 140, 75], lookAt [-35, 10, -15], fov 40deg -> 44deg, progress 0.0 to 1.0, scrub smoothing 1.30s
- hover/pointer: formula term chips hover triggers 3D corridor highlight, spring stiffness 250 damping 25, lerp 0.07
- exit/handoff: formula chips dissolve opacity 1.0 -> 0.0, weather particle velocity dampens 2.40 to 0.50 units/s, camera pull-up duration 1.10s
- type hierarchy: display Space Grotesk clamp(2.6rem, 5.2vw, 4.4rem), body Plus Jakarta Sans 1.0rem, micro JetBrains Mono 10px tracking 0.22em
- palette role: background #F8F7F4, ink #0A1128, accent #FF4400 (Solar Flame)
- degrade <768px: vertical stack formula breakdown, static 3D hazard indicator radius 40px, camera at [-110, 150, 80], fov 45deg
- reduced-motion: static formula breakdown, zero particle velocity 0.0, camera stationary, opacity 1.0, duration 0.0s

## SCENE 5 — TEST VERIFICATION & PROOF OF WORK (Act V: Resolution / Kinetic Closure)
- act role: CLOSURE
- pin spine: pin length 150vh | pinSpacing true | anticipatePin 1
- rest state: camera pos [-130, 140, 75], lookAt [-35, 10, -15], fov 44deg, checklist y 60px, screenshot stage opacity 0.0, col 1-12
- entry: verification proofs reveal clip-path inset(10% 10% 10% 10%) -> inset(0% 0% 0% 0%), duration 1.20s power4.out, stats stagger 0.10s
- scrub: camera rises to global observation deck pos [-130, 140, 75] -> [0, 340, 400], lookAt [0, 0, 0], fov 44deg -> 46deg, progress 0.0 to 1.0, scrub smoothing 1.40s
- hover/pointer: screenshot stage click opens full-screen high-res lightbox inspector, button magnetic pull bounds 16px spring stiffness 260 damping 22
- exit/handoff: final Phase 1 milestone stamp and authors signature reveal, camera enters slow gentle cinematic drift speed 0.04 rad/s, opacity 1.0
- type hierarchy: display Space Grotesk clamp(2.8rem, 6.0vw, 5.0rem), body Plus Jakarta Sans 1.05rem, micro JetBrains Mono 11px tracking 0.26em
- palette role: background #FCFCF9, ink #0A1128, accent #0047FF (Electric Azure) & #00B37E (Emerald Optimal)
- degrade <768px: single column responsive layout, direct image display width 100%, full width buttons, camera locked high angle [0, 360, 420]
- reduced-motion: static high-res screenshot view, no zoom animation, camera stationary at [0, 340, 400], opacity 1.0, duration 0.0s

## GLOBAL ARCHITECTURE
- Lenis config: duration 1.15s, easing (t => Math.min(1, 1.001 - Math.pow(2, -10 * t))), smoothTouch false
- Lenis ticker integration: named callback tick = (t) => lenis.raf(t * 1000); gsap.ticker.add(tick); gsap.ticker.lagSmoothing(0)
- Grain implementation: subtle CSS SVG static noise overlay opacity 0.015, pointer-events none (NO live SVG feTurbulence)
- WebGL Context Budget: exactly 1 Canvas instance; dpr clamped Math.min(window.devicePixelRatio, 1.5); graceful WebGL fallback
- Audio synthesis: Web Audio API tactile audio engine (520Hz tick for step clicks 18ms decay, 840Hz crystal chime for waypoint lock 140ms decay, zero external assets)
- Font substitutions: Google Fonts Space Grotesk (display), Plus Jakarta Sans (body), JetBrains Mono (code/metrics)
- Copy voice: rigorous, academic presentation posture, zero buzzwords
- Ambient layers: cursor lerp 0.08, magnetic pull bounds 16px, dynamic 3D spline camera coordinate HUD updating in real-time
