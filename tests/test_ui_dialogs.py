#!/usr/bin/env python3
"""Unit tests for UI dialogs (SettingsDialog and IndexProgressDialog).

These tests avoid launching GTK windows by monkeypatching constructors where
necessary and exercising the dialog data handling logic.
"""
import pytest

from everyfind import ui_settings


def test_settingsdialog_get_settings_monkeypatched(monkeypatch):
    # Prevent real __init__ from running (which would call GTK show_all)
    monkeypatch.setattr(ui_settings.SettingsDialog, "__init__", lambda self, parent, settings: None)

    dlg = ui_settings.SettingsDialog(None, {})

    # Provide minimal attributes the get_settings() expects
    dlg.dir_store = [("/tmp/foo",), ("/home/user",)]

    class FakeEntry:
        def __init__(self, text):
            self._text = text

        def get_text(self):
            return self._text

    dlg.filters_entry = FakeEntry("*.py, .txt")
    dlg.exclude_entry = FakeEntry("/mnt,/media")

    class FakeCheck:
        def get_active(self):
            return True

    dlg.auto_reindex_check = FakeCheck()

    class FakeSpin:
        def get_value(self):
            return 15

    dlg.interval_spin = FakeSpin()

    class FakeCombo:
        def get_active_text(self):
            return "de"

    dlg.lang_combo = FakeCombo()

    settings = dlg.get_settings()

    assert settings["indexed_paths"] == ["/tmp/foo", "/home/user"]
    assert settings["file_filters"] == ["*.py", ".txt"]
    assert settings["excluded_paths"] == ["/mnt", "/media"]
    assert settings["auto_reindex"] is True
    assert settings["reindex_interval_minutes"] == 15
    assert settings["language"] == "de"


def test_progress_dialog_api(monkeypatch):
    # Import here to ensure GTK is available in environment where tests run
    from everyfind.ui import IndexProgressDialog

    # Monkeypatch GTK dialog methods that would require a running main loop
    monkeypatch.setattr(IndexProgressDialog, 'show_all', lambda self: None)

    dlg = IndexProgressDialog(None)

    # Simulate progress updates (should not raise)
    dlg.update_progress(1, "/tmp/file1.txt")
    dlg.update_progress(2, "/tmp/file2.txt")

    # Test cancellation
    dlg._on_cancel(None)
    assert dlg.stop_event.is_set()
    assert dlg.cancelled is True
