# Elixir AI - Intelligent Code Analysis & Q&A Engine

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/badge/PyPI-elixir--ai-blue.svg)](https://pypi.org/project/elixir-ai/)

**Elixir AI** is a production-ready Python engine that provides intelligent code analysis and natural language Q&A over any codebase using TF-IDF and cosine similarity. No proprietary LLMs required!

## Key Features

- **Semantic Code Search**: Ask questions in natural language and get relevant code snippets with file:line citations
- **Smart Indexing**: Automatically chunks code into overlapping segments for comprehensive coverage
- **Auto-Generated Onboarding**: Creates `README_ELIXIR.md` with summary, key files, and contribution opportunities
- **Dependency Analysis**: Builds dependency graphs showing imports and function calls
- **Contribution Insights**: Analyzes code quality, test coverage, and suggests improvements
- **GitHub Integration**: Clone repositories directly from GitHub URLs
- **Fast CLI**: Lightning-fast command-line interface for automation

## Quick Start

### Installation

```bash
# Install from PyPI
pip install elixir-ai

# Or install from source
git clone https://github.com/your-username/elixir-ai.git
cd elixir-ai
pip install -e .
```

### Command Line Usage

```bash
# Clone a GitHub repository
elixir-ai clone https://github.com/user/repo repos/

# Index the repository for search
elixir-ai index repos/repo

# Ask questions about your code
elixir-ai ask repos/repo "How does authentication work?"

# Generate repository summary
elixir-ai summarize repos/repo

# Build dependency graph
elixir-ai graph repos/repo --dot graph.dot

# Analyze contribution opportunities
elixir-ai suggest repos/repo
```

### CLI-First Design

The CLI is designed for speed and automation:

```bash
# Quick analysis
elixir-ai suggest repos/repo

# Batch processing
for repo in repos/*; do
  elixir-ai index "$repo"
  elixir-ai suggest "$repo" > "${repo}_analysis.txt"
done
```

## Architecture

Elixir AI uses a modular architecture with these core components:

- **`indexer.py`**: Builds TF-IDF index from repository files
- **`search.py`**: Performs semantic search using cosine similarity
- **`summarizer.py`**: Generates summaries using TextRank algorithm
- **`graph.py`**: Analyzes dependencies and function calls
- **`suggest.py`**: Identifies contribution opportunities
- **`github.py`**: Handles GitHub repository downloads

## Configuration

The engine automatically handles:
- **File Types**: Supports 25+ programming languages and text formats
- **Chunking**: 120-line chunks with 20-line overlap for optimal search
- **Encoding**: Robust text decoding with chardet fallback
- **Size Limits**: Configurable file size limits (default: 800KB)

## Supported Languages

### Code Files
Python, JavaScript, TypeScript, Java, Go, Rust, C++, C, C#, PHP, Swift, Kotlin, Scala, Lua, R, Perl, Shell scripts

### Text Files
Markdown, RST, TOML, YAML, INI, JSON, XML, CSV

## Use Cases

- **Onboarding**: Quickly understand new codebases
- **Code Review**: Find related code and dependencies
- **Documentation**: Generate comprehensive project overviews
- **Maintenance**: Identify technical debt and improvement areas
- **Learning**: Explore code patterns and architectures

## Development

### Setup Development Environment

```bash
git clone https://github.com/your-username/elixir-ai.git
cd elixir-ai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest --cov=elixirai --cov-report=html
```

### Code Quality

```bash
black elixirai/
flake8 elixirai/
mypy elixirai/
```

## 📈 Performance

- **Indexing**: ~1000 files/minute on modern hardware
- **Search**: Sub-second response for most queries
- **Memory**: Efficient sparse matrix storage
- **Scalability**: Handles repositories up to 100MB+ of code

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Good First Issues

- Add support for new file types
- Improve search relevance algorithms
- Enhance dependency graph visualization
- Add more language-specific parsers

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [scikit-learn](https://scikit-learn.org/) for TF-IDF and similarity
- Uses [NetworkX](https://networkx.org/) for graph algorithms
- Powered by [Streamlit](https://streamlit.io/) for the web interface

## 📞 Support

- 📧 Email: team@elixir-ai.dev
- 🐛 Issues: [GitHub Issues](https://github.com/elixir-ai/elixir-ai/issues)
- 📖 Docs: [Documentation](https://elixir-ai.readthedocs.io)

---

**Made with love by the Elixir AI Team**

*Transform your codebase understanding with the power of AI-driven analysis!*
