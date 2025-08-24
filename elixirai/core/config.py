"""Configuration constants for Elixir AI"""

# File extensions to index
CODE_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rb", ".rs",
    ".cpp", ".c", ".h", ".hpp", ".cs", ".php", ".swift", ".kt", ".m",
    ".mm", ".scala", ".lua", ".r", ".pl", ".sh", ".ps1"
}

TEXT_EXTS = {
    ".md", ".rst", ".txt", ".toml", ".yml", ".yaml", ".ini", ".cfg",
    ".json", ".xml", ".csv"
}

# Directories to ignore during indexing
IGNORE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "dist", "build",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".elixir_index"
}

# File size limits
MAX_FILE_BYTES = 800_000

# Chunking parameters
CHUNK_LINES = 120
CHUNK_OVERLAP = 20

# Index storage
INDEX_DIRNAME = ".elixir_index"

# TF-IDF parameters
TFIDF_MAX_FEATURES = 100_000
TFIDF_NGRAM_RANGE = (1, 2)
TFIDF_STOP_WORDS = "english"

# Search parameters
DEFAULT_TOP_K = 6
DEFAULT_MAX_CHARS = 1000

# Summary parameters
DEFAULT_MAX_SENTENCES = 8
DEFAULT_SUMMARY_MAX_SENTENCES = 7

# Graph export
GRAPH_JSON_FILENAME = "elixir_graph.json"
