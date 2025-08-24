"""Suggestion and analysis functionality for Elixir AI"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Any

from . import config


def find_key_files(repo_path: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """Find key files in the repository based on heuristics"""
    repo_path_obj = Path(repo_path)
    
    file_scores = []
    
    # Score files based on various heuristics
    for file_path in repo_path_obj.rglob('*'):
        if not file_path.is_file():
            continue
        
        rel_path = str(file_path.relative_to(repo_path))
        score = 0
        reasons = []
        
        # Size-based scoring
        try:
            file_size = file_path.stat().st_size
            if file_size > 10000:  # Files > 10KB get bonus
                score += 2
                reasons.append("large file")
        except OSError:
            continue
        
        # Name-based scoring
        name_lower = file_path.name.lower()
        path_lower = rel_path.lower()
        
        # Important file patterns
        important_patterns = [
            'main', 'app', 'core', 'init', 'server', 'api', 'model',
            'routes', 'controller', 'service', 'utils', 'config'
        ]
        
        for pattern in important_patterns:
            if pattern in name_lower or pattern in path_lower:
                score += 3
                reasons.append(f"contains '{pattern}'")
                break
        
        # Extension-based scoring
        if file_path.suffix in config.CODE_EXTS:
            score += 1
            reasons.append("code file")
        
        # README and documentation
        if name_lower.startswith('readme'):
            score += 5
            reasons.append("README file")
        elif name_lower.endswith('.md'):
            score += 2
            reasons.append("markdown file")
        
        # Configuration files
        config_files = ['requirements.txt', 'pyproject.toml', 'package.json', 
                       'setup.py', 'setup.cfg', 'Makefile', 'Dockerfile']
        if name_lower in config_files:
            score += 4
            reasons.append("configuration file")
        
        if score > 0:
            file_scores.append({
                'path': rel_path,
                'score': score,
                'reason': '; '.join(reasons)
            })
    
    # Sort by score and return top-k
    file_scores.sort(key=lambda x: x['score'], reverse=True)
    return file_scores[:top_k]


def detect_run_hints(repo_path: str) -> Dict[str, Any]:
    """Detect hints about how to run the repository"""
    repo_path_obj = Path(repo_path)
    hints = {}
    
    # Python projects
    if (repo_path_obj / 'requirements.txt').exists():
        hints['python_dependencies'] = [
            'Install dependencies: `pip install -r requirements.txt`',
            'Run with: `python main.py` or `python -m module_name`'
        ]
    
    if (repo_path_obj / 'pyproject.toml').exists():
        hints['python_project'] = [
            'Install in development mode: `pip install -e .`',
            'Run tests: `pytest` or `python -m pytest`'
        ]
    
    if (repo_path_obj / 'setup.py').exists():
        hints['python_setup'] = [
            'Install: `pip install .`',
            'Install in development: `pip install -e .`'
        ]
    
    # Node.js projects
    if (repo_path_obj / 'package.json').exists():
        hints['nodejs_project'] = [
            'Install dependencies: `npm install`',
            'Run scripts: `npm run <script_name>`',
            'Common scripts: `npm start`, `npm test`, `npm run dev`'
        ]
    
    # Makefile
    if (repo_path_obj / 'Makefile').exists():
        hints['makefile'] = [
            'Available targets: `make help` or `make list`',
            'Common targets: `make install`, `make test`, `make build`'
        ]
    
    # Docker
    if (repo_path_obj / 'Dockerfile').exists():
        hints['docker'] = [
            'Build image: `docker build -t project_name .`',
            'Run container: `docker run project_name`'
        ]
    
    if (repo_path_obj / 'docker-compose.yml').exists():
        hints['docker_compose'] = [
            'Start services: `docker-compose up`',
            'Build and start: `docker-compose up --build`'
        ]
    
    # Shell scripts
    shell_scripts = list(repo_path_obj.glob('*.sh'))
    if shell_scripts:
        hints['shell_scripts'] = [
            f'Run script: `./{script.name}` or `bash {script.name}`'
            for script in shell_scripts
        ]
    
    return hints


def analyze_contribution_opportunities(repo_path: str) -> Dict[str, Any]:
    """Analyze repository for contribution opportunities"""
    repo_path_obj = Path(repo_path)
    opportunities = {}
    
    # Test coverage
    test_dirs = ['tests', 'test', 'spec', '__tests__']
    test_files = list(repo_path_obj.glob('**/*test*.py')) + list(repo_path_obj.glob('**/*_test.py'))
    
    if test_dirs and any((repo_path_obj / d).exists() for d in test_dirs):
        opportunities['testing'] = ['Tests directory exists - good coverage']
    elif test_files:
        opportunities['testing'] = ['Some test files found - could expand coverage']
    else:
        opportunities['testing'] = ['No tests found - adding tests would be valuable']
    
    # Documentation coverage
    doc_coverage = _analyze_docstring_coverage(repo_path_obj)
    if doc_coverage > 80:
        opportunities['documentation'] = [f'Good docstring coverage: {doc_coverage:.1f}%']
    elif doc_coverage > 50:
        opportunities['documentation'] = [f'Moderate docstring coverage: {doc_coverage:.1f}% - room for improvement']
    else:
        opportunities['documentation'] = [f'Low docstring coverage: {doc_coverage:.1f}% - adding docs would help']
    
    # TODO/FIXME analysis
    todo_count = _count_todo_fixme(repo_path_obj)
    if todo_count > 0:
        opportunities['code_quality'] = [f'Found {todo_count} TODO/FIXME comments - good contribution opportunities']
    
    # CI/CD presence
    ci_dirs = ['.github/workflows', '.gitlab-ci', '.travis', '.circleci']
    ci_present = any((repo_path_obj / d).exists() for d in ci_dirs)
    
    if ci_present:
        opportunities['ci_cd'] = ['CI/CD pipeline exists - good project health']
    else:
        opportunities['ci_cd'] = ['No CI/CD found - setting up would be valuable']
    
    # Linting and formatting
    lint_configs = ['.flake8', '.pylintrc', 'pyproject.toml', '.pre-commit-config.yaml']
    lint_present = any((repo_path_obj / f).exists() for f in lint_configs)
    
    if lint_present:
        opportunities['code_quality'] = ['Linting/formatting configured - good code standards']
    else:
        opportunities['code_quality'] = ['No linting config - setting up would improve code quality']
    
    # README presence
    readme_files = ['README.md', 'README.rst', 'README.txt']
    readme_present = any((repo_path_obj / f).exists() for f in readme_files)
    
    if readme_present:
        opportunities['documentation'] = ['README exists - good project documentation']
    else:
        opportunities['documentation'] = ['No README found - creating one would be valuable']
    
    return opportunities


def _analyze_docstring_coverage(repo_path: Path) -> float:
    """Analyze docstring coverage in Python files"""
    python_files = list(repo_path.rglob('*.py'))
    total_functions = 0
    documented_functions = 0
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    total_functions += 1
                    if ast.get_docstring(node):
                        documented_functions += 1
                        
        except (SyntaxError, UnicodeDecodeError):
            continue
    
    if total_functions == 0:
        return 100.0
    
    return (documented_functions / total_functions) * 100


def _count_todo_fixme(repo_path: Path) -> int:
    """Count TODO/FIXME comments in the repository"""
    count = 0
    patterns = [r'TODO', r'FIXME', r'HACK', r'XXX', r'BUG']
    
    for file_path in repo_path.rglob('*'):
        if not file_path.is_file() or file_path.suffix not in config.CODE_EXTS:
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in patterns:
                try:
                    count += len(re.findall(re.escape(pattern), content, re.IGNORECASE))
                except re.error:
                    # Fallback to simple string search if regex fails
                    count += content.upper().count(pattern.upper())
                
        except (UnicodeDecodeError, OSError):
            continue
    
    return count


def _sanitize_markdown(text: str) -> str:
    """Sanitize text for safe markdown rendering"""
    if not text:
        return ""
    
    # Replace problematic characters that could break markdown parsing
    text = str(text)
    text = text.replace('\\', '\\\\')  # Escape backslashes
    text = text.replace('`', '\\`')    # Escape backticks
    text = text.replace('*', '\\*')    # Escape asterisks
    text = text.replace('_', '\\_')    # Escape underscores
    text = text.replace('[', '\\[')    # Escape brackets
    text = text.replace(']', '\\]')    # Escape brackets
    text = text.replace('(', '\\(')    # Escape parentheses
    text = text.replace(')', '\\)')    # Escape parentheses
    text = text.replace('#', '\\#')    # Escape hash
    text = text.replace('+', '\\+')    # Escape plus
    text = text.replace('-', '\\-')    # Escape minus
    text = text.replace('.', '\\.')    # Escape dots
    text = text.replace('!', '\\!')    # Escape exclamation
    text = text.replace('?', '\\?')    # Escape question mark
    
    return text


def format_suggestions(suggestions: Dict[str, Any]) -> str:
    """Format suggestions as markdown bullets"""
    if not suggestions:
        return "No suggestions available."
    
    lines = []
    for category, items in suggestions.items():
        safe_category = _sanitize_markdown(category)
        lines.append(f"### {safe_category}")
        if isinstance(items, list):
            for item in items:
                safe_item = _sanitize_markdown(item)
                lines.append(f"- {safe_item}")
        else:
            safe_item = _sanitize_markdown(items)
            lines.append(f"- {safe_item}")
        lines.append("")
    
    return '\n'.join(lines).strip()
