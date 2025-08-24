"""Summarization functionality for Elixir AI"""

import re
import numpy as np
from pathlib import Path
from typing import List, Optional
import networkx as nx

from . import config
from .utils import Chunk
from .indexer import load_index


def textrank_summarize(text: str, max_sentences: int = None) -> str:
    """Summarize text using TextRank algorithm"""
    if max_sentences is None:
        max_sentences = config.DEFAULT_SUMMARY_MAX_SENTENCES
    
    # Split into sentences
    try:
        sentences = re.split(r'[.!?]+', text)
    except re.error:
        # Fallback to simple split if regex fails
        sentences = text.replace('.', '.\n').replace('!', '!\n').replace('?', '?\n').split('\n')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= max_sentences:
        return text
    
    try:
        # Use networkx for PageRank
        return _textrank_with_networkx(sentences, max_sentences)
    except ImportError:
        # Fallback to simple heuristic
        return _fallback_summarize(sentences, max_sentences)


def _textrank_with_networkx(sentences: List[str], max_sentences: int) -> str:
    """TextRank implementation using networkx"""
    if len(sentences) <= max_sentences:
        return '. '.join(sentences) + '.'
    
    # Create similarity matrix
    n = len(sentences)
    similarity_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i + 1, n):
            similarity = _calculate_sentence_similarity(sentences[i], sentences[j])
            similarity_matrix[i][j] = similarity
            similarity_matrix[j][i] = similarity
    
    # Create graph and run PageRank
    graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(graph)
    
    # Get top sentences
    top_indices = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:max_sentences]
    top_indices = sorted(top_indices)  # Maintain original order
    
    summary = '. '.join([sentences[i] for i in top_indices])
    return summary + '.'


def _fallback_summarize(sentences: List[str], max_sentences: int) -> str:
    """Fallback summarization using longest sentences"""
    # Sort by length and take top sentences
    sentence_lengths = [(i, len(s)) for i, s in enumerate(sentences)]
    sentence_lengths.sort(key=lambda x: x[1], reverse=True)
    
    top_indices = [i for i, _ in sentence_lengths[:max_sentences]]
    top_indices.sort()  # Maintain original order
    
    summary = '. '.join([sentences[i] for i in top_indices])
    return summary + '.'


def _calculate_sentence_similarity(sent1: str, sent2: str) -> float:
    """Calculate similarity between two sentences using word overlap"""
    try:
        words1 = set(re.findall(r'\w+', sent1.lower()))
        words2 = set(re.findall(r'\w+', sent2.lower()))
    except re.error:
        # Fallback to simple word extraction if regex fails
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def repo_summary(repo_path: str, max_sentences: int = None) -> str:
    """Generate a summary of the repository"""
    if max_sentences is None:
        max_sentences = config.DEFAULT_MAX_SENTENCES
    
    # Try to find README first
    readme_path = _find_readme(repo_path)
    if readme_path:
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            return textrank_summarize(readme_content, max_sentences)
        except Exception:
            pass
    
    # Fallback to summarizing indexed chunks
    try:
        chunks, _, _ = load_index(repo_path)
        if not chunks:
            return "No content found to summarize."
        
        # Combine all chunk text
        all_text = '\n'.join([chunk.text for chunk in chunks])
        return textrank_summarize(all_text, max_sentences)
        
    except FileNotFoundError:
        return "No index found. Please run 'elixir-ai index <repo>' first."
    except Exception as e:
        return f"Error generating summary: {e}"


def _find_readme(repo_path: str) -> Optional[Path]:
    """Find README file in repository"""
    repo_path_obj = Path(repo_path)
    readme_candidates = [
        "README.md", "README.rst", "README.txt",
        "readme.md", "readme.rst", "readme.txt"
    ]
    
    for candidate in readme_candidates:
        readme_path = repo_path_obj / candidate
        if readme_path.exists():
            return readme_path
    
    return None


def write_onboarding_readme(repo_path: str) -> str:
    """Write an onboarding README for the repository"""
    try:
        from . import suggest
        
        # Generate content
        summary = repo_summary(repo_path)
        key_files = suggest.find_key_files(repo_path)
        run_hints = suggest.detect_run_hints(repo_path)
        contributions = suggest.analyze_contribution_opportunities(repo_path)
        
        # Format content
        content = f"""# Onboarding Guide - {Path(repo_path).name}

## Quick Summary
{summary}

## Key Files & Directories
{_format_key_files(key_files)}

## How to Run Locally
{_format_run_hints(run_hints)}

## Good First Contributions
{_format_contributions(contributions)}

---
*Generated by Elixir AI - Intelligent Code Analysis Engine*
"""
        
        # Write file
        output_path = Path(repo_path) / "README_ELIXIR.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"[OK] Onboarding README written to {output_path}"
        
    except Exception as e:
        return f"[ERROR] Error writing onboarding README: {e}"


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


def _format_key_files(key_files: List[dict]) -> str:
    """Format key files for markdown"""
    if not key_files:
        return "No key files identified."
    
    lines = []
    for file_info in key_files:
        safe_path = _sanitize_markdown(file_info['path'])
        safe_reason = _sanitize_markdown(file_info.get('reason', ''))
        lines.append(f"- **{safe_path}** (score: {file_info['score']:.2f})")
        if safe_reason:
            lines.append(f"  - {safe_reason}")
    
    return '\n'.join(lines)


def _format_run_hints(run_hints: dict) -> str:
    """Format run hints for markdown"""
    if not run_hints:
        return "No run hints detected."
    
    lines = []
    for hint_type, details in run_hints.items():
        safe_hint_type = _sanitize_markdown(hint_type)
        lines.append(f"### {safe_hint_type}")
        if isinstance(details, list):
            for detail in details:
                safe_detail = _sanitize_markdown(detail)
                lines.append(f"- {safe_detail}")
        else:
            safe_detail = _sanitize_markdown(details)
            lines.append(f"- {safe_detail}")
        lines.append("")
    
    return '\n'.join(lines).strip()


def _format_contributions(contributions: dict) -> str:
    """Format contribution opportunities for markdown"""
    if not contributions:
        return "No contribution opportunities identified."
    
    lines = []
    for category, items in contributions.items():
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
