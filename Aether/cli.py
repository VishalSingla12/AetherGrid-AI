"""
AetherGrid-AI Command Line Interface (CLI)
Entry point for executing simulations, running heavy benchmarks, and verifying test suites.
"""

import argparse
import os
import sys
import unittest

from Aether.simulation.demo_sim import DemoSimulation
from Aether.simulation.large_scale_demo import LargeScaleSimulation
from Aether.experiments.cost_model_experiments import run_all_experiments
from Aether.experiments.benchmarks import MultiScaleBenchmarkSuite
from Aether.web.server import start_mission_control_server


def main():
    parser = argparse.ArgumentParser(
        description="AetherGrid-AI: Autonomous Logistics & Emergency Dispatch Simulation"
    )
    parser.add_argument(
        "--mode",
        choices=["web", "serve", "demo", "experiments", "test", "benchmark"],
        default="web",
        help="Execution mode (default: web [OpenStreetMap Mission Control])",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for Mission Control web server (default: 8080)",
    )
    parser.add_argument(
        "--map",
        choices=["manhattan_large", "manhattan", "manhattan_midtown", "grid32", "grid50", "grid10"],
        default="manhattan_large",
        help="Map topology for simulation demo (default: manhattan_large [18,912 nodes])",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=0.15,
        help="Simulation step sleep delay in seconds (default: 0.15)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run simulation in headless non-visual mode",
    )
    parser.add_argument(
        "--benchmark-scale",
        choices=["heavy", "quick"],
        default="heavy",
        help="Benchmark intensity: 'heavy' evaluates multi-scale topologies and churn",
    )

    args = parser.parse_args()

    if args.mode in ("web", "serve"):
        start_mission_control_server(port=args.port, initial_map=args.map, block=True)

    elif args.mode == "demo":
        if args.map in ("manhattan", "grid32", "grid50"):
            print(f"[*] Launching Aether Large-Scale Computational Simulation on '{args.map}'...")
            sim = LargeScaleSimulation(map_type=args.map, headless=args.headless)
            sim.run(step_delay=args.speed)
        else:
            print("[*] Launching Aether 10x10 Grid Simulation Demo...")
            demo = DemoSimulation(rows=10, cols=10, headless=args.headless)
            demo.run(sleep_delay=args.speed)

    elif args.mode == "experiments":
        print("[*] Launching Phase 01 Empirical Experimentation Suite...")
        run_all_experiments()

    elif args.mode == "benchmark":
        print("[*] Executing Industrial Multi-Scale Performance Benchmark Suite...")
        suite = MultiScaleBenchmarkSuite()
        suite.run_full_suite()

    elif args.mode == "test":
        print("[*] Executing Aether Unit and Invariant Test Suite...")
        loader = unittest.TestLoader()
        suite = loader.discover("Aether/tests")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
