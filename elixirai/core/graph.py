"""Dependency graph functionality for Elixir AI"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import ast

from . import config


def build_dependency_graph(repo_path: str) -> Dict[str, Any]:
    """Build a dependency graph for the repository"""
    repo_path_obj = Path(repo_path)
    
    # Initialize graph
    nodes = []
    edges = []
    
    # Collect all Python files
    python_files = list(repo_path_obj.rglob("*.py"))
    
    # Add file nodes
    for py_file in python_files:
        rel_path = str(py_file.relative_to(repo_path))
        nodes.append({
            "id": rel_path,
            "type": "file",
            "path": rel_path
        })
    
    # Analyze imports and function calls
    for py_file in python_files:
        rel_path = str(py_file.relative_to(repo_path))
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse imports
            imports = _extract_imports(content, rel_path, repo_path_obj)
            for import_info in imports:
                edges.append({
                    "source": rel_path,
                    "target": import_info["target"],
                    "kind": "imports",
                    "details": import_info["details"]
                })
            
            # Parse function calls
            calls = _extract_function_calls(content, rel_path)
            for call_info in calls:
                edges.append({
                    "source": f"{rel_path}::{call_info['function']}",
                    "target": rel_path,
                    "kind": "calls",
                    "details": call_info["details"]
                })
                
        except Exception as e:
            print(f"Warning: Could not parse {rel_path}: {e}")
    
    # Add function nodes for calls
    function_nodes = set()
    for edge in edges:
        if edge["kind"] == "calls":
            function_nodes.add(edge["source"])
    
    for func_node in function_nodes:
        nodes.append({
            "id": func_node,
            "type": "function",
            "path": func_node
        })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "total_files": len([n for n in nodes if n["type"] == "file"]),
            "total_functions": len([n for n in nodes if n["type"] == "function"]),
            "total_imports": len([e for e in edges if e["kind"] == "imports"]),
            "total_calls": len([e for e in edges if e["kind"] == "calls"])
        }
    }


def _extract_imports(content: str, file_path: str, repo_path: Path) -> List[Dict[str, Any]]:
    """Extract import statements from Python code"""
    imports = []
    
    try:
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "target": alias.name,
                        "details": f"import {alias.name}"
                    })
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append({
                        "target": f"{module}.{alias.name}" if module else alias.name,
                        "details": f"from {module} import {alias.name}"
                    })
    
    except SyntaxError:
        # Fallback to regex for malformed Python
        import_patterns = [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s*$',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import\s+([a-zA-Z_][a-zA-Z0-9_,\s]*)',
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            for pattern in import_patterns:
                try:
                    match = re.match(pattern, line)
                    if match:
                        if 'from' in line:
                            module = match.group(1)
                            names = match.group(2).split(',')
                            for name in names:
                                imports.append({
                                    "target": f"{module}.{name.strip()}",
                                    "details": line
                                })
                        else:
                            imports.append({
                                "target": match.group(1),
                                "details": line
                            })
                except re.error:
                    # Skip this pattern if regex fails
                    continue
    
    return imports


def _extract_function_calls(content: str, file_path: str) -> List[Dict[str, Any]]:
    """Extract function calls from Python code"""
    calls = []
    
    try:
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append({
                        "function": node.func.id,
                        "details": f"function call: {node.func.id}"
                    })
                elif isinstance(node.func, ast.Attribute):
                    calls.append({
                        "function": node.func.attr,
                        "details": f"method call: {node.func.attr}"
                    })
    
    except SyntaxError:
        # Fallback to regex for malformed Python
        call_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        try:
            matches = re.findall(call_pattern, content)
            
            for match in matches:
                if match not in ['if', 'for', 'while', 'def', 'class', 'with']:
                    calls.append({
                        "function": match,
                        "details": f"function call: {match}"
                    })
        except re.error:
            # Skip regex parsing if it fails
            pass
    
    return calls


def export_graph(repo_path: str, dot_path: str = None) -> str:
    """Export dependency graph to JSON and optionally DOT format"""
    try:
        # Build graph
        graph = build_dependency_graph(repo_path)
        
        # Export JSON
        json_path = Path(repo_path) / config.GRAPH_JSON_FILENAME
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2)
        
        result = f"[OK] Graph exported to {json_path}"
        
        # Export DOT if requested
        if dot_path:
            dot_content = _graph_to_dot(graph)
            with open(dot_path, 'w', encoding='utf-8') as f:
                f.write(dot_content)
            result += f"\n[OK] DOT file exported to {dot_path}"
        
        return result
        
    except Exception as e:
        return f"[ERROR] Error exporting graph: {e}"


def _graph_to_dot(graph: Dict[str, Any]) -> str:
    """Convert graph to DOT format"""
    dot_lines = ["digraph G {"]
    dot_lines.append("  rankdir=LR;")
    dot_lines.append("  node [shape=box];")
    
    # Add nodes
    for node in graph["nodes"]:
        if node["type"] == "file":
            dot_lines.append(f'  "{node["id"]}" [label="{node["id"]}", shape=box];')
        else:
            dot_lines.append(f'  "{node["id"]}" [label="{node["id"]}", shape=ellipse];')
    
    # Add edges
    for edge in graph["edges"]:
        if edge["kind"] == "imports":
            dot_lines.append(f'  "{edge["source"]}" -> "{edge["target"]}" [label="imports", color=blue];')
        else:
            dot_lines.append(f'  "{edge["source"]}" -> "{edge["target"]}" [label="calls", color=red];')
    
    dot_lines.append("}")
    return '\n'.join(dot_lines)


def get_graph_stats(repo_path: str) -> Dict[str, Any]:
    """Get statistics about the dependency graph"""
    try:
        graph = build_dependency_graph(repo_path)
        return graph["metadata"]
    except Exception as e:
        return {"error": str(e)}
