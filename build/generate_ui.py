import os

html_content = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light">
  <meta name="darkreader-lock" content="true">
  <title>AetherGrid AI — Autonomous Urban Dispatch Mission Control</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Syne:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <style>
    :root {
      color-scheme: light only;
      supported-color-schemes: light;
      
      /* Harmonious Muted Vellum & Alabaster Foundation (Slightly Darker, Zero Glare) */
      --bg-base: #EAE7E0;
      --bg-surface: #EFECE5;
      --bg-surface-soft: #E4E0D6;
      --bg-surface-alt: #D9D4C9;
      
      --border-hairline: rgba(26, 30, 27, 0.08);
      --border-subtle: rgba(26, 30, 27, 0.14);
      --border-strong: rgba(26, 30, 27, 0.22);
      
      --ink-black: #151816;
      --ink-deep: #282E2A;
      --ink-washed: #545E58;
      --ink-muted: #808D85;
      --ink-faint: #B0B8B2;
      
      --celadon-jade: #245A44;
      --celadon-light: #34765C;
      --celadon-wash: #EBF4EF;
      --celadon-border: rgba(36, 90, 68, 0.22);
      
      --cinnabar-red: #B33423;
      --cinnabar-light: #D14532;
      --cinnabar-wash: #FAF0EE;
      --cinnabar-border: rgba(179, 52, 35, 0.22);
      
      --amber-gold: #B37B1B;
      --amber-light: #D49320;
      --amber-wash: #FAF3E6;
      --amber-border: rgba(179, 123, 27, 0.22);
      
      --dijkstra-slate: #5C6761;
      --dijkstra-wash: #EFF3F1;
      
      --font-logo: 'Cinzel', serif;
      --font-display: 'Syne', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      
      --shadow-sm: 0 1px 3px rgba(22, 25, 23, 0.04), 0 1px 2px rgba(22, 25, 23, 0.02);
      --shadow-md: 0 4px 16px rgba(22, 25, 23, 0.06), 0 1px 4px rgba(22, 25, 23, 0.03);
      --shadow-lg: 0 12px 36px rgba(22, 25, 23, 0.09), 0 2px 8px rgba(22, 25, 23, 0.04);
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { width: 100%; height: 100%; overflow: hidden; background: var(--bg-base); background-color: var(--bg-base) !important; color: var(--ink-deep); font-family: var(--font-sans); -webkit-font-smoothing: antialiased; color-scheme: light only; }
    
    #app-container { display: flex; flex-direction: column; width: 100vw; height: 100vh; position: relative; }
    
    /* Top Masthead */
    header.top-bar {
      height: 56px;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-hairline);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
      z-index: 1000;
      box-shadow: var(--shadow-sm);
      gap: 20px;
    }
    
    .brand-group {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
    }

    /* Centered Dropdowns Container with Generous Breathing Space */
    .header-dropdowns-center {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 18px;
      flex: 1;
    }

        /* Right Header Telemetry Pills */
    .header-telemetry-right {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-shrink: 0;
    }

    /* Mission Control Extending Tab (Below Spatial Toolset, Extends to Right on Hover) */
    .mission-control-dock {
      pointer-events: auto;
      display: flex;
      align-items: center;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      height: 40px;
      box-shadow: var(--shadow-md);
      transition: max-width 0.35s cubic-bezier(0.16, 1, 0.3, 1),
                  border-color 0.25s ease,
                  box-shadow 0.25s ease;
      overflow: hidden;
      width: max-content;
      max-width: 205px; /* Matches Spatial Toolset width in collapsed state */
      cursor: pointer;
      user-select: none;
    }

    /* Extended State on Hover or when Pinned Open */
    .mission-control-dock:hover,
    .mission-control-dock.pinned {
      max-width: 620px; /* Extends smoothly to the right over open map */
      border-color: var(--celadon-jade);
      box-shadow: 0 8px 24px -3px rgba(26, 30, 27, 0.14),
                  0 2px 6px -1px rgba(26, 30, 27, 0.08);
    }

    .mission-dock-handle {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 12px;
      height: 100%;
      width: 205px;
      box-sizing: border-box;
      flex-shrink: 0;
      font-family: var(--font-display);
      font-size: 10.5px;
      font-weight: 700;
      letter-spacing: 0.8px;
      color: var(--ink-deep);
      transition: color 0.2s ease;
    }

    .mission-control-dock:hover .mission-dock-handle,
    .mission-control-dock.pinned .mission-dock-handle {
      color: var(--celadon-jade);
    }

    .dock-handle-title {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .dock-pulse-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--celadon-jade);
      box-shadow: 0 0 6px rgba(36, 90, 68, 0.5);
      animation: tabPulse 2s infinite alternate;
    }

    .dock-chevron {
      color: var(--ink-muted);
      transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), color 0.2s;
    }

    .mission-control-dock:hover .dock-chevron,
    .mission-control-dock.pinned .dock-chevron {
      transform: rotate(90deg);
      color: var(--celadon-jade);
    }

    .dock-roller-divider {
      width: 1px;
      height: 22px;
      background: var(--border-subtle);
      margin: 0 6px 0 2px;
      flex-shrink: 0;
    }

    .mission-dock-flyout {
      display: flex;
      align-items: center;
      overflow: hidden;
      height: 100%;
      padding-right: 10px;
    }

    .mission-dock-actions {
      display: flex;
      align-items: center;
      gap: 7px;
      padding-left: 2px;
      white-space: nowrap;
    }

    /* Action Buttons inside Extended Dock */
    .dock-action-btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 5px;
      font-family: var(--font-sans);
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.16s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: var(--shadow-sm);
      border: 1px solid transparent;
      outline: none;
      white-space: nowrap;
    }

    .dock-action-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 3px 8px rgba(26, 30, 27, 0.1);
    }

    .dock-action-btn.btn-primary {
      background: var(--celadon-jade);
      color: #FFF;
      border-color: var(--celadon-jade);
      box-shadow: 0 2px 8px rgba(36, 90, 68, 0.25);
    }
    .dock-action-btn.btn-primary:hover {
      background: var(--celadon-light);
      border-color: var(--celadon-light);
      color: #FFF;
    }

    .dock-action-btn.btn-warning {
      background: var(--amber-wash);
      border-color: var(--amber-border);
      color: var(--amber-gold);
    }
    .dock-action-btn.btn-warning:hover {
      background: #F4E8D0;
      border-color: var(--amber-gold);
    }

    .dock-action-btn.btn-neutral {
      background: var(--bg-surface-soft);
      border-color: var(--border-subtle);
      color: var(--ink-deep);
    }
    .dock-action-btn.btn-neutral:hover {
      background: #DED9CE;
      border-color: var(--border-strong);
    }
    
    .brand-seal {
      width: 32px;
      height: 32px;
      background: var(--cinnabar-red);
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #FFF;
      font-family: var(--font-logo);
      font-weight: 800;
      font-size: 16px;
      letter-spacing: 0;
      box-shadow: 0 2px 8px rgba(181, 54, 37, 0.3);
      border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .brand-text-block {
      display: flex;
      flex-direction: column;
    }
    
    .brand-title {
      font-family: var(--font-logo);
      font-weight: 700;
      font-size: 15px;
      letter-spacing: 1.2px;
      color: var(--ink-black);
      line-height: 1.1;
    }
    
    .brand-subtitle {
      font-family: var(--font-mono);
      font-size: 9.5px;
      letter-spacing: 0.8px;
      color: var(--ink-muted);
      margin-top: 2px;
      font-weight: 600;
    }
    
    .header-pills-center {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    
    .system-pill {
      font-family: var(--font-mono);
      font-size: 10.5px;
      font-weight: 600;
      letter-spacing: 0.4px;
      color: var(--ink-washed);
      background: var(--bg-surface-soft);
      border: 1px solid var(--border-hairline);
      padding: 3px 9px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    
    .system-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--celadon-jade);
    }
    
    .nav-controls {
      display: flex;
      align-items: center;
      gap: 9px;
      flex-wrap: wrap;
    }
    
    .control-label {
      font-size: 10px;
      font-family: var(--font-mono);
      letter-spacing: 0.6px;
      color: var(--ink-muted);
      text-transform: uppercase;
      font-weight: 600;
    }
    
    /* Hidden native select for 100% API/DOM compatibility */
    select.select-input.select-hidden {
      position: absolute !important;
      opacity: 0 !important;
      pointer-events: none !important;
      width: 1px !important;
      height: 1px !important;
      overflow: hidden !important;
      clip: rect(0, 0, 0, 0) !important;
    }

    /* Classic Scroll Dropdown Components */
    .scroll-dropdown-wrap {
      position: relative;
      display: inline-flex;
      align-items: center;
      gap: 7px;
    }

    .scroll-dropdown-trigger {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      color: var(--ink-deep);
      padding: 5px 10px 5px 11px;
      border-radius: 5px;
      font-family: var(--font-sans);
      font-size: 11.5px;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 0 1px 2px rgba(26, 30, 27, 0.04);
      user-select: none;
      outline: none;
    }

    .scroll-dropdown-trigger:hover {
      border-color: var(--celadon-jade);
      background: #E8E5DC;
      color: var(--ink-black);
    }

    .scroll-dropdown-trigger.active {
      border-color: var(--celadon-jade);
      box-shadow: 0 0 0 2px var(--celadon-wash);
      background: #E5E1D6;
    }

    .scroll-dropdown-trigger .trigger-value {
      max-width: 175px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-weight: 600;
      letter-spacing: 0.2px;
    }

    .scroll-dropdown-trigger .scroll-indicator {
      display: inline-flex;
      align-items: center;
      color: var(--ink-muted);
      transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), color 0.2s;
    }

    .scroll-dropdown-trigger.active .scroll-indicator {
      transform: rotate(180deg);
      color: var(--celadon-jade);
    }

    /* Classic Unrolling Scroll Dropdown Panel */
    .scroll-dropdown-panel {
      position: absolute;
      top: calc(100% + 6px);
      left: 0;
      min-width: 250px;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 7px;
      box-shadow: 0 12px 32px -4px rgba(26, 30, 27, 0.14),
                  0 4px 10px -2px rgba(26, 30, 27, 0.06),
                  inset 0 1px 0 rgba(255, 255, 255, 0.5);
      z-index: 2000;
      overflow: hidden;
      
      /* Initial Rolled Up State */
      opacity: 0;
      visibility: hidden;
      pointer-events: none;
      transform-origin: top center;
      transform: perspective(800px) rotateX(-18deg) scaleY(0.35) translateY(-8px);
      transition: opacity 0.22s ease,
                  transform 0.35s cubic-bezier(0.22, 1, 0.36, 1),
                  visibility 0.35s;
    }

    /* Classic Decorative Roller Rib Caps */
    .scroll-roller-cap {
      height: 3px;
      width: 100%;
      background: linear-gradient(90deg, var(--border-hairline) 0%, var(--celadon-jade) 25%, var(--celadon-jade) 75%, var(--border-hairline) 100%);
      opacity: 0.85;
    }
    .scroll-roller-cap.bottom {
      height: 2px;
      background: linear-gradient(90deg, transparent 0%, var(--border-subtle) 30%, var(--border-subtle) 70%, transparent 100%);
      opacity: 0.6;
    }

    /* Unrolled State (Scroll Style Motion Drop) */
    .scroll-dropdown-panel.open {
      opacity: 1;
      visibility: visible;
      pointer-events: auto;
      transform: perspective(800px) rotateX(0deg) scaleY(1) translateY(0);
      animation: scrollUnroll 0.35s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    @keyframes scrollUnroll {
      0% {
        opacity: 0;
        transform: perspective(800px) rotateX(-22deg) scaleY(0.25) translateY(-10px);
      }
      60% {
        opacity: 1;
        transform: perspective(800px) rotateX(3deg) scaleY(1.02) translateY(0);
      }
      100% {
        opacity: 1;
        transform: perspective(800px) rotateX(0deg) scaleY(1) translateY(0);
      }
    }

    .scroll-menu-items {
      max-height: 270px;
      overflow-y: auto;
      padding: 6px;
      display: flex;
      flex-direction: column;
      gap: 2px;
      background: linear-gradient(to bottom, #F4F1E9 0%, #EFECE5 15px, #EFECE5 calc(100% - 15px), #ECE8DF 100%);
    }

    .scroll-menu-items::-webkit-scrollbar {
      width: 5px;
    }
    .scroll-menu-items::-webkit-scrollbar-track {
      background: rgba(26, 30, 27, 0.04);
    }
    .scroll-menu-items::-webkit-scrollbar-thumb {
      background: rgba(26, 30, 27, 0.20);
      border-radius: 3px;
    }
    .scroll-menu-items::-webkit-scrollbar-thumb:hover {
      background: var(--celadon-jade);
    }

    .scroll-menu-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 7px 11px;
      border-radius: 5px;
      font-size: 11.5px;
      color: var(--ink-deep);
      cursor: pointer;
      transition: all 0.16s cubic-bezier(0.16, 1, 0.3, 1);
      user-select: none;
      border: 1px solid transparent;
    }

    .scroll-menu-item:hover {
      background: #E5E0D5;
      color: var(--ink-black);
      border-color: var(--border-hairline);
      padding-left: 13px;
    }

    .scroll-menu-item.selected {
      background: var(--celadon-wash);
      color: var(--celadon-jade);
      font-weight: 600;
      border-color: var(--celadon-border);
    }

    .scroll-menu-item .item-lead {
      display: inline-flex;
      align-items: center;
      gap: 7px;
    }

    .scroll-menu-item .item-marker {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--celadon-jade);
      opacity: 0;
      transform: scale(0);
      transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    .scroll-menu-item.selected .item-marker {
      opacity: 1;
      transform: scale(1);
    }

    .scroll-menu-item .item-tag {
      font-size: 10px;
      font-family: var(--font-mono);
      color: var(--ink-muted);
      letter-spacing: 0.3px;
      margin-left: 10px;
    }
    
    button.btn-control {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      color: var(--ink-deep);
      padding: 5px 11px;
      border-radius: 5px;
      font-family: var(--font-sans);
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
      box-shadow: var(--shadow-sm);
    }
    button.btn-control:hover {
      background: var(--bg-surface-soft);
      border-color: var(--border-strong);
    }
    
    button.btn-primary {
      background: var(--celadon-jade);
      color: #FFF;
      border: 1px solid var(--celadon-jade);
      box-shadow: 0 2px 8px rgba(39, 92, 70, 0.25);
    }
    button.btn-primary:hover {
      background: var(--celadon-light);
      border-color: var(--celadon-light);
      box-shadow: 0 3px 12px rgba(39, 92, 70, 0.35);
      color: #FFF;
    }
    
    button.btn-warning {
      background: var(--amber-wash);
      border-color: var(--amber-border);
      color: var(--amber-gold);
    }
    button.btn-warning:hover {
      background: #F4E8D0;
      border-color: var(--amber-gold);
    }
    
    button.btn-danger {
      background: var(--cinnabar-wash);
      border-color: var(--cinnabar-border);
      color: var(--cinnabar-red);
    }
    button.btn-danger:hover {
      background: #F6E2DE;
      border-color: var(--cinnabar-red);
    }
    
    /* Workspace */
    .workspace {
      flex: 1;
      display: flex;
      position: relative;
      overflow: hidden;
    }
    
    #map-view {
      flex: 1;
      height: 100%;
      background: var(--bg-base);
      z-index: 10;
    }
    
    #weather-canvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 200;
    }
    
    /* Left Floating Tool Stack (Spatial Toolset + Mission Control Dock) */
    .left-floating-dock {
      position: absolute;
      top: 18px;
      left: 18px;
      z-index: 500;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
      pointer-events: none;
    }

    /* Floating Tool Dock */
    .map-tool-palette {
      pointer-events: auto;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 5px;
      box-shadow: var(--shadow-md);
      width: 205px;
      box-sizing: border-box;
    }
    
    .palette-header {
      font-size: 10px;
      font-family: var(--font-display);
      color: var(--ink-muted);
      letter-spacing: 0.8px;
      text-transform: uppercase;
      font-weight: 700;
      margin-bottom: 2px;
      padding-left: 2px;
    }
    
    .palette-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--bg-surface);
      border: 1px solid var(--border-hairline);
      color: var(--ink-deep);
      padding: 6px 9px;
      border-radius: 5px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      text-align: left;
      width: 100%;
    }
    .palette-btn:hover {
      background: var(--bg-surface-soft);
      border-color: var(--border-subtle);
    }
    
    .palette-btn.active {
      border-color: var(--celadon-jade);
      background: var(--celadon-wash);
      color: var(--celadon-jade);
    }
    
    .palette-btn.active-close {
      border-color: var(--cinnabar-red);
      background: var(--cinnabar-wash);
      color: var(--cinnabar-red);
    }
    
    .palette-btn.active-hazard {
      border-color: var(--amber-gold);
      background: var(--amber-wash);
      color: var(--amber-gold);
    }
    
    .palette-divider {
      height: 1px;
      background: var(--border-hairline);
      margin: 4px 0;
    }
    
    .cursor-closure, .cursor-hazard { cursor: crosshair !important; }
    
    /* Floating Banners */
    .weather-banner {
      position: absolute;
      top: 18px;
      right: 440px;
      z-index: 500;
      background: var(--bg-surface);
      border: 1px solid var(--border-hairline);
      border-radius: 6px;
      padding: 6px 14px;
      font-family: var(--font-mono);
      font-size: 11px;
      display: flex;
      align-items: center;
      gap: 9px;
      box-shadow: var(--shadow-sm);
      transition: all 0.25s ease;
      color: var(--ink-deep);
    }
    .weather-icon-box {
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--amber-gold);
    }
    
    .hazmat-alert-banner {
      position: absolute;
      top: 60px;
      right: 440px;
      z-index: 500;
      background: var(--bg-surface);
      border: 1.5px solid var(--amber-gold);
      border-radius: 8px;
      padding: 10px 14px;
      font-family: var(--font-mono);
      font-size: 11px;
      display: flex;
      flex-direction: column;
      gap: 5px;
      box-shadow: var(--shadow-md);
      max-width: 440px;
      animation: hazmatPulse 2s infinite alternate;
    }
    @keyframes hazmatPulse {
      0% { box-shadow: 0 4px 16px rgba(181, 127, 30, 0.15); }
      100% { box-shadow: 0 8px 24px rgba(181, 127, 30, 0.3); }
    }
    .hazmat-banner-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }
    .hazmat-alert-title {
      font-size: 11.5px;
      font-weight: 800;
      color: var(--amber-gold);
      letter-spacing: 0.6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .hazmat-count-badge {
      background: var(--amber-wash);
      color: var(--amber-gold);
      border: 1px solid var(--amber-border);
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 9.5px;
      font-weight: 700;
      letter-spacing: 0.4px;
    }
    .hazmat-alert-desc {
      font-size: 11px;
      color: var(--ink-washed);
      line-height: 1.45;
      font-family: var(--font-sans);
    }
    .hazmat-alert-gear {
      font-size: 10.5px;
      font-weight: 700;
      color: var(--celadon-jade);
      background: var(--celadon-wash);
      border: 1px solid var(--celadon-border);
      padding: 3px 8px;
      border-radius: 4px;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      margin-top: 2px;
    }
    
    .route-severed-banner {
      position: absolute;
      top: 60px;
      right: 440px;
      z-index: 510;
      background: var(--bg-surface);
      border: 1.5px solid var(--cinnabar-red);
      border-radius: 8px;
      padding: 11px 15px;
      font-family: var(--font-mono);
      font-size: 11px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      box-shadow: 0 8px 30px rgba(181, 54, 37, 0.2);
      max-width: 440px;
    }
    .route-severed-title {
      font-size: 12px;
      font-weight: 800;
      color: var(--cinnabar-red);
      letter-spacing: 0.6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .route-severed-badge {
      background: var(--cinnabar-wash);
      color: var(--cinnabar-red);
      border: 1px solid var(--cinnabar-border);
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 9.5px;
      font-weight: 700;
      letter-spacing: 0.4px;
    }
    
    /* Sidebar */
    aside.sidebar {
      width: 420px;
      height: 100%;
      background: var(--bg-surface);
      border-left: 1px solid var(--border-hairline);
      z-index: 100;
      display: flex;
      flex-direction: column;
      box-shadow: -2px 0 15px rgba(22, 25, 23, 0.03);
      overflow-y: auto;
    }
    
    .sidebar-section {
      padding: 13px 18px;
      border-bottom: 1px solid var(--border-hairline);
      transition: background 0.2s ease;
    }
    
    .section-header {
      font-size: 10.5px;
      font-family: var(--font-display);
      text-transform: uppercase;
      letter-spacing: 1.2px;
      color: var(--ink-muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 700;
      cursor: pointer;
      user-select: none;
      padding: 2px 0;
      transition: color 0.15s ease;
    }

    .section-header:hover {
      color: var(--ink-black);
    }

    .section-title-wrap {
      display: inline-flex;
      align-items: center;
      gap: 7px;
    }

    .panel-fold-icon {
      width: 11px;
      height: 11px;
      color: var(--ink-muted);
      transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), color 0.2s;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }

    .section-header:hover .panel-fold-icon {
      color: var(--celadon-jade);
    }

    .sidebar-section.collapsed .panel-fold-icon {
      transform: rotate(-90deg);
    }

    /* Scroll Style Motion Drop for Sidebar Section Contents */
    .sidebar-section-content {
      overflow: hidden;
      margin-top: 10px;
      transform-origin: top center;
      max-height: 850px;
      opacity: 1;
      transform: perspective(700px) rotateX(0deg) scaleY(1);
      transition: max-height 0.4s cubic-bezier(0.22, 1, 0.36, 1),
                  opacity 0.28s ease,
                  transform 0.38s cubic-bezier(0.22, 1, 0.36, 1),
                  margin-top 0.25s ease;
    }

    .sidebar-section.collapsed .sidebar-section-content {
      max-height: 0;
      opacity: 0;
      margin-top: 0;
      transform: perspective(700px) rotateX(-12deg) scaleY(0.7) translateY(-6px);
      pointer-events: none;
    }
    
    .section-num {
      color: var(--celadon-jade);
      margin-right: 4px;
    }
    
    .metrics-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 9px;
    }
    
    .metric-card {
      background: var(--bg-surface-soft);
      border: 1px solid var(--border-hairline);
      border-radius: 6px;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      gap: 3px;
      transition: border-color 0.15s ease;
    }
    .metric-card:hover {
      border-color: var(--border-subtle);
    }
    
    .metric-title {
      font-size: 9.5px;
      color: var(--ink-muted);
      font-family: var(--font-mono);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-weight: 600;
    }
    
    .metric-val {
      font-size: 18px;
      font-weight: 700;
      font-family: var(--font-mono);
      color: var(--ink-black);
      letter-spacing: -0.5px;
    }
    .metric-val.celadon { color: var(--celadon-jade); }
    .metric-val.amber { color: var(--amber-gold); }
    .metric-val.cinnabar { color: var(--cinnabar-red); }
    
    .comp-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 11px;
      font-family: var(--font-mono);
      margin-top: 4px;
    }
    .comp-table th {
      text-align: left;
      padding: 6px 7px;
      color: var(--ink-muted);
      border-bottom: 1px solid var(--border-hairline);
      font-weight: 600;
      font-size: 9.5px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .comp-table td {
      padding: 7px;
      border-bottom: 1px solid var(--border-hairline);
      cursor: pointer;
      transition: background 0.15s ease;
      color: var(--ink-deep);
    }
    .comp-table tr:hover td {
      background: var(--bg-surface-soft);
    }
    .comp-table tr.highlight td {
      background: var(--celadon-wash);
      font-weight: 600;
      color: var(--celadon-jade);
    }
    
    .badge-algo {
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 9.5px;
      font-weight: 700;
      display: inline-block;
      letter-spacing: 0.3px;
    }
    .badge-dijkstra {
      background: var(--dijkstra-wash);
      color: var(--dijkstra-slate);
      border: 1px solid rgba(92, 103, 97, 0.2);
    }
    .badge-astar {
      background: var(--amber-wash);
      color: var(--amber-gold);
      border: 1px solid var(--amber-border);
    }
    .badge-bi {
      background: var(--celadon-wash);
      color: var(--celadon-jade);
      border: 1px solid var(--celadon-border);
    }
    
    .layer-toggles-bar {
      display: flex;
      flex-direction: column;
      gap: 6px;
      background: var(--bg-surface-soft);
      border: 1px solid var(--border-hairline);
      border-radius: 6px;
      padding: 8px 10px;
      font-size: 11px;
      font-family: var(--font-mono);
      margin-top: 8px;
    }
    .toggle-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .toggle-label {
      display: flex;
      align-items: center;
      gap: 7px;
      cursor: pointer;
      color: var(--ink-deep);
      font-weight: 500;
    }
    .toggle-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }
    
    .road-legend {
      display: flex;
      justify-content: space-between;
      margin-top: 10px;
      padding: 6px 10px;
      background: var(--bg-surface-soft);
      border-radius: 5px;
      border: 1px solid var(--border-hairline);
      font-size: 9.5px;
      font-family: var(--font-mono);
      color: var(--ink-muted);
    }
    .legend-item { display: flex; align-items: center; gap: 5px; }
    .legend-swatch { width: 14px; height: 3px; border-radius: 2px; }
    
    .manifest-list {
      max-height: 125px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .manifest-item {
      font-size: 11px;
      font-family: var(--font-mono);
      background: var(--bg-surface-soft);
      border: 1px solid var(--border-hairline);
      padding: 5px 9px;
      border-radius: 4px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: var(--ink-deep);
    }
    .manifest-index {
      color: var(--ink-muted);
      font-size: 9.5px;
      font-weight: 600;
      margin-right: 6px;
    }
    
    .log-feed {
      max-height: 145px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 5px;
      font-family: var(--font-mono);
      font-size: 10.5px;
    }
    .log-entry {
      padding: 6px 9px;
      border-radius: 4px;
      background: var(--bg-surface-soft);
      border-left: 3px solid var(--celadon-jade);
      color: var(--ink-deep);
      line-height: 1.4;
    }
    .log-entry.warn { border-left-color: var(--amber-gold); color: #8F6010; }
    .log-entry.alert { border-left-color: var(--cinnabar-red); color: #9A2818; }
    .log-entry.success { border-left-color: var(--celadon-jade); color: var(--celadon-jade); }
    .log-time { color: var(--ink-muted); font-size: 9px; margin-bottom: 2px; }
    
    .divergence-badge {
      display: inline-block;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 9.5px;
      font-weight: 700;
      font-family: var(--font-mono);
      background: var(--bg-surface-soft);
      color: var(--ink-washed);
      border: 1px solid var(--border-hairline);
    }
    
    .vehicle-marker-pulse {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: var(--celadon-jade);
      border: 2.5px solid #FFF;
      box-shadow: 0 0 10px rgba(39, 92, 70, 0.6);
      animation: pulse 1s infinite alternate;
    }
    @keyframes pulse {
      0% { transform: scale(0.9); box-shadow: 0 0 6px rgba(39, 92, 70, 0.4); }
      100% { transform: scale(1.25); box-shadow: 0 0 16px rgba(39, 92, 70, 0.8); }
    }
  </style>
</head>
<body>
<div id="app-container">
  <header class="top-bar">
    <!-- Left: Brand Monogram & SCC Title -->
    <div class="brand-group">
      <div class="brand-seal">Æ</div>
      <div class="brand-text-block">
        <div class="brand-title">AETHERGRID AI</div>
        <div class="brand-subtitle">AUTONOMOUS URBAN DISPATCH · REAL-TIME NETWORK SCC</div>
      </div>
    </div>
    
    <!-- Middle: Spacious Centered Dropdowns with Full Breathing Room -->
    <div class="header-dropdowns-center">
      <!-- Grid Selector Scroll Dropdown -->
      <div class="scroll-dropdown-wrap" id="wrap-map-selector">
        <span class="control-label">GRID:</span>
        <button type="button" class="scroll-dropdown-trigger" id="trigger-map-selector" aria-haspopup="listbox" aria-expanded="false">
          <span class="trigger-value">Manhattan Island (18,912 Nodes)</span>
          <span class="scroll-indicator">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
          </span>
        </button>
        <div class="scroll-dropdown-panel" id="panel-map-selector" role="listbox">
          <div class="scroll-roller-cap top"></div>
          <div class="scroll-menu-items">
            <div class="scroll-menu-item selected" data-value="manhattan_large">
              <span class="item-lead"><span class="item-marker"></span>Manhattan Island</span>
              <span class="item-tag">18,912 Nodes</span>
            </div>
            <div class="scroll-menu-item" data-value="manhattan_midtown">
              <span class="item-lead"><span class="item-marker"></span>Manhattan Midtown</span>
              <span class="item-tag">1,529 Nodes</span>
            </div>
            <div class="scroll-menu-item" data-value="grid50">
              <span class="item-lead"><span class="item-marker"></span>Metro Grid</span>
              <span class="item-tag">50x50, 2,500 Nodes</span>
            </div>
            <div class="scroll-menu-item" data-value="grid32">
              <span class="item-lead"><span class="item-marker"></span>Urban Core</span>
              <span class="item-tag">32x32, 1,024 Nodes</span>
            </div>
            <div class="scroll-menu-item" data-value="grid16">
              <span class="item-lead"><span class="item-marker"></span>Tactical Grid</span>
              <span class="item-tag">16x16, 256 Nodes</span>
            </div>
          </div>
          <div class="scroll-roller-cap bottom"></div>
        </div>
        <select id="map-selector" class="select-input select-hidden">
          <option value="manhattan_large" selected>Manhattan Island (18,912 Nodes)</option>
          <option value="manhattan_midtown">Manhattan Midtown (1,529 Nodes)</option>
          <option value="grid50">Metro Grid (50x50, 2,500 Nodes)</option>
          <option value="grid32">Urban Core (32x32, 1,024 Nodes)</option>
          <option value="grid16">Tactical Grid (16x16, 256 Nodes)</option>
        </select>
      </div>
      
      <!-- Basemap Selector Scroll Dropdown -->
      <div class="scroll-dropdown-wrap" id="wrap-basemap-selector">
        <span class="control-label">BASEMAP:</span>
        <button type="button" class="scroll-dropdown-trigger" id="trigger-basemap-selector" aria-haspopup="listbox" aria-expanded="false">
          <span class="trigger-value">Esri Light Canvas</span>
          <span class="scroll-indicator">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
          </span>
        </button>
        <div class="scroll-dropdown-panel" id="panel-basemap-selector" role="listbox">
          <div class="scroll-roller-cap top"></div>
          <div class="scroll-menu-items">
            <div class="scroll-menu-item selected" data-value="esri_light">
              <span class="item-lead"><span class="item-marker"></span>Esri Light Canvas</span>
              <span class="item-tag">Recommended</span>
            </div>
            <div class="scroll-menu-item" data-value="osm">
              <span class="item-lead"><span class="item-marker"></span>OpenStreetMap Light</span>
              <span class="item-tag">Standard</span>
            </div>
            <div class="scroll-menu-item" data-value="opentopo">
              <span class="item-lead"><span class="item-marker"></span>Topographic Relief</span>
              <span class="item-tag">Contours</span>
            </div>
            <div class="scroll-menu-item" data-value="satellite">
              <span class="item-lead"><span class="item-marker"></span>Satellite Imagery</span>
              <span class="item-tag">Aerial</span>
            </div>
            <div class="scroll-menu-item" data-value="esri_dark">
              <span class="item-lead"><span class="item-marker"></span>Esri Dark Slate</span>
              <span class="item-tag">Night Ops</span>
            </div>
          </div>
          <div class="scroll-roller-cap bottom"></div>
        </div>
        <select id="basemap-selector" class="select-input select-hidden">
          <option value="esri_light" selected>Esri Light Canvas</option>
          <option value="osm">OpenStreetMap Light</option>
          <option value="opentopo">Topographic Relief</option>
          <option value="satellite">Satellite Imagery</option>
          <option value="esri_dark">Esri Dark Slate</option>
        </select>
      </div>
      
      <!-- Weather Selector Scroll Dropdown -->
      <div class="scroll-dropdown-wrap" id="wrap-weather-selector">
        <span class="control-label">WEATHER:</span>
        <button type="button" class="scroll-dropdown-trigger" id="trigger-weather-selector" aria-haspopup="listbox" aria-expanded="false">
          <span class="trigger-value">Clear Skies (1.00x)</span>
          <span class="scroll-indicator">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
          </span>
        </button>
        <div class="scroll-dropdown-panel" id="panel-weather-selector" role="listbox">
          <div class="scroll-roller-cap top"></div>
          <div class="scroll-menu-items">
            <div class="scroll-menu-item selected" data-value="clear">
              <span class="item-lead"><span class="item-marker"></span>Clear Skies</span>
              <span class="item-tag">1.00x Friction</span>
            </div>
            <div class="scroll-menu-item" data-value="rain">
              <span class="item-lead"><span class="item-marker"></span>Rain / Alley Surge</span>
              <span class="item-tag">1.25x Friction</span>
            </div>
            <div class="scroll-menu-item" data-value="fog">
              <span class="item-lead"><span class="item-marker"></span>Coastal Fog / Visibility</span>
              <span class="item-tag">1.40x Friction</span>
            </div>
            <div class="scroll-menu-item" data-value="snow">
              <span class="item-lead"><span class="item-marker"></span>Snow / Highway Frost</span>
              <span class="item-tag">1.85x Friction</span>
            </div>
          </div>
          <div class="scroll-roller-cap bottom"></div>
        </div>
        <select id="weather-selector" class="select-input select-hidden">
          <option value="clear" selected>Clear Skies (1.00x)</option>
          <option value="rain">Rain / Alley Surge (1.25x)</option>
          <option value="fog">Coastal Fog / Visibility (1.40x)</option>
          <option value="snow">Snow / Highway Frost (1.85x)</option>
        </select>
      </div>
    </div>
    
    <!-- Right: Clean System Telemetry Pills -->
    <div class="header-telemetry-right">
      <div class="system-pill">
        <span class="system-dot"></span>
        <span>METROPOLITAN SCC</span>
      </div>
      <div class="system-pill">
        <span>18,912 NODES</span>
      </div>
      <div class="system-pill">
        <span>24,164 CORRIDORS</span>
      </div>
    </div>
  </header>
  
  <div class="workspace">
    <!-- Left Floating Toolset & Mission Control Stack -->
    <div class="left-floating-dock">
      <!-- Floating Interactive Tool Dock -->
      <div class="map-tool-palette">
        <div class="palette-header">Spatial Toolset</div>
        <button id="tool-route" class="palette-btn active">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3"></circle></svg>
          <span>Waypoints (Origin / Goal)</span>
        </button>
        <button id="tool-close" class="palette-btn">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="6" width="18" height="12" rx="2"></rect><line x1="3" y1="12" x2="21" y2="12"></line></svg>
          <span>Toggle Road Closure</span>
        </button>
        <button id="tool-hazard" class="palette-btn">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="2"></circle><path d="M12 2a5 5 0 0 0-4.9 4A5 5 0 0 0 2 11a5 5 0 0 0 4 4.9"></path><path d="M12 22a5 5 0 0 0 4.9-4A5 5 0 0 0 22 13a5 5 0 0 0-4-4.9"></path></svg>
          <span>Inject HazMat Spill</span>
        </button>
        <button id="tool-compare" class="palette-btn">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
          <span>Run Benchmark Shootout</span>
        </button>
        <div class="palette-divider"></div>
        <button id="btn-quick-close" class="palette-btn" style="background:var(--cinnabar-wash);border-color:var(--cinnabar-border);color:var(--cinnabar-red);">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          <span>Block Active Route</span>
        </button>
        <button id="btn-quick-hazard" class="palette-btn" style="background:var(--amber-wash);border-color:var(--amber-border);color:var(--amber-gold);">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
          <span>HazMat on Route</span>
        </button>
      </div>

      <!-- Mission Control Extending Tab (Below Spatial Toolset, Extends to Right on Hover) -->
      <div class="mission-control-dock" id="mission-control-dock">
        <div class="mission-dock-handle" id="mission-dock-handle" role="button" aria-expanded="false" title="Click to pin / Hover to extend">
          <div class="dock-handle-title">
            <span class="dock-pulse-dot"></span>
            <span>MISSION CONTROL</span>
          </div>
          <svg class="dock-chevron" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
        </div>
        <div class="mission-dock-flyout">
          <div class="dock-roller-divider"></div>
          <div class="mission-dock-actions">
            <button id="btn-dispatch-mission" class="dock-action-btn btn-primary" type="button">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>
              <span>Dispatch Mission</span>
            </button>
            
            <button id="btn-traffic-surge" class="dock-action-btn btn-warning" type="button">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
              <span>Congestion Surge</span>
            </button>
            
            <button id="btn-reset-disruptions" class="dock-action-btn btn-neutral" type="button">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>
              <span>Reset</span>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Floating Weather Status -->
    <div id="weather-banner" class="weather-banner">
      <div class="weather-icon-box" id="weather-banner-icon">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line></svg>
      </div>
      <span id="weather-banner-text">CLEAR: Balanced terrain costs across all corridor types.</span>
    </div>
    
    <!-- Floating HazMat Advisory Banner -->
    <div id="hazmat-alert-banner" class="hazmat-alert-banner" style="display:none;">
      <div class="hazmat-banner-header">
        <span class="hazmat-alert-title" id="hazmat-alert-title">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
          <span id="hazmat-title-text">HAZMAT ADVISORY</span>
        </span>
        <span id="hazmat-count-badge" class="hazmat-count-badge">1 INCIDENT SITE</span>
      </div>
      <div id="hazmat-alert-desc" class="hazmat-alert-desc">Evaluating corridor threat...</div>
      <div id="hazmat-alert-gear" class="hazmat-alert-gear">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
        <span id="hazmat-gear-text">MANDATORY GEAR: Level C PPE</span>
      </div>
    </div>
    
    <!-- Floating Route Severed Notice -->
    <div id="route-severed-banner" class="route-severed-banner" style="display:none;">
      <div class="hazmat-banner-header">
        <span class="route-severed-title">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line></svg>
          <span>DESTINATION UNREACHABLE · PATH SEVERED</span>
        </span>
        <span class="route-severed-badge">INVARIANT I1 UPHELD</span>
      </div>
      <div class="hazmat-alert-desc">Active closures have completely isolated Destination Node <span id="severed-dest-node" style="font-weight:700;color:var(--cinnabar-red)">--</span>. Zero closed edges traversed. Remove barrier or select alternate destination.</div>
    </div>
    
    <div id="map-view"></div>
    <canvas id="weather-canvas"></canvas>
    
    <!-- Right Telemetry & Mission Control Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-section">
        <div class="section-header" onclick="toggleSidebarSection(this)" role="button" aria-expanded="true">
          <div class="section-title-wrap">
            <svg class="panel-fold-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
            <span><span class="section-num">01 //</span> Search Telemetry</span>
          </div>
          <span id="algo-badge" style="color:var(--celadon-jade);font-weight:700;">BIDIRECTIONAL A*</span>
        </div>
        <div class="sidebar-section-content">
          <div class="metrics-grid">
            <div class="metric-card">
              <span class="metric-title">Search Latency</span>
              <span id="metric-latency" class="metric-val celadon">-- ms</span>
            </div>
            <div class="metric-card">
              <span class="metric-title">Nodes Expanded</span>
              <span id="metric-expanded" class="metric-val amber">--</span>
            </div>
            <div class="metric-card">
              <span class="metric-title">Search Pruned</span>
              <span id="metric-pruned" class="metric-val celadon">-- %</span>
            </div>
            <div class="metric-card">
              <span class="metric-title">Transit Cost</span>
              <span id="metric-cost" class="metric-val">-- s</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="sidebar-section">
        <div class="section-header" onclick="toggleSidebarSection(this)" role="button" aria-expanded="true">
          <div class="section-title-wrap">
            <svg class="panel-fold-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
            <span><span class="section-num">02 //</span> Benchmark Shootout</span>
          </div>
          <span id="divergence-display" class="divergence-badge">Divergence: --%</span>
        </div>
        <div class="sidebar-section-content">
          <table class="comp-table">
            <thead>
              <tr><th>Algorithm</th><th>Latency</th><th>Expanded</th><th>Cost</th><th>Speedup</th></tr>
            </thead>
            <tbody id="comp-table-body">
              <tr><td><span class="badge-algo badge-dijkstra">Dijkstra</span></td><td>--</td><td>--</td><td>--</td><td>1.0x</td></tr>
              <tr><td><span class="badge-algo badge-astar">Weighted A*</span></td><td>--</td><td>--</td><td>--</td><td>--</td></tr>
              <tr class="highlight"><td><span class="badge-algo badge-bi">Bidir A*</span></td><td>--</td><td>--</td><td>--</td><td>--</td></tr>
            </tbody>
          </table>
          
          <div class="layer-toggles-bar">
            <div class="toggle-row">
              <label class="toggle-label">
                <input type="checkbox" id="chk-show-bi" checked>
                <span class="toggle-dot" style="background:var(--celadon-jade);"></span>
                <span>Bidirectional A* (Optimal Route)</span>
              </label>
            </div>
            <div class="toggle-row">
              <label class="toggle-label">
                <input type="checkbox" id="chk-show-astar" checked>
                <span class="toggle-dot" style="background:var(--amber-gold);"></span>
                <span>Weighted A* (ε=2.5 Greedy)</span>
              </label>
            </div>
            <div class="toggle-row">
              <label class="toggle-label">
                <input type="checkbox" id="chk-show-dijkstra" checked>
                <span class="toggle-dot" style="background:var(--dijkstra-slate);"></span>
                <span>Dijkstra (Uninformed Baseline)</span>
              </label>
            </div>
            <div class="toggle-row" style="margin-top:4px;padding-top:4px;border-top:1px solid var(--border-hairline);">
              <label class="toggle-label">
                <input type="checkbox" id="chk-show-frontier" checked>
                <span class="toggle-dot" style="background:var(--amber-gold);"></span>
                <span style="color:var(--amber-gold);font-weight:700;">Frontier Exploration Clouds</span>
              </label>
            </div>
          </div>
        </div>
      </div>
      
      <div class="sidebar-section">
        <div class="section-header" onclick="toggleSidebarSection(this)" role="button" aria-expanded="true">
          <div class="section-title-wrap">
            <svg class="panel-fold-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
            <span><span class="section-num">03 //</span> Environmental Sensors</span>
          </div>
          <button id="btn-refresh-net" class="btn-control" style="padding:2px 7px;font-size:9.5px" onclick="event.stopPropagation()">Poll</button>
        </div>
        <div class="sidebar-section-content">
          <div class="metrics-grid">
            <div class="metric-card">
              <span class="metric-title">Weather Factor</span>
              <span id="metric-weather" class="metric-val celadon">1.00x</span>
            </div>
            <div class="metric-card">
              <span class="metric-title">Mean Congestion</span>
              <span id="metric-congestion" class="metric-val celadon">0.05</span>
            </div>
            <div class="metric-card">
              <span class="metric-title">Active Closures</span>
              <span id="metric-closures" class="metric-val cinnabar">0</span>
            </div>
            <div class="metric-card">
              <span class="metric-title">Intersections</span>
              <span id="metric-total-nodes" class="metric-val">--</span>
            </div>
          </div>
          
          <div class="road-legend">
            <div class="legend-item"><span class="legend-swatch" style="background:#5B9777;"></span><span>Free (ρ&lt;0.3)</span></div>
            <div class="legend-item"><span class="legend-swatch" style="background:#D99B26;"></span><span>Moderate</span></div>
            <div class="legend-item"><span class="legend-swatch" style="background:#D64733;"></span><span>Gridlock</span></div>
          </div>
        </div>
      </div>
      
      <div class="sidebar-section">
        <div class="section-header" onclick="toggleSidebarSection(this)" role="button" aria-expanded="true">
          <div class="section-title-wrap">
            <svg class="panel-fold-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
            <span><span class="section-num">04 //</span> Corridor Itinerary</span>
          </div>
          <span id="waypoint-count">0 waypoints</span>
        </div>
        <div class="sidebar-section-content">
          <div id="street-manifest" class="manifest-list">
            <div class="manifest-item"><span>Select Start and Destination on map...</span></div>
          </div>
        </div>
      </div>
      
      <div class="sidebar-section" style="flex:1;">
        <div class="section-header" onclick="toggleSidebarSection(this)" role="button" aria-expanded="true">
          <div class="section-title-wrap">
            <svg class="panel-fold-icon" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
            <span><span class="section-num">05 //</span> Mission Chronicle</span>
          </div>
        </div>
        <div class="sidebar-section-content">
          <div id="mission-log-feed" class="log-feed">
            <div class="log-entry success">
              <div class="log-time">[00:00.0]</div>
              <div>AetherGrid AI: Autonomous spatial dispatch engine ready. Urban SCC topology online.</div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  </div>
</div>

<script>
let map = null, canvasRenderer = null, tileLayers = {}, currentNetwork = null;
let roadLayerGroup = L.layerGroup(), biRouteLayerGroup = L.layerGroup(), astarRouteLayerGroup = L.layerGroup(), dijkstraRouteLayerGroup = L.layerGroup(), frontierLayerGroup = L.layerGroup(), markersLayerGroup = L.layerGroup(), disruptionMarkersGroup = L.layerGroup(), vehicleMarker = null;
let startNodeId = null, goalNodeId = null, activeTool = 'route', isVehicleAnimating = false, latestShootoutData = null;
let edgeIndex = [];
let weatherAnimationId = null, weatherType = 'clear', particles = [];

function initMap() {
  canvasRenderer = L.canvas({ padding: 0.5, tolerance: 15 });
  map = L.map('map-view', { center: [40.755, -73.98], zoom: 13, zoomControl: true, preferCanvas: true });
  
  tileLayers.esri_light = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', { attribution: 'Esri Light Canvas (Free)', maxZoom: 18 });
  tileLayers.osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: 'OpenStreetMap (Free)', maxZoom: 19 });
  tileLayers.opentopo = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', { attribution: 'Esri World Topo', maxZoom: 18 });
  tileLayers.satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { attribution: 'Esri Imagery', maxZoom: 18 });
  tileLayers.esri_dark = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', { attribution: 'Esri Dark Slate', maxZoom: 18 });
  
  tileLayers.esri_light.addTo(map);
  
  roadLayerGroup.addTo(map);
  frontierLayerGroup.addTo(map);
  dijkstraRouteLayerGroup.addTo(map);
  astarRouteLayerGroup.addTo(map);
  biRouteLayerGroup.addTo(map);
  disruptionMarkersGroup.addTo(map);
  markersLayerGroup.addTo(map);
  
  map.on('click', onMapClick);
  setupEventListeners();
  setupWeatherCanvas();
  loadNetwork();
}

