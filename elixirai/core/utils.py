"""Utility functions and data structures for Elixir AI"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional

# Try to import chardet, fallback to basic encoding detection
try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False


@dataclass
class Chunk:
    """Represents a chunk of text from a file"""
    path: str
    start: int
    end: int
    text: str


def sniff_decode(file_path: str) -> str:
    """Decode file content with chardet fallback"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        if CHARDET_AVAILABLE:
            # Try to detect encoding with chardet
            detected = chardet.detect(raw_data)
            encoding = detected['encoding'] if detected['confidence'] > 0.7 else 'utf-8'
        else:
            # Fallback to utf-8 if chardet not available
            encoding = 'utf-8'
        
        # Decode with detected encoding, fallback to utf-8 with replacement
        try:
            return raw_data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            return raw_data.decode('utf-8', errors='replace')
            
    except Exception as e:
        raise RuntimeError(f"Failed to read file {file_path}: {e}")


def iter_repo_files(root: str) -> Iterator[Path]:
    """Iterate over all files in a repository"""
    root_path = Path(root)
    if not root_path.exists():
        raise ValueError(f"Repository path does not exist: {root}")
    
    for path in root_path.rglob('*'):
        if path.is_file():
            yield path


def should_index_file(path: Path, code_exts: set, text_exts: set, 
                     ignore_dirs: set, max_bytes: int) -> bool:
    """Check if a file should be indexed"""
    # Check if in ignored directory
    for part in path.parts:
        if part in ignore_dirs:
            return False
    
    # Check file extension
    if path.suffix not in code_exts and path.suffix not in text_exts:
        return False
    
    # Check file size
    try:
        if path.stat().st_size > max_bytes:
            return False
    except OSError:
        return False
    
    return True


def read_file_text(path: Path) -> str:
    """Read and decode file text content"""
    return sniff_decode(str(path))


def chunk_lines(text: str, size: int, overlap: int) -> List[str]:
    """Split text into overlapping line chunks"""
    lines = text.splitlines()
    chunks = []
    
    for i in range(0, len(lines), size - overlap):
        chunk_lines = lines[i:i + size]
        chunks.append('\n'.join(chunk_lines))
    
    return chunks


def human_bytes(n: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if n < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} TB"


def indent(text: str, n: int = 2) -> str:
    """Indent text by n spaces"""
    spaces = ' ' * n
    return '\n'.join(spaces + line for line in text.splitlines())
