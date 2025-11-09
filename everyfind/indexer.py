#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Everyfind - Indexer Module
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

import os
import sqlite3
import logging
import threading
from pathlib import Path
from typing import Optional, Generator, Callable, Iterable, List, Union
from datetime import datetime
import fnmatch

logger = logging.getLogger(__name__)


class FileIndexer:
    """Recursively scan directories and store file paths in SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the indexer with a database path.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.config/everyfind/index.db
        """
        if db_path is None:
            config_dir = Path.home() / ".config" / "everyfind"
            config_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(config_dir / "index.db")

        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
        self._lock = threading.RLock()  # Reentrant lock for thread-safe operations
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the SQLite database with required schema."""
        # check_same_thread=False allows usage across threads (needed for GTK worker threads)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL UNIQUE,
                filename TEXT NOT NULL,
                size INTEGER,
                modified REAL,
                indexed_at REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filename ON files(filename)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_path ON files(path)
        """)

        self.conn.commit()
        logger.info(f"Database initialized at {self.db_path}")

    def get_all_paths(self) -> List[str]:
        """Retrieve all indexed paths from the database."""
        if self.conn is None:
            raise RuntimeError("Database not initialized")

        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT path FROM files ORDER BY filename")
            return [row[0] for row in cursor.fetchall()]

    def get_all_files(self) -> List[str]:
        """Alias for get_all_paths() for backward compatibility."""
        return self.get_all_paths()

    def search_files(self, pattern: str) -> List[str]:
        """Search for files matching a pattern (SQL LIKE on filename/path)."""
        if self.conn is None:
            raise RuntimeError("Database not initialized")

        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT path FROM files WHERE filename LIKE ? OR path LIKE ? ORDER BY filename",
                (f"%{pattern}%", f"%{pattern}%")
            )
            return [row[0] for row in cursor.fetchall()]

    def search(self, pattern: str, limit: Optional[int] = None) -> List[str]:
        """Compatibility wrapper for older API expecting `search`.

        Args:
            pattern: search substring or pattern
            limit: optional result limit (returns first `limit` matches)
        """
        results = self.search_files(pattern)
        if limit is not None:
            return results[:limit]
        return results

    def clear_index(self) -> None:
        """Clear all entries from the index."""
        if self.conn is None:
            raise RuntimeError("Database not initialized")

        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM files")
            self.conn.commit()
            logger.info("Index cleared")

    def close(self) -> None:
        """Close the database connection."""
        with self._lock:
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed")

    def scan_directory(self, root_path: str, exclude_patterns: Optional[List[str]] = None,
                       filters: Optional[Iterable[str]] = None,
                       excludes: Optional[Iterable[str]] = None,
                       progress_callback: Optional[Callable[[int, str], None]] = None,
                       stop_event: Optional[object] = None) -> Generator[dict, None, None]:
        """Recursively scan a directory and yield file information.

        Args:
            root_path: Root directory to scan
            exclude_patterns: List of directory/file patterns to exclude (name based)
            filters: Iterable of filename patterns or extensions to include
            excludes: Iterable of absolute path prefixes to exclude
            progress_callback: optional callable(indexed_count, current_path)
            stop_event: optional object with is_set() to cancel scan

        Yields:
            dict with keys: path, filename, size, modified
        """
        if exclude_patterns is None:
            exclude_patterns = ['.git', '__pycache__', '.venv', 'venv', 'node_modules']

        excludes_resolved: List[str] = []
        if excludes:
            for e in excludes:
                try:
                    excludes_resolved.append(str(Path(e).expanduser().resolve()))
                except Exception:
                    excludes_resolved.append(str(Path(e).expanduser()))

        root = Path(root_path).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            logger.error(f"Path is not a directory or does not exist: {root}")
            return

        indexed = 0
        for dirpath, dirnames, filenames in os.walk(root):
            # filter out name-based excludes
            dirnames[:] = [d for d in dirnames if d not in exclude_patterns]

            # filter out directory entries under excluded prefixes
            if excludes_resolved:
                kept = []
                for d in dirnames:
                    try:
                        absd = str((Path(dirpath) / d).resolve())
                    except Exception:
                        absd = str((Path(dirpath) / d).absolute())
                    if any(absd.startswith(ex) for ex in excludes_resolved):
                        continue
                    kept.append(d)
                dirnames[:] = kept

            for fname in filenames:
                # allow stop via event-like object
                if stop_event is not None:
                    try:
                        if getattr(stop_event, 'is_set', lambda: False)():
                            return
                    except Exception:
                        pass

                fp = Path(dirpath) / fname

                # skip files under excluded prefixes
                if excludes_resolved:
                    try:
                        absfp = str(fp.resolve())
                    except Exception:
                        absfp = str(fp.absolute())
                    if any(absfp.startswith(ex) for ex in excludes_resolved):
                        continue

                # apply filters if provided
                if filters:
                    matched = False
                    for f in filters:
                        f = f.strip()
                        if not f:
                            continue
                        if any(ch in f for ch in '*?['):
                            if fnmatch.fnmatch(fname, f):
                                matched = True
                                break
                        else:
                            # treat as extension
                            norm = f if f.startswith('.') else f'.{f}'
                            if fname.lower().endswith(norm.lower()):
                                matched = True
                                break
                    if not matched:
                        continue

                try:
                    st = fp.stat()
                except (OSError, PermissionError) as e:
                    logger.debug(f"Skipping inaccessible file {fp}: {e}")
                    continue

                indexed += 1
                if progress_callback:
                    try:
                        progress_callback(indexed, str(fp))
                    except Exception:
                        pass

                yield {
                    'path': str(fp),
                    'filename': fname,
                    'size': st.st_size,
                    'modified': st.st_mtime
                }

    def index_directory(self, root_path: Union[str, Iterable[str]], exclude_patterns: Optional[List[str]] = None,
                        filters: Optional[Iterable[str]] = None,
                        excludes: Optional[Iterable[str]] = None,
                        progress_callback: Optional[Callable[[int, str], None]] = None,
                        stop_event: Optional[object] = None) -> int:
        """Index files from root_path into the SQLite database.

        Returns the number of files indexed.
        """
        if self.conn is None:
            raise RuntimeError("Database not initialized")
        # Accept either a single path (str/Path) or an iterable of paths
        if isinstance(root_path, (str, Path)):
            paths = [root_path]
        else:
            try:
                paths = list(root_path)
            except Exception:
                raise TypeError("root_path must be a string path or an iterable of paths")

        total_indexed = 0
        current_time = datetime.now().timestamp()

        # Iterate over each provided path and index files
        for p in paths:
            with self._lock:
                cursor = self.conn.cursor()
                indexed_count = 0

                for info in self.scan_directory(p, exclude_patterns=exclude_patterns,
                                                filters=filters, excludes=excludes,
                                                progress_callback=progress_callback,
                                                stop_event=stop_event):
                    try:
                        cursor.execute(
                            "INSERT OR REPLACE INTO files (path, filename, size, modified, indexed_at) VALUES (?, ?, ?, ?, ?)",
                            (info['path'], info['filename'], info['size'], info['modified'], current_time)
                        )
                        indexed_count += 1
                        total_indexed += 1

                        if indexed_count % 1000 == 0:
                            self.conn.commit()
                            logger.info(f"Indexed {indexed_count} files for {p}...")

                    except sqlite3.Error as e:
                        logger.error(f"Database error for {info.get('path')}: {e}")
                        continue

                self.conn.commit()
                logger.info(f"Indexing complete for {p}. Files indexed: {indexed_count}")

        logger.info(f"Indexing complete. Total files indexed: {total_indexed}")
        return total_indexed

    def index(self, root_path: str, **kwargs) -> int:
        """Alias for index_directory() for backward compatibility."""
        return self.index_directory(root_path, **kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    idx = FileIndexer()
    count = idx.index_directory('.')
    print(f"Indexed {count} files")
    matches = idx.search_files('.py')
    print(f"Found {len(matches)} matches for .py")
    idx.close()