function pointToSegmentDist(px, py, ax, ay, bx, by) {
  const dx = bx - ax, dy = by - ay, lenSq = dx * dx + dy * dy;
  if (lenSq < 1e-12) return Math.hypot(px - ax, py - ay);
  let t = ((px - ax) * dx + (py - ay) * dy) / lenSq;
  t = Math.max(0, Math.min(1, t));
  return Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
}

function findNearestEdge(latlng, maxPx) {
  maxPx = maxPx || 35;
  if (edgeIndex.length === 0 || !map) return null;
  const clickPt = map.latLngToContainerPoint(latlng);
  let best = Infinity, bestE = null;
  for (const e of edgeIndex) {
    const p1 = map.latLngToContainerPoint([e.lat1, e.lon1]);
    const p2 = map.latLngToContainerPoint([e.lat2, e.lon2]);
    const d = pointToSegmentDist(clickPt.x, clickPt.y, p1.x, p1.y, p2.x, p2.y);
    if (d < best) { best = d; bestE = e; }
  }
  return (best <= maxPx) ? bestE : null;
}

function findNearestNode(latlng) {
  if (!currentNetwork) return null;
  let best = Infinity, bestN = null;
  for (const n of currentNetwork.nodes) {
    const d = Math.hypot(n.lat - latlng.lat, n.lon - latlng.lng);
    if (d < best) { best = d; bestN = n; }
  }
  return (best * 111000 < 500) ? bestN : null;
}

