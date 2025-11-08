#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings loader/saver for Everyfind
Copyright (C) 2025 Stefan

This module manages persistent settings stored in JSON under
XDG_CONFIG_HOME/everyfind/settings.json (falls back to ~/.config/everyfind).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
import os


DEFAULT_SETTINGS: Dict[str, Any] = {
    "indexed_paths": [],  # list of directories to index
    "file_filters": ["*"],  # e.g. ["*.pdf","*.txt"]
    "excluded_paths": ["/media","/mnt"],
    "auto_reindex": False,
    "reindex_interval_minutes": 60,
    "language": "system",
}


def get_config_dir() -> Path:
    """Return the configuration directory path for everyfind.

    Uses XDG_CONFIG_HOME if set, otherwise ~/.config
    """
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "everyfind"
    return Path.home() / ".config" / "everyfind"


def get_settings_path() -> Path:
    return get_config_dir() / "settings.json"


def load_settings() -> Dict[str, Any]:
    """Load settings from JSON, merging with defaults."""
    path = get_settings_path()
    settings = DEFAULT_SETTINGS.copy()

    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    settings.update(data)
    except Exception:
        # If anything goes wrong, just return defaults
        pass

    return settings


def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings dict to JSON, creating directories as needed."""
    path = get_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def reset_settings() -> None:
    """Remove the settings file so defaults will be used next load."""
    path = get_settings_path()
    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass
