# DIRECTIVE — AetherGrid Song Dynasty Light Editorial UI

## 0 ROUTING / ANCESTORS / LOAD LIST
- concept: Song Dynasty Cartographic Minimalist Mission Control (华夏宋韵与现代空间图论交互界面)
- routing per element:
  - Header & Masthead: STRICT (Editorial Masthead, Celadon Jade & Vermilion Seal)
  - Interactive Tool Dock: SYNTHESIS (Minimalist Segmented Control Pill with SVG Vector Icons)
  - Telemetry Sidebar: STRICT (Numbered 01–06 Sections, Hairline Grids, Monospace Matrix)
  - HazMat & Severed Advisories: MICRO (Architectural Vermilion / Amber Seal Badges)
- ancestors:
  - awwwards-winner-14-com → TOKEN: Ink/Parchment/Gold palette, line-mask reveal, hairline borders (1px at 10% ink)
  - awwwards-winner-33-com → COMPOSITION: Asymmetric 12-col layout, high-contrast serif headlines, micro-type (10px uppercase tracking 0.25em)
  - standalone-chinese-heritage → MOTION: Celadon (#2F5B46) and Cinnabar (#B33927) lacquer accents, subtle silk grain, calligraphic restraint
- SIGNATURE MOVE: Pure light Xuan-paper & Song celadon aesthetic for high-throughput urban mission control with ZERO tacky emojis (100% SVG line glyphs and Chinese seal markers).
- SKILLS TO LOAD: art-direction-editorial, design-library
- R&D FLAGS: L2 stylized cartographic SVG & Leaflet light-canvas styling

## COORDINATE & LAYER TOPOLOGY
- Canvas/Map layer: z-index (z-10) | pointer-events (auto)
- Weather particle canvas: z-index (z-20) | pointer-events (none)
- Interactive Floating Tool Dock: z-index (z-50) | pointer-events (auto)
- Floating Advisory Banners (HazMat / Severance): z-index (z-55) | pointer-events (auto)
- Editorial Telemetry Sidebar: z-index (z-40) | pointer-events (auto)
- Global Masthead Bar: z-index (z-60) | pointer-events (auto)

## DESIGN TOKENS (LIGHT CHINESE SONG DYNASTY PALETTE)
- Base Xuan Paper (宣纸底色): #F9F7F1
- Porcelain Card (白瓷卡片): #FFFFFF
- Deep Mist Wash (淡墨底): #F2EEE5
- Hairline Border (竹节细线): rgba(32, 36, 33, 0.09)
- Pine-Soot Ink (松烟浓墨 - Headings): #1C1F1D
- Washed Ink (淡墨 - Body): #585E5A
- Fine Mist (烟岚 - Micro-type): #8A928C
- Celadon Jade (龙泉青瓷 - Optimal Route & Accents): #2F5B46
- Celadon Tint: rgba(47, 91, 70, 0.08)
- Imperial Cinnabar (朱砂红 - Closure & Emergency): #B33927
- Cinnabar Tint: rgba(179, 57, 39, 0.08)
- Imperial Amber / Ochre (赭石金 - Warnings & Congestion): #B38024
- Amber Tint: rgba(179, 128, 36, 0.08)
- Typography:
  - Display Headline: Cinzel / Cormorant Garamond, serif, letter-spacing: 0.04em
  - Body & Labels: Plus Jakarta Sans / Inter, sans-serif
  - Telemetry & Numbers: JetBrains Mono, monospace, tracking: -0.02em
  - Micro-indices: 10px, uppercase, letter-spacing: 0.22em, font-weight: 700

## GLOBAL ARCHITECTURE & REPLACEMENTS
- Elimination of all emojis:
  - 🚑 replaced with SVG Emergency Cross / Directional Chevron
  - ☣️ replaced with SVG Geometric Biohazard Glyph
  - 🦺 replaced with SVG Tactical Shield / Armor Icon
  - ⚡ replaced with SVG Pulse Ray / Speed Metric Icon
  - ⚠️ replaced with SVG Triangle Alert Glyph
  - 🚫 replaced with SVG Barrier Cross
  - ☀️ 🌧️ ❄️ 🌫️ replaced with clean minimal atmospheric SVG icons