function onMapClick(e) {
  if (activeTool === 'close') {
    const edge = findNearestEdge(e.latlng, 35);
    if (edge) {
      toggleClosure(edge.u, edge.v);
      logEvent('CLOSURE TOGGLED on corridor (' + edge.u + '↔' + edge.v + '). Recalculating...', 'warn');
    } else {
      logEvent('CLOSURE: No road within click range. Click closer to a road line.', 'alert');
    }
  } else if (activeTool === 'hazard') {
    const edge = findNearestEdge(e.latlng, 35);
    if (edge) {
      injectHazard(edge.u, edge.v);
      logEvent('HAZMAT SPILL injected on corridor (' + edge.u + '↔' + edge.v + '). Recalculating...', 'warn');
    } else {
      logEvent('HAZMAT: No road within click range. Click closer to a road line.', 'alert');
    }
  } else if (activeTool === 'route') {
    const node = findNearestNode(e.latlng);
    if (node) {
      if (!startNodeId || (startNodeId && goalNodeId)) {
        startNodeId = node.id;
        goalNodeId = null;
        logEvent('ORIGIN: Node ' + node.id + '. Click destination...', 'normal');
        updateEndpointMarkers();
      } else {
        goalNodeId = node.id;
        logEvent('DESTINATION: Node ' + node.id + '. Computing routes...', 'success');
        updateEndpointMarkers();
        recalculateAndShootout();
      }
    }
  }
}

