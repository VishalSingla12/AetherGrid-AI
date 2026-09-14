# DIRECTIVE — AetherGrid AI GitHub Pages
COMPLETENESS RULE: Zero blank slots. If a slot uses art-direction default,
explicitly write "→ AD default". Numbers everywhere: deg, vh, %, s, stiffness/damping.
NUMERIC DENSITY RULE: Floor >= 12 numeric tokens per scene (deg|vh|%|s|stiffness|damping|lerp).

## 0 ROUTING / ANCESTORS / LOAD LIST
- concept: "Cartographic Dispatch — A Living Map Unfolds." The page opens as a folded transit
  map that progressively unfolds through scroll, revealing the system's layers — graph topology,
  pathfinding wavefronts, weather overlays, and invariant gates — as if the viewer is unfolding
  a paper city. Each section is a "panel" of the map, connected by transit-line visual connectors.
  Narrative thesis: The city breathes through data, and AetherGrid is the nervous system.
- routing per element:
  - Hero headline + unfold animation: STRICT (klim-co-nz line-mask-reveal + velocity-skew)
  - Section transitions: SYNTHESIS (clip-wipe from #61 + scroll-progress-bar from brief)
  - Metric counters: STRICT (counter-increment from brief kinematics)
  - Micro-label system: STRICT (awwwards-winner-84-com editorial micro-type)
  - Ambient grain: static 48×48px WebP tile, opacity 4%, pointer-events: none, composited on ::after
  - Magnetic buttons: spring stiffness: 200, damping: 25, max displacement: 12px, cursor-follow lerp: 0.08
  - Typography pairing: SYNTHESIS (Cinzel from Song Dynasty palette + Plus Jakarta Sans body)
- ancestors (3, separate jobs):
  - klim-co-nz → MOTION → velocity-skew on scroll, pinned-horizontal gallery, line-mask-reveal entrance choreography
  - awwwards-winner-84-com → COMPOSITION → 12-col asymmetric grid, editorial micro-type labels, headline cols 1-9 bleeding right
  - awwwards-winner-61-com → TOKEN → grain overlay 4% opacity, clip-wipe transitions, magnetic CTA spring behavior
- SIGNATURE MOVE: "Transit-Line Scene Connectors" — between each scene, a horizontal SVG transit line
  (stroke-dashoffset animated on scroll via scrub: 1) connects the bottom of one section to the top
  of the next, with a pulsing "station dot" at each junction. The line color inherits the accent of
  the departing section (celadon-jade → cinnabar-red → amber-gold) and transitions via stroke
  gradient. No other build has used this continuous transit-line threading mechanic.
- SKILLS TO LOAD: gsap-core, gsap-plugins (ScrollTrigger only), gsap-performance, art-direction-editorial
- R&D FLAGS: None. Pure CSS + GSAP + vanilla JS. No WebGL canvas, no React, no Three.js. L0 (no 3D ladder).

## COORDINATE & LAYER TOPOLOGY
- Canvas layer: NOT USED (no WebGL). z-index: N/A.
- Content layer: z-index: z-10 | pointer-events: auto
- Ambient HUD/Marginalia: z-index: z-20 | pointer-events: none (section index labels "01/", "02/", etc.)
- Transit-line SVG overlay: z-index: z-5 | pointer-events: none
- Modal / Fullscreen Cursor: z-index: z-50 | pointer-events: auto (magnetic CTA hover state)

## SCENE 1 — THRESHOLD: The Folded Map (Act I)
- act role: THRESHOLD
- pin spine: pin length 120vh | pinSpacing true | anticipatePin 1
- rest state: Hero headline "AETHERGRID" set at rotateZ(-2deg), translateY(15vh), opacity 0.
  Subtitle "Autonomous Logistics & Emergency Dispatch" at rotateZ(1.5deg), translateY(20vh).
  A decorative SVG grid pattern (representing city blocks) fills the background at opacity 0.06,
  scale(1.15). Layout: headline cols 1-8 of 12-col grid, right bleed reserved for a floating
  "map fold" crease line at col 10-12.
- entry: headline line-mask-reveal y: 110% → 0%, easing: expo.out, duration: 1.1s, stagger: 0.09s.
  Subtitle fades translateY: 30px → 0px, opacity: 0 → 1, easing: power4.out, duration: 0.8s, delay: 0.4s.
  Background grid pattern scale: 1.15 → 1.0, opacity: 0.06 → 0.1, easing: expo.out, duration: 1.4s.
- scrub: On pin scroll (0.0 → 1.0): hero block translateY: 0% → -8vh, background grid translateY: 0 → -12vh
  (parallax separation 4vh), scrub smoothing: 1.2s. Crease line opacity: 0.3 → 0, scaleX: 1 → 0.
- hover/pointer: → AD default (magnetic CTAs, cursor-follow lerp: 0.08)
- exit/handoff: clip-wipe from bottom (clip-path inset: 0 0 0% 0 → 0 0 100% 0), duration: 0.6s via scrub
- type hierarchy: Display Cinzel 700 clamp(3.2rem, 8vw, 7rem) leading 0.92 tracking -0.02em.
  Subtitle Plus Jakarta Sans 400 clamp(0.9rem, 1.4vw, 1.1rem) leading 1.5. Micro: 10px uppercase 0.25em spacing 55% opacity.
- palette role: background #F9F7F1 (Xuan Paper), ink #1A1A1A (near-black), accent #2F5B46 (Celadon Jade)
- degrade <768px: pin killed via gsap.matchMedia("(max-width: 767px)"). Headline font-size: 2.5rem.
  Subtitle stacks below. Grid pattern hidden. Single-column flow. overflow-x: hidden.
- reduced-motion: all elements at final state (progress: 1), pins killed, opacity: 1, transforms: none.

## SCENE 2 — EXPOSITION: The Graph Awakens (Act II)
- act role: EXPOSITION
- pin spine: pin length 200vh | pinSpacing true | anticipatePin 1
- rest state: Left column (cols 1-5): stacked stat cards, each rotateZ alternating ±1.5deg,
  translateX(-8%), opacity 0. Right column (cols 7-12): large infographic panel showing graph
  topology stats (18,912 nodes / 24,164 edges / 4 algorithms) at scale(0.95), opacity 0.
  Section label "01/ GRAPH ENGINE" at top-left as micro-type.
- entry: stat cards stagger-reveal from left: translateX: -8% → 0%, rotateZ: ±1.5deg → 0deg,
  opacity: 0 → 1, easing: expo.out, duration: 0.9s, stagger: 0.12s. Infographic panel
  scale: 0.95 → 1.0, opacity: 0 → 1, easing: power4.out, duration: 1.0s, delay: 0.3s.
- scrub: On pin (0.0 → 0.5): counter-increment animation on stat numbers (0 → 18912, 0 → 24164,
  0 → 4). Format: toLocaleString(). Duration mapped to scrub range. On pin (0.5 → 1.0):
  stat cards translateY: 0 → -4vh, parallax offset 2vh between cards, scrub: 1.5s.
- hover/pointer: stat cards scale on hover: 1.0 → 1.02 via spring stiffness: 200, damping: 25.
  quickTo on translateX for magnetic drift: 6px max.
- exit/handoff: opacity dissolve 0.4s as next scene overlaps from below (translateY: 100vh → 0vh
  on next scene entry)
- type hierarchy: Display Cinzel 600 clamp(2rem, 4vw, 3.5rem). Stat numbers JetBrains Mono 700
  clamp(2.5rem, 5vw, 4rem). Body Plus Jakarta Sans 400 1rem/1.6. Micro-label: 10px uppercase 0.25em 55%.
- palette role: background #FFFFFF (Porcelain Card), ink #1A1A1A, accent #2F5B46 (Celadon Jade)
- degrade <768px: pin killed. Cards stack vertically. Counter animation fires on scroll-enter
  (threshold: 0.3). Infographic panel full-width. overflow-x: hidden.
- reduced-motion: counters display final values. Cards at final position. opacity: 1.

## SCENE 3 — CLIMAX: Pathfinding Wavefront (Act III)
- act role: CLIMAX
- pin spine: pin length 250vh | pinSpacing true | anticipatePin 1
- rest state: Full-width section. Center: a CSS-grid "algorithm comparison" panel showing 3 columns
  (Dynamic A* / Bidirectional A* / Dijkstra) at scale(0.9), translateY(5vh), opacity 0.
  Each column has a vertical "wavefront bar" (div gradient from celadon → transparent) at height: 0%.
  Background: SVG topographic contour lines at 3% opacity, stroke-width: 0.5px, translateY(10vh).
- entry: Panel scale: 0.9 → 1.0, translateY: 5vh → 0, opacity: 0 → 1, easing: expo.out, duration: 1.2s.
  Column headers line-mask-reveal stagger: 0.15s. Contour lines translateY: 10vh → 0, duration: 1.8s.
- scrub: On pin (0.0 → 0.4): wavefront bars height: 0% → 100% (representing search space coverage),
  stagger 0.2s between columns. Bar 2 (Bidirectional) stops at 21.3% height (78.7% pruning stat).
  On pin (0.4 → 0.7): metric callouts fade in — "78.7% search space pruned", "0 admissibility violations",
  "93.7% path divergence in snow" — each with counter-increment and line-mask-reveal, stagger: 0.12s.
  On pin (0.7 → 1.0): columns translateX to compact formation, scrub: 1.5s.
- hover/pointer: algorithm columns scale: 1.0 → 1.03 on hover, spring stiffness: 250, damping: 22.
  Metric callouts cursor-follow with lerp: 0.06.
- exit/handoff: clip-wipe diagonal (clip-path polygon) from bottom-left to top-right, duration via scrub 0.5s.
- type hierarchy: Display Cinzel 700 clamp(2.5rem, 5vw, 4.5rem). Metric numbers JetBrains Mono 800
  clamp(3rem, 6vw, 5rem) with cinnabar-red color. Body Plus Jakarta Sans 400 0.95rem/1.5.
  Micro-label: 10px uppercase 0.25em 55%.
- palette role: background #F2EEE5 (Deep Mist), ink #1A1A1A, accent #B33927 (Imperial Cinnabar)
- degrade <768px: pin killed. Columns stack vertically. Wavefront bars animate on scroll-enter.
  Contour SVG hidden. overflow-x: hidden.
- reduced-motion: wavefront bars at final height. Metrics visible. opacity: 1. transforms: none.

## SCENE 4 — DECELERATION: Invariant Observatory (Act IV)
- act role: DECELERATION
- pin spine: pin length 180vh | pinSpacing true | anticipatePin 1
- rest state: 6 invariant cards (I1–I6) arranged in 3×2 grid, each at rotateZ alternating ±2deg,
  scale(0.92), opacity 0. Each card has: code name (I1: Closure Safety), status badge ("PROVEN" /
  "SPECIFIED"), and a 1-line description. Left margin: vertical micro-label "SYSTEM INVARIANTS".
  Bottom: a horizontal scroll marquee with "2,462 TRIALS · 0 VIOLATIONS · 85.9% VARIANCE REDUCTION"
  repeating, at opacity 0.
- entry: Cards stagger-reveal: scale: 0.92 → 1.0, rotateZ: ±2deg → 0deg, opacity: 0 → 1,
  easing: expo.out, duration: 0.8s, stagger: 0.1s. Marquee fades in opacity: 0 → 1 after 0.6s delay,
  then begins translateX animation at 40px/s continuous.
- scrub: On pin (0.0 → 0.6): cards translateY: 0 → -3vh with 1.5vh parallax offset between rows,
  scrub: 1.2s. On pin (0.6 → 1.0): cards that are "SPECIFIED" (not yet implemented) dim to 40% opacity,
  while "PROVEN" cards gain a 1px celadon-jade border-left, scrub: 0.8s.
- hover/pointer: cards magnetic tilt via quickTo: rotateX ±4deg, rotateY ±4deg based on pointer position.
  Spring stiffness: 180, damping: 20. Max displacement: 8px.
- exit/handoff: opacity dissolve 0.5s, marquee continues running beneath next scene entry.
- type hierarchy: Card title Cinzel 600 1.1rem. Status badge JetBrains Mono 700 0.7rem uppercase with
  2px border-radius, padding 2px 8px. Description Plus Jakarta Sans 400 0.85rem/1.4.
  Marquee: JetBrains Mono 600 clamp(0.7rem, 1vw, 0.9rem) uppercase 0.15em spacing.
- palette role: background #F9F7F1 (Xuan Paper), ink #1A1A1A, accent #B38024 (Imperial Amber)
- degrade <768px: pin killed. Cards stack in single column. Marquee full-width at smaller font.
  Magnetic tilt disabled. overflow-x: hidden.
- reduced-motion: cards at final position with borders applied. Marquee static. opacity: 1.

## SCENE 5 — CLOSURE: Dispatch Terminal (Act V)
- act role: CLOSURE
- pin spine: pin length 100vh | pinSpacing true | anticipatePin 1
- rest state: Split layout. Left (cols 1-6): Project credits — authors, course, institution —
  styled as a "dispatch manifest" with micro-type labels. Right (cols 7-12): 3 placeholder link
  cards ("Documentation", "Presentation", "Live Demo") stacked vertically at translateX(15%),
  opacity 0. Footer bar at bottom with GitHub link and "UCS503P · Thapar Institute" micro-label.
- entry: Manifest text line-mask-reveal y: 110% → 0%, easing: expo.out, duration: 0.9s, stagger: 0.08s.
  Link cards slide-in translateX: 15% → 0%, opacity: 0 → 1, easing: power4.out, duration: 0.7s,
  stagger: 0.15s, delay: 0.3s.
- scrub: On pin (0.0 → 1.0): gentle parallax — manifest translateY: 0 → -3vh, cards translateY: 0 → -1.5vh,
  scrub: 1.0s. Transit-line from Scene 4 completes its final segment into the footer station dot.
- hover/pointer: link cards magnetic pull (spring stiffness: 220, damping: 24, max displacement: 12px).
  GitHub icon rotateZ: 0 → 360deg on hover, duration: 0.6s, easing: expo.out.
- exit/handoff: N/A (final scene). Footer remains in normal flow.
- type hierarchy: Author names Cinzel 600 clamp(1.2rem, 2vw, 1.8rem). Course info Plus Jakarta Sans 400
  0.85rem/1.4. Link card titles Cinzel 500 1rem. Link card descriptions Plus Jakarta Sans 300 0.8rem.
  Footer micro: JetBrains Mono 400 0.7rem uppercase 0.2em spacing 45% opacity.
- palette role: background #FFFFFF (Porcelain Card), ink #1A1A1A, accent #2F5B46 (Celadon Jade)
- degrade <768px: pin killed. Single column: manifest on top, link cards below full-width.
  Footer stacks centered. overflow-x: hidden.
- reduced-motion: all elements visible at final position. opacity: 1. transforms: none.

## GLOBAL ARCHITECTURE
- Lenis config: duration: 1.2, easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)), smoothTouch: false
- Lenis ticker integration: gsap.ticker.add callback, lagSmoothing(0)
- Grain implementation: static repeating WebP tile (48×48px, 4% opacity) via CSS background-image on ::after
  pseudo-element. Composited via pointer-events: none. NO live SVG feTurbulence.
- WebGL Context Budget: 0 canvases. No WebGL. Pure CSS + GSAP + SVG.
- Audio synthesis: → AD default (disabled — no audio for academic project page)
- Font substitutions: Cinzel (Google Fonts) → fallback Georgia, "Times New Roman", serif.
  Plus Jakarta Sans (Google Fonts) → fallback -apple-system, "Segoe UI", sans-serif.
  JetBrains Mono (Google Fonts) → fallback "SF Mono", "Cascadia Code", monospace.
- Copy voice: Technical-observational. Clinical precision with quiet confidence. No marketing
  hyperbole. Data speaks. Banned words: "elevate, unlock, seamless, delve, embark, timeless,
  unforgettable, where X meets Y".
- Ambient layers: cursor lerp: 0.08 (magnetic CTAs only), velocity skew max: 4deg (on scroll via
  Lenis velocity), magnetic pull bounds: 12px max displacement.
- Transit-line SVG: stroke-width: 2px, stroke-dasharray: 8 4, animated via stroke-dashoffset scrubbed
  to ScrollTrigger progress. Color transitions: #2F5B46 → #B33927 → #B38024 via SVG linearGradient stops.
  Station dots: 8px circles with 2px stroke, filled on scroll arrival.
