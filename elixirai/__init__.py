"""Elixir AI - Intelligent Code Analysis and Q&A Engine"""

__version__ = "0.1.0"
__author__ = "Elixir AI Team"

from .core import (
    indexer,
    search,
    summarizer,
    graph,
    suggest,
    github,
)

__all__ = [
    "indexer",
    "search", 
    "summarizer",
    "graph",
    "suggest",
    "github",
]