function setupEventListeners() {
  document.getElementById('basemap-selector').addEventListener('change', e => {
    Object.values(tileLayers).forEach(l => map.removeLayer(l));
    if (tileLayers[e.target.value]) tileLayers[e.target.value].addTo(map);
  });
  
  document.getElementById('map-selector').addEventListener('change', e => {
    logEvent('Loading network ' + e.target.value + '...', 'normal');
    fetch('/api/load_map', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ map: e.target.value })
    }).then(() => loadNetwork());
  });
  
  document.getElementById('weather-selector').addEventListener('change', e => {
    weatherType = e.target.value;
    updateWeatherVisuals(e.target.value);
    fetch('/api/weather', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ weather: e.target.value })
    }).then(r => r.json()).then(d => {
      document.getElementById('metric-weather').textContent = d.multiplier.toFixed(2) + 'x';
      logEvent('WEATHER: ' + d.weather + ' active. Corridors adjusting for terrain friction.', 'warn');
      refreshEdgesStatus();
      recalculateAndShootout();
    });
  });
  
  document.getElementById('btn-traffic-surge').addEventListener('click', () => {
    logEvent('SURGE: Injecting arterial rush-hour congestion...', 'warn');
    fetch('/api/traffic_surge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ delta: 60 })
    }).then(r => r.json()).then(d => {
      document.getElementById('metric-congestion').textContent = d.mean_congestion;
      document.getElementById('metric-congestion').className = 'metric-val cinnabar';
      logEvent('SURGE: ' + d.affected_corridors + ' corridors congested (ρ=' + d.mean_congestion + '). Detours recomputing...', 'alert');
      refreshEdgesStatus();
      recalculateAndShootout();
    });
  });
  
  document.getElementById('btn-reset-disruptions').addEventListener('click', () => {
    fetch('/api/reset', { method: 'POST' }).then(r => r.json()).then(d => {
      document.getElementById('metric-congestion').textContent = d.mean_congestion;
      document.getElementById('metric-congestion').className = 'metric-val celadon';
      document.getElementById('metric-closures').textContent = '0';
      disruptionMarkersGroup.clearLayers();
      const sb = document.getElementById('route-severed-banner');
      if (sb) sb.style.display = 'none';
      const hzBtn = document.getElementById('btn-dispatch-mission');
      if (hzBtn) {
        hzBtn.disabled = false;
        hzBtn.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg><span>Dispatch Mission</span>';
      }
      logEvent('RESET: All closures and hazards cleared. Free-flow restored.', 'success');
      refreshEdgesStatus();
      recalculateAndShootout();
    });
  });
  
  document.getElementById('btn-dispatch-mission').addEventListener('click', () => animateVehicleMission());
  
  document.getElementById('btn-quick-close').addEventListener('click', () => {
    fetch('/api/route', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start_id: startNodeId, goal_id: goalNodeId, algorithm: 'bi_astar' })
    }).then(r => r.json()).then(r => {
      if (r.success && r.path_node_ids && r.path_node_ids.length > 3) {
        const mid = Math.floor(r.path_node_ids.length / 2);
        const u = r.path_node_ids[mid], v = r.path_node_ids[mid + 1];
        toggleClosure(u, v);
        logEvent('BLOCK: Corridor (' + u + '↔' + v + ') closed. Observing deterministic detour...', 'alert');
      }
    });
  });
  
  document.getElementById('btn-quick-hazard').addEventListener('click', () => {
    fetch('/api/route', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start_id: startNodeId, goal_id: goalNodeId, algorithm: 'bi_astar' })
    }).then(r => r.json()).then(r => {
      if (r.success && r.path_node_ids && r.path_node_ids.length > 3) {
        const mid = Math.floor(r.path_node_ids.length / 2);
        const u = r.path_node_ids[mid], v = r.path_node_ids[mid + 1];
        injectHazard(u, v);
        logEvent('HAZMAT: Incident injected on route corridor (' + u + '↔' + v + ') [+60s penalty].', 'warn');
      }
    });
  });
  
  document.getElementById('btn-refresh-net').addEventListener('click', () => refreshEdgesStatus());
  
  [{ id: 'tool-route', name: 'route' }, { id: 'tool-close', name: 'close' }, { id: 'tool-hazard', name: 'hazard' }, { id: 'tool-compare', name: 'compare' }].forEach(t => {
    document.getElementById(t.id).addEventListener('click', () => {
      document.querySelectorAll('.palette-btn').forEach(b => b.classList.remove('active', 'active-close', 'active-hazard'));
      const btn = document.getElementById(t.id);
      if (t.name === 'close') btn.classList.add('active-close');
      else if (t.name === 'hazard') btn.classList.add('active-hazard');
      else btn.classList.add('active');
      activeTool = t.name;
      const mapEl = document.getElementById('map-view');
      mapEl.classList.remove('cursor-closure', 'cursor-hazard');
      if (t.name === 'close') {
        mapEl.classList.add('cursor-closure');
        logEvent('TOOL: Road Closure active. Click any corridor to toggle barrier.', 'warn');
      } else if (t.name === 'hazard') {
        mapEl.classList.add('cursor-hazard');
        logEvent('TOOL: HazMat active. Click any corridor to inject contamination.', 'warn');
      }
      if (activeTool === 'compare') recalculateAndShootout();
    });
  });
  
  document.getElementById('chk-show-bi').addEventListener('change', e => {
    if (e.target.checked) biRouteLayerGroup.addTo(map); else map.removeLayer(biRouteLayerGroup);
  });
  document.getElementById('chk-show-astar').addEventListener('change', e => {
    if (e.target.checked) astarRouteLayerGroup.addTo(map); else map.removeLayer(astarRouteLayerGroup);
  });
  document.getElementById('chk-show-dijkstra').addEventListener('change', e => {
    if (e.target.checked) dijkstraRouteLayerGroup.addTo(map); else map.removeLayer(dijkstraRouteLayerGroup);
  });
  document.getElementById('chk-show-frontier').addEventListener('change', e => {
    if (e.target.checked) frontierLayerGroup.addTo(map); else map.removeLayer(frontierLayerGroup);
  });
}

