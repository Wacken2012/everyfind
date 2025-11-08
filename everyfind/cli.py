#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Everyfind - CLI Interface
Copyright (C) 2025 Stefan

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import logging
import sys
from pathlib import Path

from . import __version__
from .indexer import FileIndexer
from .search_backend import get_search_backend
from .actions import FileActions


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def cmd_index(args):
    """Index a directory."""
    indexer = FileIndexer(args.db)
    
    paths = args.path if args.path else [str(Path.home())]
    
    total_indexed = 0
    for path in paths:
        print(f"Indexing: {path}")
        count = indexer.index_directory(path, exclude_patterns=args.exclude)
        total_indexed += count
        print(f"Indexed {count} files from {path}")
    
    print(f"\nTotal: {total_indexed} files indexed")
    indexer.close()


def cmd_search(args):
    """Search for files."""
    indexer = FileIndexer(args.db)
    
    # Get all paths from index
    all_paths = indexer.get_all_paths()
    
    if not all_paths:
        print("No files in index. Run 'everyfind index' first.")
        indexer.close()
        return
    
    print(f"Searching {len(all_paths)} files...")
    
    # Use fzf for fuzzy search
    backend = get_search_backend()
    result = backend.search(
        all_paths,
        multi=args.multi,
        prompt="Everyfind: ",
        query=args.query or ""
    )
    
    if result:
        if isinstance(result, list):
            for path in result:
                print(path)
        else:
            print(result)
            
            # Auto-open if requested
            if args.open:
                actions = FileActions()
                actions.open_file(result)
    
    indexer.close()


def cmd_gui(args):
    """Launch GTK GUI."""
    try:
        from .ui import run_gui
        run_gui(args.db)
    except ImportError as e:
        print(f"Error: GTK GUI not available. {e}")
        print("Install PyGObject: pip install PyGObject")
        sys.exit(1)


def cmd_clear(args):
    """Clear the index."""
    indexer = FileIndexer(args.db)
    indexer.clear_index()
    print("Index cleared")
    indexer.close()


def cmd_stats(args):
    """Show index statistics."""
    indexer = FileIndexer(args.db)
    
    all_paths = indexer.get_all_paths()
    
    print(f"Database: {indexer.db_path}")
    print(f"Total files: {len(all_paths)}")
    
    if indexer.db_path.exists():
        size = indexer.db_path.stat().st_size
        print(f"Database size: {FileActions._human_readable_size(size)}")
    
    indexer.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Everyfind - Ultra-fast file search for Linux",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  everyfind index /home/user              # Index home directory
  everyfind search                        # Interactive fuzzy search
  everyfind search -q "*.py"              # Search with initial query
  everyfind gui                           # Launch GTK GUI
  everyfind stats                         # Show index statistics
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--db',
        type=str,
        help='Path to SQLite database (default: ~/.config/everyfind/index.db)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Index command
    parser_index = subparsers.add_parser('index', help='Index directories')
    parser_index.add_argument(
        'path',
        nargs='*',
        help='Directories to index (default: home directory)'
    )
    parser_index.add_argument(
        '--exclude',
        nargs='+',
        default=['.git', '__pycache__', '.venv', 'venv', 'node_modules'],
        help='Patterns to exclude (default: .git __pycache__ .venv venv node_modules)'
    )
    parser_index.set_defaults(func=cmd_index)
    
    # Search command
    parser_search = subparsers.add_parser('search', help='Search for files')
    parser_search.add_argument(
        '-q', '--query',
        type=str,
        help='Initial search query'
    )
    parser_search.add_argument(
        '-m', '--multi',
        action='store_true',
        help='Allow multiple selections'
    )
    parser_search.add_argument(
        '-o', '--open',
        action='store_true',
        help='Open selected file automatically'
    )
    parser_search.set_defaults(func=cmd_search)
    
    # GUI command
    parser_gui = subparsers.add_parser('gui', help='Launch GTK GUI')
    parser_gui.set_defaults(func=cmd_gui)
    
    # Clear command
    parser_clear = subparsers.add_parser('clear', help='Clear the index')
    parser_clear.set_defaults(func=cmd_clear)
    
    # Stats command
    parser_stats = subparsers.add_parser('stats', help='Show index statistics')
    parser_stats.set_defaults(func=cmd_stats)
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    # Default to GUI if no command specified
    if not args.command:
        args.command = 'gui'
        args.func = cmd_gui
    
    # Execute command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == "__main__":
    main()
