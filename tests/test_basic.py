"""Basic tests for Elixir AI"""

import pytest
from pathlib import Path
import tempfile
import os

from elixirai.core import config, utils


def test_config_constants():
    """Test that configuration constants are properly defined"""
    assert len(config.CODE_EXTS) > 0
    assert len(config.TEXT_EXTS) > 0
    assert config.MAX_FILE_BYTES > 0
    assert config.CHUNK_LINES > 0
    assert config.CHUNK_OVERLAP >= 0


def test_chunk_dataclass():
    """Test the Chunk dataclass"""
    from elixirai.core.utils import Chunk
    
    chunk = Chunk(
        path="test.py",
        start=1,
        end=10,
        text="def test():\n    pass"
    )
    
    assert chunk.path == "test.py"
    assert chunk.start == 1
    assert chunk.end == 10
    assert chunk.text == "def test():\n    pass"


def test_should_index_file():
    """Test file filtering logic"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("def test():\n    pass")
        
        # Test Python file
        assert utils.should_index_file(
            test_file, 
            config.CODE_EXTS, 
            config.TEXT_EXTS,
            config.IGNORE_DIRS,
            config.MAX_FILE_BYTES
        )
        
        # Test ignored directory
        ignored_dir = Path(temp_dir) / ".git"
        ignored_dir.mkdir()
        ignored_file = ignored_dir / "config"
        ignored_file.write_text("test")
        
        assert not utils.should_index_file(
            ignored_file,
            config.CODE_EXTS,
            config.TEXT_EXTS,
            config.IGNORE_DIRS,
            config.MAX_FILE_BYTES
        )


def test_chunk_lines():
    """Test text chunking functionality"""
    text = "line1\nline2\nline3\nline4\nline5"
    chunks = utils.chunk_lines(text, size=3, overlap=1)
    
    assert len(chunks) == 2
    assert "line1\nline2\nline3" in chunks[0]
    assert "line3\nline4\nline5" in chunks[1]


def test_human_bytes():
    """Test human-readable byte formatting"""
    assert utils.human_bytes(1024) == "1.0 KB"
    assert utils.human_bytes(1024 * 1024) == "1.0 MB"
    assert utils.human_bytes(500) == "500.0 B"


if __name__ == "__main__":
    pytest.main([__file__])