function loadNetwork() {
  logEvent('Connecting to routing engine...', 'normal');
  fetch('/api/network').then(r => r.json()).then(data => {
    currentNetwork = data;
    renderNetwork(data);
    startNodeId = data.start_node;
    goalNodeId = data.goal_node;
    document.getElementById('metric-total-nodes').textContent = data.num_nodes.toLocaleString();
    document.getElementById('metric-closures').textContent = '0';
    logEvent('LOADED: ' + data.name + ' (' + data.num_nodes.toLocaleString() + ' nodes, ' + data.num_edges.toLocaleString() + ' edges)', 'success');
    recalculateAndShootout();
  }).catch(err => logEvent('Load Error: ' + err.message, 'alert'));
}

function renderNetwork(net) {
  roadLayerGroup.clearLayers();
  markersLayerGroup.clearLayers();
  disruptionMarkersGroup.clearLayers();
  edgeIndex = [];
  
  if (net.bounds && net.bounds[0][0] !== net.bounds[1][0]) {
    map.fitBounds(net.bounds, { padding: [25, 25] });
  } else if (net.center) {
    map.setView(net.center, 13);
  }
  
  const nLookup = {};
  net.nodes.forEach(n => { nLookup[n.id] = n; });
  
  net.edges.forEach(e => {
    const u = nLookup[e.u], v = nLookup[e.v];
    if (!u || !v) return;
    const s = getEdgeStyle(e);
    const poly = L.polyline([[u.lat, u.lon], [v.lat, v.lon]], {
      renderer: canvasRenderer,
      color: s.color,
      weight: s.weight,
      opacity: s.opacity
    });
    poly._edgeRef = e;
    poly.bindTooltip((e.street || 'Corridor') + ' | ' + e.cost + 's | ρ=' + e.congestion + ' (' + e.terrain + ')', { sticky: true });
    poly.on('click', function(ev) {
      if (L.DomEvent) L.DomEvent.stopPropagation(ev);
      if (activeTool === 'close') {
        toggleClosure(e.u, e.v);
        logEvent('Corridor (' + e.u + '↔' + e.v + ') toggled via direct click.', 'warn');
      } else if (activeTool === 'hazard') {
        injectHazard(e.u, e.v);
        logEvent('HazMat injected on corridor (' + e.u + '↔' + e.v + ').', 'warn');
      }
    });
    roadLayerGroup.addLayer(poly);
    edgeIndex.push({ u: e.u, v: e.v, lat1: u.lat, lon1: u.lon, lat2: v.lat, lon2: v.lon });
  });
  
  const sr = net.nodes.length > 5000 ? 0.03 : 0.12;
  net.nodes.forEach(n => {
    if (n.is_depot || n.is_hospital || Math.random() < sr) {
      const c = L.circleMarker([n.lat, n.lon], {
        radius: n.is_depot || n.is_hospital ? 6.5 : 3.0,
        fillColor: n.is_depot ? '#275C46' : (n.is_hospital ? '#B53625' : '#88918A'),
        color: '#FFFFFF',
        weight: 1.5,
        opacity: 0.9,
        fillOpacity: 0.85
      });
      c.bindTooltip('Node ' + n.id + ': ' + (n.label || 'Intersection'));
      markersLayerGroup.addLayer(c);
    }
  });
  updateEndpointMarkers();
}

