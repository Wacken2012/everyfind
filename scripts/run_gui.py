#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run the Everyfind GTK GUI with optional pre-indexing and window size for screenshots.

Usage examples:
  # activate venv then:
  python3 scripts/run_gui.py --index /path/to/dir --size 1280x720

This script is a convenience helper for manual testing and screenshots.
"""

# Copyright (C) 2025 Stefan
# Licensed under the GNU General Public License v3 (see LICENSE)

import argparse
import logging
import sys
from pathlib import Path

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
except Exception as e:
    print("PyGObject (Gtk) not available. Install system packages (gir1.2-gtk-3.0) and PyGObject.")
    raise

from everyfind.indexer import FileIndexer
from everyfind.ui import EveryfindWindow


def parse_size(s: str):
    try:
        w, h = s.lower().split('x')
        return int(w), int(h)
    except Exception:
        raise argparse.ArgumentTypeError("Size must be WIDTHxHEIGHT, e.g. 1280x720")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run Everyfind GUI (helper for screenshots)")
    parser.add_argument("--db", type=str, default=None, help="Path to SQLite DB (optional)")
    parser.add_argument("--index", type=str, default=None, help="Directory to index before starting GUI")
    parser.add_argument("--size", type=parse_size, default=(800, 600), help="Window size WxH (e.g. 1280x720)")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    indexer = FileIndexer(db_path=args.db) if args.db else FileIndexer()

    if args.index:
        idx_path = Path(args.index)
        if not idx_path.exists():
            print(f"Index path does not exist: {args.index}")
            sys.exit(1)
        print(f"Indexing {args.index} (may take a while)...")
        indexer.index_directory(str(idx_path))

    win = EveryfindWindow(indexer)
    win.set_default_size(*args.size)
    win.show_all()

    try:
        Gtk.main()
    finally:
        indexer.close()


if __name__ == '__main__':
    main()
