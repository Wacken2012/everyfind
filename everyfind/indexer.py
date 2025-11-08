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
from pathlib import Path
from typing import Optional, Generator
from datetime import datetime

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
            db_path = config_dir / "index.db"
        
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the SQLite database with required schema."""
        self.conn = sqlite3.connect(str(self.db_path))
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
    
    def scan_directory(self, root_path: str, exclude_patterns: Optional[list] = None) -> Generator[dict, None, None]:
        """
        Recursively scan a directory and yield file information.
        
        Args:
            root_path: Root directory to scan
            exclude_patterns: List of directory/file patterns to exclude (e.g., ['.git', '__pycache__'])
        
        Yields:
            Dictionary with file information (path, filename, size, modified)
        """
        if exclude_patterns is None:
            exclude_patterns = ['.git', '__pycache__', '.venv', 'venv', 'node_modules']
        
        root_path = Path(root_path).resolve()
        
        if not root_path.exists():
            logger.error(f"Path does not exist: {root_path}")
            return
        
        if not root_path.is_dir():
            logger.error(f"Path is not a directory: {root_path}")
            return
        
        logger.info(f"Starting scan of {root_path}")
        
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Filter out excluded directories
            dirnames[:] = [d for d in dirnames if d not in exclude_patterns]
            
            for filename in filenames:
                try:
                    filepath = Path(dirpath) / filename
                    stat = filepath.stat()
                    
                    yield {
                        'path': str(filepath),
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    }
                except (OSError, PermissionError) as e:
                    logger.warning(f"Cannot access {filepath}: {e}")
                    continue
    
    def index_directory(self, root_path: str, exclude_patterns: Optional[list] = None) -> int:
        """
        Index all files in a directory and store in database.
        
        Args:
            root_path: Root directory to index
            exclude_patterns: List of directory/file patterns to exclude
        
        Returns:
            Number of files indexed
        """
        if self.conn is None:
            raise RuntimeError("Database not initialized")
        
        cursor = self.conn.cursor()
        indexed_count = 0
        current_time = datetime.now().timestamp()
        
        for file_info in self.scan_directory(root_path, exclude_patterns):
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO files (path, filename, size, modified, indexed_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    file_info['path'],
                    file_info['filename'],
                    file_info['size'],
                    file_info['modified'],
                    current_time
                ))
                indexed_count += 1
                
                if indexed_count % 1000 == 0:
                    self.conn.commit()
                    logger.info(f"Indexed {indexed_count} files...")
                
            except sqlite3.Error as e:
                logger.error(f"Database error for {file_info['path']}: {e}")
                continue
        
        self.conn.commit()
        logger.info(f"Indexing complete. Total files indexed: {indexed_count}")
        return indexed_count
    
    def get_all_paths(self) -> list[str]:
        """
        Retrieve all file paths from the database.
        
        Returns:
            List of all indexed file paths
        """
        if self.conn is None:
            raise RuntimeError("Database not initialized")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT path FROM files ORDER BY filename")
        return [row[0] for row in cursor.fetchall()]
    
    def search_files(self, pattern: str) -> list[str]:
        """
        Search for files matching a pattern (SQL LIKE).
        
        Args:
            pattern: Search pattern (supports SQL wildcards %)
        
        Returns:
            List of matching file paths
        """
        if self.conn is None:
            raise RuntimeError("Database not initialized")
        
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT path FROM files WHERE filename LIKE ? OR path LIKE ? ORDER BY filename",
            (f"%{pattern}%", f"%{pattern}%")
        )
        return [row[0] for row in cursor.fetchall()]
    
    def clear_index(self) -> None:
        """Clear all entries from the index."""
        if self.conn is None:
            raise RuntimeError("Database not initialized")
        
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM files")
        self.conn.commit()
        logger.info("Index cleared")
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    indexer = FileIndexer()
    
    # Index current directory
    count = indexer.index_directory(".")
    print(f"Indexed {count} files")
    
    # Search example
    results = indexer.search_files("*.py")
    print(f"Found {len(results)} Python files")
    
    indexer.close()