function getEdgeStyle(e) {
  if (!e.is_open) return { color: '#B53625', weight: 5.5, opacity: 1.0 };
  if (e.is_hazard) return { color: '#B57F1E', weight: 4.2, opacity: 0.95 };
  const rho = e.congestion || 0;
  if (rho >= 0.6) return { color: '#D64733', weight: 3.6, opacity: 0.9 };
  if (rho >= 0.25) return { color: '#D99B26', weight: 2.6, opacity: 0.75 };
  if (e.terrain === 'highway') return { color: '#3A6B56', weight: 2.8, opacity: 0.75 };
  if (e.terrain === 'arterial') return { color: '#5B7E6F', weight: 2.0, opacity: 0.65 };
  return { color: '#88918A', weight: 1.4, opacity: 0.45 };
}

function refreshEdgesStatus() {
  fetch('/api/edges_status').then(r => r.json()).then(data => {
    const em = {};
    data.edges.forEach(e => { em[e.u + '_' + e.v] = e; });
    roadLayerGroup.eachLayer(l => {
      if (l._edgeRef) {
        const u = em[l._edgeRef.u + '_' + l._edgeRef.v];
        if (u) {
          l._edgeRef.congestion = u.congestion;
          l._edgeRef.cost = u.cost;
          l._edgeRef.is_open = u.is_open;
          l._edgeRef.is_hazard = u.is_hazard;
          const s = getEdgeStyle(l._edgeRef);
          l.setStyle({ color: s.color, weight: s.weight, opacity: s.opacity });
        }
      }
    });
  });
}

function updateEndpointMarkers() {
  markersLayerGroup.eachLayer(l => { if (l._isEndpointMarker) markersLayerGroup.removeLayer(l); });
  if (!currentNetwork) return;
  const nL = {};
  currentNetwork.nodes.forEach(n => { nL[n.id] = n; });
  if (startNodeId !== null && nL[startNodeId]) {
    const sn = nL[startNodeId];
    const m = L.circleMarker([sn.lat, sn.lon], {
      radius: 9.5,
      fillColor: '#275C46',
      color: '#FFFFFF',
      weight: 3.0,
      fillOpacity: 0.95
    }).bindPopup('<b>Origin Station</b><br>Node ' + startNodeId);
    m._isEndpointMarker = true;
    markersLayerGroup.addLayer(m);
  }
  if (goalNodeId !== null && nL[goalNodeId]) {
    const gn = nL[goalNodeId];
    const m = L.circleMarker([gn.lat, gn.lon], {
      radius: 9.5,
      fillColor: '#B53625',
      color: '#FFFFFF',
      weight: 3.0,
      fillOpacity: 0.95
    }).bindPopup('<b>Destination Hospital</b><br>Node ' + goalNodeId);
    m._isEndpointMarker = true;
    markersLayerGroup.addLayer(m);
  }
}

