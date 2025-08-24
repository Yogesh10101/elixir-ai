#!/usr/bin/env python3
"""
Elixir AI CLI Demo Script

This script demonstrates how to use Elixir AI programmatically
through the CLI interface.
"""

import subprocess
import sys
from pathlib import Path


def run_cli_command(command_args):
    """Run an Elixir AI CLI command and return the result"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "elixirai.cli"] + command_args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr


def demo_analysis():
    """Demonstrate repository analysis"""
    print("Elixir AI CLI Demo")
    print("=" * 50)
    
    # Check if we have a current repository indexed
    if Path(".elixir_index").exists():
        print("[OK] Found existing index for current repository")
        
        print("\nAnalyzing current repository...")
        stdout, stderr = run_cli_command(["suggest", "."])
        if stdout:
            print("Analysis Results:")
            print(stdout)
        if stderr:
            print("Warnings:", stderr)
            
        print("\nBuilding dependency graph...")
        stdout, stderr = run_cli_command(["graph", ".", "--dot", "demo_graph.dot"])
        if stdout:
            print("Graph Results:")
            print(stdout)
            
        print("\nChecking generated files...")
        if Path("demo_graph.dot").exists():
            print("[OK] Generated demo_graph.dot")
            print("First few lines:")
            with open("demo_graph.dot", "r") as f:
                print(f.read()[:200] + "...")
    else:
        print("[WARN] No index found. Run 'python3 -m elixirai.cli index .' first")
    
    print("\nCLI Commands to Try:")
    print("  python3 -m elixirai.cli suggest .")
    print("  python3 -m elixirai.cli graph . --dot graph.dot")
    print("  python3 -m elixirai.cli summarize .")


if __name__ == "__main__":
    demo_analysis()
