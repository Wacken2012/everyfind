#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Everyfind - Indexer Filter/Exclude Tests
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

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from everyfind.indexer import FileIndexer


class TestIndexerFilters(unittest.TestCase):
    """Test cases for FileIndexer filter and exclude functionality."""
    
    def setUp(self):
        """Create a temporary directory with test files."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        
        # Create test file structure
        # Root level files
        (self.root / "document.txt").write_text("test content")
        (self.root / "image.jpg").write_text("fake image")
        (self.root / "report.pdf").write_text("fake pdf")
        (self.root / "script.py").write_text("print('hello')")
        (self.root / "data.json").write_text("{}")
        
        # Subdirectories
        docs_dir = self.root / "documents"
        docs_dir.mkdir()
        (docs_dir / "file1.txt").write_text("content 1")
        (docs_dir / "file2.pdf").write_text("content 2")
        (docs_dir / "photo.jpg").write_text("photo")
        
        code_dir = self.root / "code"
        code_dir.mkdir()
        (code_dir / "main.py").write_text("main")
        (code_dir / "utils.py").write_text("utils")
        (code_dir / "config.json").write_text("{}")
        
        # Directories to simulate exclusions
        mnt_dir = self.root / "mnt"
        mnt_dir.mkdir()
        (mnt_dir / "external.txt").write_text("should be excluded")
        
        media_dir = self.root / "media"
        media_dir.mkdir()
        (media_dir / "usb.txt").write_text("should be excluded")
        
        # Hidden directory
        hidden_dir = self.root / ".cache"
        hidden_dir.mkdir()
        (hidden_dir / "temp.txt").write_text("cache file")
        
        # Create indexer with in-memory database
        self.indexer = FileIndexer(":memory:")
    
    def tearDown(self):
        """Clean up temporary directory and indexer."""
        self.indexer.close()
        self.temp_dir.cleanup()
    
    def test_no_filters_indexes_all(self):
        """Test that without filters, all files are indexed."""
        count = self.indexer.index_directory(str(self.root))
        
        # Should index all files (excluding default patterns like .cache)
        # Root: 5 files + documents: 3 + code: 3 + mnt: 1 + media: 1 = 13
        self.assertGreaterEqual(count, 13)
        
        paths = self.indexer.get_all_paths()
        # Verify we have files from different locations
        self.assertTrue(any("document.txt" in p for p in paths))
        self.assertTrue(any("script.py" in p for p in paths))
        self.assertTrue(any("image.jpg" in p for p in paths))
    
    def test_filter_single_extension(self):
        """Test filtering for a single file extension."""
        count = self.indexer.index_directory(str(self.root), filters=[".txt"])
        
        paths = self.indexer.get_all_paths()
        
        # Should only have .txt files
        # Root: 1 + documents: 1 + mnt: 1 + media: 1 + .cache: 1 = 5
        self.assertEqual(count, 5)
        self.assertTrue(all(p.endswith(".txt") for p in paths))
        
        # Verify specific files
        self.assertTrue(any("document.txt" in p for p in paths))
        self.assertTrue(any("file1.txt" in p for p in paths))
    
    def test_filter_wildcard_pattern(self):
        """Test filtering with wildcard patterns."""
        count = self.indexer.index_directory(str(self.root), filters=["*.py"])
        
        paths = self.indexer.get_all_paths()
        
        # Should only have .py files: root: 1 + code: 2 = 3
        self.assertEqual(count, 3)
        self.assertTrue(all(p.endswith(".py") for p in paths))
        
        # Verify we got the Python files
        self.assertTrue(any("script.py" in p for p in paths))
        self.assertTrue(any("main.py" in p for p in paths))
        self.assertTrue(any("utils.py" in p for p in paths))
    
    def test_filter_multiple_extensions(self):
        """Test filtering with multiple file extensions."""
        count = self.indexer.index_directory(str(self.root), filters=[".txt", ".pdf"])
        
        paths = self.indexer.get_all_paths()
        
        # .txt: 5 + .pdf: 2 = 7
        self.assertEqual(count, 7)
        self.assertTrue(all(p.endswith((".txt", ".pdf")) for p in paths))
    
    def test_filter_mixed_patterns(self):
        """Test filtering with mixed wildcard and extension patterns."""
        count = self.indexer.index_directory(str(self.root), filters=["*.py", ".json"])
        
        paths = self.indexer.get_all_paths()
        
        # .py: 3 + .json: 2 = 5
        self.assertEqual(count, 5)
        self.assertTrue(all(p.endswith((".py", ".json")) for p in paths))
    
    def test_exclude_single_path(self):
        """Test excluding a single directory path."""
        mnt_path = str(self.root / "mnt")
        count = self.indexer.index_directory(str(self.root), excludes=[mnt_path])
        
        paths = self.indexer.get_all_paths()
        
        # Should not contain any files from mnt directory
        self.assertFalse(any("mnt" in p for p in paths))
        self.assertFalse(any("external.txt" in p for p in paths))
        
        # Should contain files from other directories
        self.assertTrue(any("document.txt" in p for p in paths))
        self.assertTrue(any("media" in p for p in paths))
    
    def test_exclude_multiple_paths(self):
        """Test excluding multiple directory paths."""
        mnt_path = str(self.root / "mnt")
        media_path = str(self.root / "media")
        count = self.indexer.index_directory(str(self.root), excludes=[mnt_path, media_path])
        
        paths = self.indexer.get_all_paths()
        
        # Should not contain any files from excluded directories
        self.assertFalse(any("mnt" in p for p in paths))
        self.assertFalse(any("media" in p for p in paths))
        self.assertFalse(any("external.txt" in p for p in paths))
        self.assertFalse(any("usb.txt" in p for p in paths))
        
        # Should still have other files
        self.assertTrue(any("document.txt" in p for p in paths))
    
    def test_exclude_with_prefix(self):
        """Test excluding paths by prefix matching."""
        # Use just "mnt" as exclude - should match any path containing /mnt/
        mnt_prefix = str(self.root / "mnt")
        count = self.indexer.index_directory(str(self.root), excludes=[mnt_prefix])
        
        paths = self.indexer.get_all_paths()
        
        # No files from mnt
        self.assertFalse(any(mnt_prefix in p for p in paths))
    
    def test_combined_filters_and_excludes(self):
        """Test combining filters and excludes."""
        mnt_path = str(self.root / "mnt")
        count = self.indexer.index_directory(
            str(self.root), 
            filters=[".txt"], 
            excludes=[mnt_path]
        )
        
        paths = self.indexer.get_all_paths()
        
        # Should only have .txt files AND not from mnt
        self.assertTrue(all(p.endswith(".txt") for p in paths))
        self.assertFalse(any("mnt" in p for p in paths))
        self.assertFalse(any("external.txt" in p for p in paths))
        
        # Should have other .txt files
        self.assertTrue(any("document.txt" in p for p in paths))
        self.assertTrue(any("file1.txt" in p for p in paths))
    
    def test_default_exclude_patterns(self):
        """Test that default patterns like __pycache__ are excluded."""
        # Create __pycache__ directory
        pycache_dir = self.root / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "test.pyc").write_text("bytecode")
        
        count = self.indexer.index_directory(str(self.root))
        
        paths = self.indexer.get_all_paths()
        
        # Should not index files in __pycache__ (default exclude pattern)
        self.assertFalse(any("__pycache__" in p for p in paths))
        self.assertFalse(any("test.pyc" in p for p in paths))
    
    def test_progress_callback(self):
        """Test that progress callback is called during indexing."""
        call_count = 0
        indexed_paths = []
        
        def progress_cb(count, path):
            nonlocal call_count
            call_count += 1
            if path:
                indexed_paths.append(path)
        
        count = self.indexer.index_directory(
            str(self.root),
            progress_callback=progress_cb
        )
        
        # Progress callback should have been called
        self.assertGreater(call_count, 0)
        self.assertGreater(len(indexed_paths), 0)
        
        # Should have indexed multiple files
        self.assertGreater(count, 0)
    
    def test_stop_event_cancellation(self):
        """Test that indexing can be cancelled with stop_event."""
        import threading
        
        stop_event = threading.Event()
        indexed_count = [0]
        
        def progress_cb(count, path):
            indexed_count[0] = count
            # Cancel after indexing a few files
            if count >= 3:
                stop_event.set()
        
        count = self.indexer.index_directory(
            str(self.root),
            progress_callback=progress_cb,
            stop_event=stop_event
        )
        
        # Should have stopped early
        # Total files available is ~13, we should stop around 3-5
        self.assertLess(count, 10)
        self.assertTrue(stop_event.is_set())
    
    def test_empty_filters_list(self):
        """Test that empty filters list indexes all files."""
        count_no_filter = self.indexer.index_directory(str(self.root))
        
        self.indexer.clear_index()
        
        count_empty_filter = self.indexer.index_directory(str(self.root), filters=[])
        
        # Both should index same number of files
        self.assertEqual(count_no_filter, count_empty_filter)
    
    def test_empty_excludes_list(self):
        """Test that empty excludes list doesn't exclude anything."""
        count_no_exclude = self.indexer.index_directory(str(self.root))
        
        self.indexer.clear_index()
        
        count_empty_exclude = self.indexer.index_directory(str(self.root), excludes=[])
        
        # Both should index same number of files
        self.assertEqual(count_no_exclude, count_empty_exclude)
    
    def test_nonexistent_filter(self):
        """Test filtering for extension that doesn't exist."""
        count = self.indexer.index_directory(str(self.root), filters=[".xyz"])
        
        # Should index 0 files
        self.assertEqual(count, 0)
        
        paths = self.indexer.get_all_paths()
        self.assertEqual(len(paths), 0)
    
    def test_case_sensitivity(self):
        """Test that file extensions are case-insensitive."""
        # Create file with uppercase extension
        (self.root / "README.TXT").write_text("readme")
        
        count = self.indexer.index_directory(str(self.root), filters=[".txt"])
        
        paths = self.indexer.get_all_paths()
        
        # Should match both .txt and .TXT
        self.assertTrue(any("README.TXT" in p for p in paths))


if __name__ == "__main__":
    unittest.main()