function recalculateAndShootout() {
  if (startNodeId === null || goalNodeId === null) return;
  fetch('/api/compare_routes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start_id: startNodeId, goal_id: goalNodeId })
  }).then(r => r.json()).then(res => {
    const severedBanner = document.getElementById('route-severed-banner');
    const hzBanner = document.getElementById('hazmat-alert-banner');
    const hzBtn = document.getElementById('btn-dispatch-mission');
    
    if (!res.success) {
      logEvent('ROUTE SEVERED: Destination unreachable under active road closures (Invariant I1 upheld).', 'alert');
      biRouteLayerGroup.clearLayers();
      astarRouteLayerGroup.clearLayers();
      dijkstraRouteLayerGroup.clearLayers();
      frontierLayerGroup.clearLayers();
      latestShootoutData = null;
      
      if (severedBanner) {
        severedBanner.style.display = 'flex';
        const el = document.getElementById('severed-dest-node');
        if (el) el.textContent = goalNodeId;
      }
      if (hzBanner) hzBanner.style.display = 'none';
      if (hzBtn) {
        hzBtn.innerHTML = '<span>Path Severed (Unreachable)</span>';
        hzBtn.disabled = true;
      }
      document.getElementById('algo-badge').textContent = 'BLOCKED (NO PATH)';
      document.getElementById('algo-badge').style.color = 'var(--cinnabar-red)';
      document.getElementById('metric-latency').textContent = 'N/A';
      document.getElementById('metric-expanded').textContent = '--';
      document.getElementById('metric-pruned').textContent = '0.0%';
      document.getElementById('metric-cost').textContent = 'SEVERED (∞)';
      document.getElementById('divergence-display').textContent = 'Divergence: N/A';
      
      const tbody = document.getElementById('comp-table-body');
      tbody.innerHTML = ''
        + '<tr><td><span class="badge-algo badge-dijkstra">Dijkstra</span></td><td>--</td><td>--</td><td style="color:var(--cinnabar-red);font-weight:700">UNREACHABLE</td><td>--</td></tr>'
        + '<tr><td><span class="badge-algo badge-astar">Weighted A*</span></td><td>--</td><td>--</td><td style="color:var(--cinnabar-red);font-weight:700">UNREACHABLE</td><td>--</td></tr>'
        + '<tr class="highlight"><td><span class="badge-algo badge-bi">Bidir A*</span></td><td>--</td><td>--</td><td style="color:var(--cinnabar-red);font-weight:700">UNREACHABLE</td><td>--</td></tr>';
      
      document.getElementById('waypoint-count').textContent = '0 waypoints';
      const mc = document.getElementById('street-manifest');
      mc.innerHTML = '<div class="manifest-item"><span style="color:var(--cinnabar-red)">All corridors to destination are walled by active closures.</span></div>';
      return;
    }
    
    if (severedBanner) severedBanner.style.display = 'none';
    if (hzBtn) hzBtn.disabled = false;
    document.getElementById('algo-badge').style.color = 'var(--celadon-jade)';
    latestShootoutData = res;
    
    const divD = document.getElementById('divergence-display');
    if (res.path_divergence_pct !== undefined) divD.textContent = 'Divergence: ' + res.path_divergence_pct + '%';
    
    const tbody = document.getElementById('comp-table-body');
    tbody.innerHTML = '';
    let dR = null, aR = null, bR = null;
    res.comparison.forEach(row => {
      const tr = document.createElement('tr');
      let bc = 'badge-astar';
      if (row.key === 'dijkstra') { bc = 'badge-dijkstra'; dR = row; }
      else if (row.key === 'bi_astar') { bc = 'badge-bi'; tr.className = 'highlight'; bR = row; }
      else { aR = row; }
      const cs = row.cost_seconds >= 0 ? row.cost_seconds.toFixed(0) + 's' : 'N/A';
      tr.innerHTML = '<td><span class="badge-algo ' + bc + '">' + row.name.split('(')[0].trim() + '</span></td><td>' + row.time_ms.toFixed(2) + ' ms</td><td>' + row.nodes_expanded.toLocaleString() + '</td><td>' + cs + '</td><td style="color:var(--celadon-jade);font-weight:700">' + row.speedup.toFixed(1) + 'x</td>';
      tr.addEventListener('click', () => focusAlgorithm(row.key));
      tbody.appendChild(tr);
    });
    
    const best = bR || aR || dR;
    document.getElementById('algo-badge').textContent = best.name.toUpperCase();
    document.getElementById('metric-latency').textContent = best.time_ms.toFixed(2) + ' ms';
    document.getElementById('metric-expanded').textContent = best.nodes_expanded.toLocaleString();
    document.getElementById('metric-pruned').textContent = best.pruned_pct.toFixed(1) + '%';
    document.getElementById('metric-cost').textContent = best.cost_seconds.toFixed(1) + ' s';
    
    renderComparativeRoutes(dR, aR, bR);
    renderFrontierClouds(dR, aR, bR);
    
    const wCost = aR ? aR.cost_seconds : 0, oCost = bR ? bR.cost_seconds : 0;
    const costDiff = wCost > 0 && oCost > 0 ? ((wCost / oCost - 1) * 100).toFixed(1) : '0.0';
    logEvent('SHOOTOUT: Bidir A* ' + bR.speedup.toFixed(1) + 'x speedup, pruned ' + bR.pruned_pct.toFixed(1) + '%. W-A* divergence ' + (res.path_divergence_pct || 0) + '% (+ ' + costDiff + '% cost).', 'success');
    
    // HazMat Corridor Traversal Evaluation
    if (res.hazmat_status && res.hazmat_status.has_hazmat) {
      hzBanner.style.display = 'flex';
      document.getElementById('hazmat-title-text').textContent = res.hazmat_status.severity_level;
      const sitesCount = res.hazmat_status.incident_sites_count || res.hazmat_status.count || 1;
      const segsCount = res.hazmat_status.segments_count || 0;
      const siteWord = sitesCount === 1 ? '1 INCIDENT SITE' : sitesCount + ' INCIDENT SITES';
      const segWord = segsCount > 1 ? ' (' + segsCount + ' SEGMENTS)' : '';
      document.getElementById('hazmat-count-badge').textContent = siteWord + segWord;
      document.getElementById('hazmat-alert-desc').textContent = res.hazmat_status.crew_directive + ' (Affects: ' + (res.hazmat_status.affected_streets.join(', ') || 'Corridor') + ')';
      document.getElementById('hazmat-gear-text').textContent = 'CREW DIRECTIVE: ' + res.hazmat_status.ppe_gear;
      
      if (res.hazmat_status.severity_code >= 3) {
        hzBanner.style.borderColor = 'var(--cinnabar-red)';
        document.getElementById('hazmat-alert-title').style.color = 'var(--cinnabar-red)';
      } else if (res.hazmat_status.severity_code === 2) {
        hzBanner.style.borderColor = 'var(--amber-gold)';
        document.getElementById('hazmat-alert-title').style.color = 'var(--amber-gold)';
      } else {
        hzBanner.style.borderColor = 'var(--amber-gold)';
        document.getElementById('hazmat-alert-title').style.color = 'var(--amber-gold)';
      }
      hzBtn.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg><span>Dispatch (' + (res.hazmat_status.severity_code === 3 ? 'Level A' : (res.hazmat_status.severity_code === 2 ? 'SCBA' : 'PPE')) + ' Equipped)</span>';
      logEvent('HAZMAT NOTIFICATION [' + res.hazmat_status.severity_level + ']: ' + siteWord + segWord + ' on route. Order: Don ' + res.hazmat_status.ppe_gear, 'alert');
    } else {
      hzBanner.style.display = 'none';
      hzBtn.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg><span>Dispatch Mission</span>';
    }
  });
  
  fetch('/api/route', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start_id: startNodeId, goal_id: goalNodeId, algorithm: 'bi_astar' })
  }).then(r => r.json()).then(r => {
    if (r.success) {
      document.getElementById('waypoint-count').textContent = r.total_waypoints + ' waypoints';
      const mc = document.getElementById('street-manifest');
      mc.innerHTML = '';
      (r.streets || []).forEach((st, i) => {
        const it = document.createElement('div');
        it.className = 'manifest-item';
        const numStr = (i + 1 < 10 ? '0' : '') + (i + 1);
        it.innerHTML = '<div><span class="manifest-index">' + numStr + '</span><span>' + st + '</span></div><span style="color:var(--celadon-jade);font-size:14px;">&bull;</span>';
        mc.appendChild(it);
      });
    }
  });
}

function renderComparativeRoutes(dD, aD, bD) {
  dijkstraRouteLayerGroup.clearLayers();
  astarRouteLayerGroup.clearLayers();
  biRouteLayerGroup.clearLayers();
  
  if (dD && dD.path_coords && dD.path_coords.length > 0) {
    const p = L.polyline(dD.path_coords, { color: '#5C6761', weight: 4.0, opacity: 0.75, dashArray: '6,6' });
    p.bindTooltip('<b>Dijkstra Baseline</b><br>Cost: ' + dD.cost_seconds + 's | Expanded: ' + dD.nodes_expanded, { sticky: true });
    dijkstraRouteLayerGroup.addLayer(p);
  }
  if (aD && aD.path_coords && aD.path_coords.length > 0) {
    const p = L.polyline(aD.path_coords, { color: '#B57F1E', weight: 4.8, opacity: 0.85, dashArray: '10,6' });
    p.bindTooltip('<b>Weighted A* (ε=2.5 Greedy)</b><br>Cost: ' + aD.cost_seconds + 's', { sticky: true });
    astarRouteLayerGroup.addLayer(p);
  }
  if (bD && bD.path_coords && bD.path_coords.length > 0) {
    const p = L.polyline(bD.path_coords, { color: '#275C46', weight: 5.5, opacity: 0.95, lineCap: 'round', lineJoin: 'round' });
    p.bindTooltip('<b>Bidirectional A* (Optimal)</b><br>Cost: ' + bD.cost_seconds + 's', { sticky: true });
    biRouteLayerGroup.addLayer(p);
  }
}

function renderFrontierClouds(dD, aD, bD) {
  frontierLayerGroup.clearLayers();
  if (dD && dD.explored_coords) {
    dD.explored_coords.forEach(c => {
      frontierLayerGroup.addLayer(L.circleMarker(c, { renderer: canvasRenderer, radius: 2.8, fillColor: '#B57F1E', fillOpacity: 0.35, stroke: false }));
    });
  }
  if (aD && aD.explored_coords) {
    aD.explored_coords.forEach(c => {
      frontierLayerGroup.addLayer(L.circleMarker(c, { renderer: canvasRenderer, radius: 2.8, fillColor: '#275C46', fillOpacity: 0.45, stroke: false }));
    });
  }
}

function focusAlgorithm(key) {
  if (!latestShootoutData) return;
  const f = latestShootoutData.comparison.find(c => c.key === key);
  if (!f) return;
  document.getElementById('algo-badge').textContent = f.name.toUpperCase();
  document.getElementById('metric-latency').textContent = f.time_ms.toFixed(2) + ' ms';
  document.getElementById('metric-expanded').textContent = f.nodes_expanded.toLocaleString();
  document.getElementById('metric-pruned').textContent = f.pruned_pct.toFixed(1) + '%';
  document.getElementById('metric-cost').textContent = f.cost_seconds.toFixed(1) + ' s';
}

function toggleClosure(u, v) {
  fetch('/api/closure', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ u: u, v: v })
  }).then(r => r.json()).then(d => {
    const stLabel = d.corridor_street || ('Corridor ' + u + '↔' + v);
    const segCount = d.affected_edges ? d.affected_edges.length : 1;
    logEvent((d.is_open ? 'REOPENED: ' : 'CLOSED: ') + stLabel + ' (' + segCount + ' segment' + (segCount > 1 ? 's' : '') + '). Total: ' + d.active_closures_count, 'alert');
    document.getElementById('metric-closures').textContent = d.active_closures_count;
    
    if (d.affected_edges) {
      d.affected_edges.forEach(ae => {
        disruptionMarkersGroup.eachLayer(l => {
          if (l._closureRef === ae.u + '_' + ae.v || l._closureRef === ae.v + '_' + ae.u) disruptionMarkersGroup.removeLayer(l);
        });
      });
    } else {
      disruptionMarkersGroup.eachLayer(l => {
        if (l._closureRef === u + '_' + v || l._closureRef === v + '_' + u) disruptionMarkersGroup.removeLayer(l);
      });
    }
    
    if (!d.is_open) {
      const edge = edgeIndex.find(e => e.u === u && e.v === v) || (d.affected_edges && d.affected_edges.length ? edgeIndex.find(e => e.u === d.affected_edges[0].u && e.v === d.affected_edges[0].v) : null);
      if (edge) {
        const m = L.circleMarker([(edge.lat1 + edge.lat2) / 2, (edge.lon1 + edge.lon2) / 2], {
          radius: 8,
          fillColor: '#B53625',
          color: '#FFFFFF',
          weight: 2.2,
          fillOpacity: 0.95
        }).bindTooltip('BLOCK CLOSED: ' + stLabel);
        m._closureRef = u + '_' + v;
        disruptionMarkersGroup.addLayer(m);
      }
    }
    refreshEdgesStatus();
    recalculateAndShootout();
  });
}

