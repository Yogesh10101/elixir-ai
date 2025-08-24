"""Indexing functionality for Elixir AI"""

import os
import pickle
from pathlib import Path
from typing import List, Tuple, Optional

# Try to import required dependencies
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from . import config
from .utils import (
    Chunk, iter_repo_files, should_index_file, read_file_text, 
    chunk_lines, human_bytes
)


class RepositoryIndexer:
    """Indexes repository files into searchable chunks"""
    
    def __init__(self):
        self.chunks: List[Chunk] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.matrix: Optional[np.ndarray] = None
    
    def index_repository(self, repo_path: str) -> None:
        """Index all files in a repository"""
        print(f"Indexing repository: {repo_path}")
        
        # Clear previous index
        self.chunks.clear()
        
        # Collect and process files
        total_files = 0
        indexed_files = 0
        total_bytes = 0
        
        for file_path in iter_repo_files(repo_path):
            total_files += 1
            
            if should_index_file(
                file_path, config.CODE_EXTS, config.TEXT_EXTS,
                config.IGNORE_DIRS, config.MAX_FILE_BYTES
            ):
                try:
                    file_text = read_file_text(file_path)
                    file_bytes = len(file_text.encode('utf-8'))
                    total_bytes += file_bytes
                    
                    # Create chunks
                    file_chunks = chunk_lines(
                        file_text, config.CHUNK_LINES, config.CHUNK_OVERLAP
                    )
                    
                    for i, chunk_text in enumerate(file_chunks):
                        start_line = i * (config.CHUNK_LINES - config.CHUNK_OVERLAP) + 1
                        end_line = start_line + len(chunk_text.splitlines()) - 1
                        
                        chunk = Chunk(
                            path=str(file_path.relative_to(repo_path)),
                            start=start_line,
                            end=end_line,
                            text=chunk_text
                        )
                        self.chunks.append(chunk)
                    
                    indexed_files += 1
                    print(f"  ✓ {file_path.relative_to(repo_path)} ({human_bytes(file_bytes)})")
                    
                except Exception as e:
                    print(f"  ✗ {file_path.relative_to(repo_path)}: {e}")
        
        print(f"\nIndexed {indexed_files}/{total_files} files ({human_bytes(total_bytes)})")
        print(f"Created {len(self.chunks)} chunks")
        
        # Build TF-IDF matrix
        if self.chunks:
            self._build_tfidf_matrix()
            self._save_index(repo_path)
        else:
            print("No files to index!")
    
    def _build_tfidf_matrix(self) -> None:
        """Build TF-IDF matrix from chunks"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for TF-IDF indexing. Install with: pip install scikit-learn")
        
        if not NUMPY_AVAILABLE:
            raise ImportError("numpy is required for TF-IDF indexing. Install with: pip install numpy")
        
        print("Building TF-IDF matrix...")
        
        # Extract text from chunks
        texts = [chunk.text for chunk in self.chunks]
        
        # Create vectorizer
        self.vectorizer = TfidfVectorizer(
            ngram_range=config.TFIDF_NGRAM_RANGE,
            stop_words=config.TFIDF_STOP_WORDS,
            max_features=config.TFIDF_MAX_FEATURES
        )
        
        # Fit and transform
        self.matrix = self.vectorizer.fit_transform(texts)
        
        print(f"Matrix shape: {self.matrix.shape}")
        print(f"Vocabulary size: {len(self.vectorizer.vocabulary_)}")
    
    def _save_index(self, repo_path: str) -> None:
        """Save index to disk"""
        index_dir = Path(repo_path) / config.INDEX_DIRNAME
        index_dir.mkdir(exist_ok=True)
        
        # Save chunks
        chunks_path = index_dir / "chunks.pkl"
        with open(chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
        
        # Save TF-IDF data
        tfidf_data = {
            'vocabulary_': self.vectorizer.vocabulary_,
            'idf_': self.vectorizer.idf_,
            'stop_words_': getattr(self.vectorizer, 'stop_words_', set())
        }
        tfidf_path = index_dir / "tfidf.pkl"
        with open(tfidf_path, 'wb') as f:
            pickle.dump(tfidf_data, f)
        
        # Save matrix
        matrix_path = index_dir / "matrix.npz"
        np.savez_compressed(matrix_path, matrix=self.matrix)
        
        print(f"Index saved to {index_dir}")


def load_index(repo_path: str) -> Tuple[List[Chunk], 'TfidfVectorizer', 'np.ndarray']:
    """Load existing index from disk"""
    if not SKLEARN_AVAILABLE:
        raise ImportError("scikit-learn is required for loading indexes. Install with: pip install scikit-learn")
    
    if not NUMPY_AVAILABLE:
        raise ImportError("numpy is required for loading indexes. Install with: pip install numpy")
    
    index_dir = Path(repo_path) / config.INDEX_DIRNAME
    
    if not index_dir.exists():
        raise FileNotFoundError(f"No index found at {index_dir}")
    
    # Load chunks
    chunks_path = index_dir / "chunks.pkl"
    with open(chunks_path, 'rb') as f:
        chunks = pickle.load(f)
    
    # Load TF-IDF data
    tfidf_path = index_dir / "tfidf.pkl"
    with open(tfidf_path, 'rb') as f:
        tfidf_data = pickle.load(f)
    
    # Reconstruct vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=config.TFIDF_NGRAM_RANGE,
        stop_words=config.TFIDF_STOP_WORDS,
        max_features=config.TFIDF_MAX_FEATURES
    )
    vectorizer.vocabulary_ = tfidf_data['vocabulary_']
    vectorizer.idf_ = tfidf_data['idf_']
    if 'stop_words_' in tfidf_data:
        vectorizer.stop_words_ = tfidf_data['stop_words_']
    
    # Load matrix
    matrix_path = index_dir / "matrix.npz"
    matrix_data = np.load(matrix_path, allow_pickle=True)
    matrix = matrix_data['matrix']
    
    return chunks, vectorizer, matrix


def index_repository(repo_path: str) -> None:
    """Convenience function to index a repository"""
    indexer = RepositoryIndexer()
    indexer.index_repository(repo_path)
