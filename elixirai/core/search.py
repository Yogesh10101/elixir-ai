"""Search functionality for Elixir AI"""

import numpy as np
from typing import List, Tuple
from sklearn.metrics.pairwise import cosine_similarity

from . import config
from .utils import Chunk
from .indexer import load_index


def ask_question(repo_path: str, question: str, k: int = None, 
                max_chars: int = None) -> str:
    """Ask a question about the repository and get an answer"""
    if k is None:
        k = config.DEFAULT_TOP_K
    if max_chars is None:
        max_chars = config.DEFAULT_MAX_CHARS
    
    try:
        # Load index
        chunks, vectorizer, matrix = load_index(repo_path)
        
        # Transform question
        question_vector = vectorizer.transform([question])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(question_vector, matrix).flatten()
        
        # Get top-k chunks
        top_indices = np.argsort(similarities)[::-1][:k]
        top_chunks = [chunks[i] for i in top_indices]
        top_scores = [similarities[i] for i in top_indices]
        
        # Build answer
        answer = _build_answer(top_chunks, top_scores, max_chars)
        
        return answer
        
    except FileNotFoundError:
        return "[ERROR] No index found. Please run 'elixir-ai index <repo>' first."
    except Exception as e:
        return f"[ERROR] Error searching repository: {e}"


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


def _build_answer(chunks: List[Chunk], scores: List[float], 
                 max_chars: int) -> str:
    """Build a formatted answer from top chunks"""
    if not chunks:
        return "No relevant information found."
    
    answer_parts = []
    total_chars = 0
    
    for chunk, score in zip(chunks, scores):
        if total_chars >= max_chars:
            break
        
        # Format chunk header with sanitized path
        safe_path = _sanitize_markdown(chunk.path)
        header = f"**From {safe_path}:{chunk.start}-{chunk.end}** (score: {score:.3f})"
        
        # Truncate chunk text if needed
        chunk_text = chunk.text
        remaining_chars = max_chars - total_chars - len(header) - 10  # Buffer for formatting
        
        if len(chunk_text) > remaining_chars:
            chunk_text = chunk_text[:remaining_chars] + "..."
        
        # Add to answer
        answer_parts.append(f"{header}\n```\n{chunk_text}\n```\n")
        total_chars += len(header) + len(chunk_text) + 10
    
    if not answer_parts:
        return "No relevant information found."
    
    return "\n".join(answer_parts)


def search_similar(repo_path: str, query: str, k: int = None) -> List[Tuple[Chunk, float]]:
    """Find chunks similar to a query"""
    if k is None:
        k = config.DEFAULT_TOP_K
    
    try:
        chunks, vectorizer, matrix = load_index(repo_path)
        
        # Transform query
        query_vector = vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, matrix).flatten()
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:k]
        results = [(chunks[i], similarities[i]) for i in top_indices]
        
        return results
        
    except FileNotFoundError:
        raise FileNotFoundError("No index found. Please run 'elixir-ai index <repo>' first.")
    except Exception as e:
        raise RuntimeError(f"Error searching repository: {e}")


def get_chunk_context(repo_path: str, chunk_index: int) -> Chunk:
    """Get a specific chunk by index"""
    try:
        chunks, _, _ = load_index(repo_path)
        if 0 <= chunk_index < len(chunks):
            return chunks[chunk_index]
        else:
            raise IndexError(f"Chunk index {chunk_index} out of range")
    except FileNotFoundError:
        raise FileNotFoundError("No index found. Please run 'elixir-ai index <repo>' first.")
