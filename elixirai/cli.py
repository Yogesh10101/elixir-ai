"""Command-line interface for Elixir AI"""

import argparse
import sys
from pathlib import Path

from .core import (
    indexer, search, summarizer, graph, suggest, github
)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Elixir AI - Intelligent Code Analysis and Q&A Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  elixir-ai clone https://github.com/user/repo repos/
  elixir-ai index repos/repo
  elixir-ai ask repos/repo "How does authentication work?"
  elixir-ai summarize repos/repo
  elixir-ai graph repos/repo --dot graph.dot
  elixir-ai suggest repos/repo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Clone command
    clone_parser = subparsers.add_parser('clone', help='Clone or download GitHub repository')
    clone_parser.add_argument('url', help='GitHub repository URL')
    clone_parser.add_argument('dest', help='Destination directory')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index repository for search')
    index_parser.add_argument('repo', help='Repository path')
    
    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask a question about the repository')
    ask_parser.add_argument('repo', help='Repository path')
    ask_parser.add_argument('question', help='Question to ask')
    ask_parser.add_argument('--k', type=int, default=6, help='Number of top results (default: 6)')
    ask_parser.add_argument('--max-chars', type=int, default=1000, help='Maximum characters in answer (default: 1000)')
    
    # Summarize command
    summarize_parser = subparsers.add_parser('summarize', help='Generate repository summary')
    summarize_parser.add_argument('repo', help='Repository path')
    summarize_parser.add_argument('--max-sentences', type=int, default=8, help='Maximum sentences in summary (default: 8)')
    
    # Graph command
    graph_parser = subparsers.add_parser('graph', help='Generate dependency graph')
    graph_parser.add_argument('repo', help='Repository path')
    graph_parser.add_argument('--dot', help='Export DOT file path')
    
    # Suggest command
    suggest_parser = subparsers.add_parser('suggest', help='Analyze contribution opportunities')
    suggest_parser.add_argument('repo', help='Repository path')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'clone':
            _handle_clone(args.url, args.dest)
        elif args.command == 'index':
            _handle_index(args.repo)
        elif args.command == 'ask':
            _handle_ask(args.repo, args.question, args.k, args.max_chars)
        elif args.command == 'summarize':
            _handle_summarize(args.repo, args.max_sentences)
        elif args.command == 'graph':
            _handle_graph(args.repo, args.dot)
        elif args.command == 'suggest':
            _handle_suggest(args.repo)
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n[ERROR] Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)


def _handle_clone(url: str, dest: str):
    """Handle clone command"""
    print(f"Cloning repository from {url}")
    result_path = github.clone_or_download_github(url, dest)
    print(f"[OK] Repository cloned to: {result_path}")


def _handle_index(repo_path: str):
    """Handle index command"""
    if not Path(repo_path).exists():
        print(f"[ERROR] Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    print(f"Indexing repository: {repo_path}")
    indexer.index_repository(repo_path)
    print("[OK] Indexing completed successfully")


def _handle_ask(repo_path: str, question: str, k: int, max_chars: int):
    """Handle ask command"""
    if not Path(repo_path).exists():
        print(f"[ERROR] Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    print(f"Question: {question}")
    print(f"Repository: {repo_path}")
    print("-" * 50)
    
    answer = search.ask_question(repo_path, question, k, max_chars)
    print(answer)


def _handle_summarize(repo_path: str, max_sentences: int):
    """Handle summarize command"""
    if not Path(repo_path).exists():
        print(f"[ERROR] Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    print(f"Generating summary for: {repo_path}")
    print("-" * 50)
    
    summary = summarizer.repo_summary(repo_path, max_sentences)
    print(summary)
    
    # Offer to write onboarding README
    print("\n" + "=" * 50)
    response = input("Would you like to generate an onboarding README? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        result = summarizer.write_onboarding_readme(repo_path)
        print(result)


def _handle_graph(repo_path: str, dot_path: str):
    """Handle graph command"""
    if not Path(repo_path).exists():
        print(f"[ERROR] Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    print(f"Generating dependency graph for: {repo_path}")
    
    # Get graph stats first
    stats = graph.get_graph_stats(repo_path)
    if 'error' in stats:
        print(f"[ERROR] Error getting graph stats: {stats['error']}")
        sys.exit(1)
    
    print(f"Graph statistics:")
    print(f"  Files: {stats['total_files']}")
    print(f"  Functions: {stats['total_functions']}")
    print(f"  Imports: {stats['total_imports']}")
    print(f"  Function calls: {stats['total_calls']}")
    
    # Export graph
    result = graph.export_graph(repo_path, dot_path)
    print(result)


def _handle_suggest(repo_path: str):
    """Handle suggest command"""
    if not Path(repo_path).exists():
        print(f"[ERROR] Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    print(f"Analyzing contribution opportunities for: {repo_path}")
    print("-" * 50)
    
    # Get suggestions
    suggestions = suggest.analyze_contribution_opportunities(repo_path)
    formatted = suggest.format_suggestions(suggestions)
    print(formatted)
    
    # Get key files
    print("\n" + "=" * 50)
    print("Key Files & Directories:")
    key_files = suggest.find_key_files(repo_path)
    for file_info in key_files:
        print(f"  {file_info['path']} (score: {file_info['score']:.2f})")
        if file_info.get('reason'):
            print(f"    - {file_info['reason']}")
    
    # Get run hints
    print("\n" + "=" * 50)
    print("How to Run Locally:")
    run_hints = suggest.detect_run_hints(repo_path)
    for hint_type, details in run_hints.items():
        print(f"  {hint_type.title()}:")
        if isinstance(details, list):
            for detail in details:
                print(f"    - {detail}")
        else:
            print(f"    - {details}")


if __name__ == '__main__':
    main()
