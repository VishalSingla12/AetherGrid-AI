#!/usr/bin/env python3
"""
Quick runner for AetherGrid Phase 01 Simulation Demo.
"""

import os
import sys

# Ensure project root is in sys.path so Aether can be imported cleanly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Aether.cli import main

if __name__ == "__main__":
    if "--terminal" in sys.argv:
        sys.argv.remove("--terminal")
        if not any(arg.startswith("--mode") for arg in sys.argv):
            sys.argv.insert(1, "--mode=demo")
    elif not any(arg.startswith("--mode") for arg in sys.argv):
        sys.argv.insert(1, "--mode=web")
    main()
