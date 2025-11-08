# -*- coding: utf-8 -*-
"""
Test for FileIndexer: creates a temporary directory with files and verifies indexing.
"""
from pathlib import Path

import pytest

from everyfind.indexer import FileIndexer


def test_indexer_creates_entries(tmp_path):
    # Create temp dir structure
    d = tmp_path / "data"
    d.mkdir()

    file_paths = []
    for i in range(5):
        p = d / f"file_{i}.txt"
        p.write_text(f"content {i}\n", encoding="utf-8")
        file_paths.append(str(p))

    # Use a temp database inside tmp_path
    db_path = tmp_path / "test_index.db"

    indexer = FileIndexer(db_path=str(db_path))

    try:
        count = indexer.index_directory(str(d))
        assert count == 5

        all_paths = indexer.get_all_paths()
        # Ensure all files are indexed
        for p in file_paths:
            assert p in all_paths
    finally:
        indexer.close()