function injectHazard(u, v) {
  fetch('/api/hazard', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ u: u, v: v, penalty: 60 })
  }).then(r => r.json()).then(d => {
    const stLabel = d.corridor_street || ('Corridor ' + u + '↔' + v);
    logEvent('HAZMAT on ' + stLabel + ' [+60s/segment]. Active: ' + d.active_hazards_count, 'warn');
    const edge = edgeIndex.find(e => e.u === u && e.v === v) || (d.affected_edges && d.affected_edges.length ? edgeIndex.find(e => e.u === d.affected_edges[0].u && e.v === d.affected_edges[0].v) : null);
    if (edge) {
      const m = L.circleMarker([(edge.lat1 + edge.lat2) / 2, (edge.lon1 + edge.lon2) / 2], {
        radius: 8,
        fillColor: '#B57F1E',
        color: '#FFFFFF',
        weight: 2.2,
        fillOpacity: 0.95
      }).bindTooltip('HAZMAT ZONE: ' + stLabel + ' (+60s)');
      m._hazardRef = u + '_' + v;
      disruptionMarkersGroup.addLayer(m);
    }
    refreshEdgesStatus();
    recalculateAndShootout();
  });
}

function animateVehicleMission() {
  if (startNodeId === null || goalNodeId === null || isVehicleAnimating) return;
  fetch('/api/route', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start_id: startNodeId, goal_id: goalNodeId, algorithm: 'bi_astar' })
  }).then(r => r.json()).then(res => {
    if (!res.success) return;
    isVehicleAnimating = true;
    logEvent('DISPATCH: Emergency unit en route to Node ' + goalNodeId + '...', 'warn');
    const coords = res.path_coords;
    let idx = 0;
    if (!vehicleMarker) {
      vehicleMarker = L.marker(coords[0], {
        icon: L.divIcon({ className: 'vehicle-marker-pulse', iconSize: [20, 20] })
      }).addTo(map);
    } else {
      vehicleMarker.setLatLng(coords[0]);
    }
    const iv = Math.max(80, Math.min(250, 4000 / coords.length));
    const tmr = setInterval(() => {
      if (idx < coords.length) {
        vehicleMarker.setLatLng(coords[idx]);
        idx++;
      } else {
        clearInterval(tmr);
        isVehicleAnimating = false;
        logEvent('MISSION ACCOMPLISHED: Arrived at Destination Node ' + goalNodeId + '.', 'success');
      }
    }, iv);
  });
}

function setupWeatherCanvas() {
  const canvas = document.getElementById('weather-canvas'), ctx = canvas.getContext('2d');
  function resize() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
  }
  window.addEventListener('resize', resize);
  resize();
  particles = [];
  for (let i = 0; i < 120; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      len: 10 + Math.random() * 15,
      speed: 3 + Math.random() * 5,
      radius: 1.5 + Math.random() * 2.5,
      drift: -1 + Math.random() * 2
    });
  }
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (weatherType === 'rain') {
      ctx.strokeStyle = 'rgba(70, 110, 95, 0.45)';
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      for (let p of particles) {
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(p.x - 3, p.y + p.len);
        p.y += p.speed * 2.2;
        p.x -= 1;
        if (p.y > canvas.height) { p.y = -20; p.x = Math.random() * canvas.width; }
      }
      ctx.stroke();
    } else if (weatherType === 'snow') {
      ctx.fillStyle = 'rgba(215, 222, 218, 0.7)';
      for (let p of particles) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();
        p.y += p.speed * 0.4;
        p.x += Math.sin(p.y * 0.03) * 0.8;
        if (p.y > canvas.height) { p.y = -10; p.x = Math.random() * canvas.width; }
      }
    }
    weatherAnimationId = requestAnimationFrame(draw);
  }
  draw();
}

function updateWeatherVisuals(w) {
  const banner = document.getElementById('weather-banner');
  const icon = document.getElementById('weather-banner-icon');
  const text = document.getElementById('weather-banner-text');
  if (w === 'clear') {
    icon.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line></svg>';
    text.textContent = 'CLEAR: Balanced terrain costs across all corridor types.';
    banner.style.borderColor = 'var(--border-hairline)';
  } else if (w === 'rain') {
    icon.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="16" y1="13" x2="16" y2="21"></line><line x1="8" y1="13" x2="8" y2="21"></line><line x1="12" y1="15" x2="12" y2="23"></line><path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"></path></svg>';
    text.textContent = 'RAIN: Alleys flood (+90%), unpaved mud (+150%). Arterials clear.';
    banner.style.borderColor = 'var(--celadon-border)';
  } else if (w === 'fog') {
    icon.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="14" x2="20" y2="14"></line><line x1="4" y1="18" x2="20" y2="18"></line><line x1="6" y1="10" x2="18" y2="10"></line><line x1="8" y1="6" x2="16" y2="6"></line></svg>';
    text.textContent = 'FOG: Highway visibility reduced (+80% penalty). Streets sheltered.';
    banner.style.borderColor = 'var(--amber-border)';
  } else if (w === 'snow') {
    icon.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="22"></line><line x1="12" y1="12" x2="4.93" y2="7.93"></line><line x1="12" y1="12" x2="19.07" y2="16.07"></line></svg>';
    text.textContent = 'BLIZZARD: Highways icy (+80%), offroad impassable. Alleys sheltered.';
    banner.style.borderColor = 'var(--celadon-border)';
  }
}

function logEvent(text, type) {
  type = type || 'normal';
  const feed = document.getElementById('mission-log-feed');
  const now = new Date();
  const ts = '[' + now.toTimeString().split(' ')[0] + '.' + Math.floor(now.getMilliseconds() / 100) + ']';
  const en = document.createElement('div');
  en.className = 'log-entry ' + type;
  en.innerHTML = '<div class="log-time">' + ts + '</div><div>' + text + '</div>';
  feed.prepend(en);
  while (feed.children.length > 50) feed.removeChild(feed.lastChild);
}

function toggleSidebarSection(header) {
  const section = header.closest('.sidebar-section');
  if (!section) return;
  const isCollapsed = section.classList.toggle('collapsed');
  header.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
}

function setupScrollDropdowns() {
  // Mission Control Dock: Click to pin / unpin
  const dock = document.getElementById('mission-control-dock');
  const dockHandle = document.getElementById('mission-dock-handle');
  if (dock && dockHandle) {
    dockHandle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isPinned = dock.classList.toggle('pinned');
      dockHandle.setAttribute('aria-expanded', isPinned ? 'true' : 'false');
    });

    document.addEventListener('click', (e) => {
      if (!dock.contains(e.target)) {
        dock.classList.remove('pinned');
        dockHandle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  const dropdownWraps = document.querySelectorAll('.scroll-dropdown-wrap');
  dropdownWraps.forEach(wrap => {
    const trigger = wrap.querySelector('.scroll-dropdown-trigger');
    const panel = wrap.querySelector('.scroll-dropdown-panel');
    const select = wrap.querySelector('select.select-input');
    const valueDisplay = wrap.querySelector('.trigger-value');
    const items = wrap.querySelectorAll('.scroll-menu-item');

    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = panel.classList.contains('open');
      document.querySelectorAll('.scroll-dropdown-panel.open').forEach(p => {
        if (p !== panel) {
          p.classList.remove('open');
          const wrp = p.closest('.scroll-dropdown-wrap');
          wrp?.querySelector('.scroll-dropdown-trigger')?.classList.remove('active');
          wrp?.querySelector('.scroll-dropdown-trigger')?.setAttribute('aria-expanded', 'false');
        }
      });

      if (isOpen) {
        panel.classList.remove('open');
        trigger.classList.remove('active');
        trigger.setAttribute('aria-expanded', 'false');
      } else {
        panel.classList.add('open');
        trigger.classList.add('active');
        trigger.setAttribute('aria-expanded', 'true');
      }
    });

    items.forEach(item => {
      item.addEventListener('click', (e) => {
        e.stopPropagation();
        const val = item.getAttribute('data-value');
        if (!val) return;

        items.forEach(i => i.classList.remove('selected'));
        item.classList.add('selected');

        const option = select.querySelector(`option[value="${val}"]`);
        if (option) {
          valueDisplay.textContent = option.textContent;
          select.value = val;
          select.dispatchEvent(new Event('change'));
        }

        panel.classList.remove('open');
        trigger.classList.remove('active');
        trigger.setAttribute('aria-expanded', 'false');
      });
    });

    select.addEventListener('change', () => {
      const currentVal = select.value;
      items.forEach(i => {
        if (i.getAttribute('data-value') === currentVal) {
          i.classList.add('selected');
          const option = select.querySelector(`option[value="${currentVal}"]`);
          if (option) valueDisplay.textContent = option.textContent;
        } else {
          i.classList.remove('selected');
        }
      });
    });
  });

  document.addEventListener('click', () => {
    document.querySelectorAll('.scroll-dropdown-panel.open').forEach(p => {
      p.classList.remove('open');
      const wrp = p.closest('.scroll-dropdown-wrap');
      wrp?.querySelector('.scroll-dropdown-trigger')?.classList.remove('active');
      wrp?.querySelector('.scroll-dropdown-trigger')?.setAttribute('aria-expanded', 'false');
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.scroll-dropdown-panel.open').forEach(p => {
        p.classList.remove('open');
        const wrp = p.closest('.scroll-dropdown-wrap');
        wrp?.querySelector('.scroll-dropdown-trigger')?.classList.remove('active');
        wrp?.querySelector('.scroll-dropdown-trigger')?.setAttribute('aria-expanded', 'false');
      });
    }
  });
}

window.addEventListener('DOMContentLoaded', () => {
  initMap();
  setupScrollDropdowns();
});
</script>
</body>
</html>
'''

target_path = 'Aether/web/static/index.html'
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Successfully generated {target_path} ({len(html_content)} bytes)")