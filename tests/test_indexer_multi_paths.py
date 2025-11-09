import os
import tempfile
from everyfind.indexer import FileIndexer


def test_indexer_indexes_multiple_paths(tmp_path):
    # Create two directories with files
    dir1 = tmp_path / "dir1"
    dir2 = tmp_path / "dir2"
    dir1.mkdir()
    dir2.mkdir()

    f1 = dir1 / "file1.txt"
    f2 = dir2 / "file2.txt"
    f1.write_text("hello")
    f2.write_text("world")

    # Use a temporary sqlite database file
    db_fd, db_path = tempfile.mkstemp(prefix="everyfind-test-", suffix=".db")
    os.close(db_fd)

    indexer = None
    try:
        indexer = FileIndexer(db_path)
        # Pass a list of paths (this used to raise a TypeError)
        total = indexer.index_directory([str(dir1), str(dir2)])

        # Should have indexed both files (total >= 2)
        all_paths = indexer.get_all_paths()
        assert any(str(f1) in p for p in all_paths), "file1 not indexed"
        assert any(str(f2) in p for p in all_paths), "file2 not indexed"
        assert total >= 2
    finally:
        if indexer is not None:
            try:
                indexer.close()
            except Exception:
                pass
        if os.path.exists(db_path):
            os.unlink(db_path)
