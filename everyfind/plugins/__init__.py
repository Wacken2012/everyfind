#!/usr/bin/env python3
"""Plugin interface and loader for Everyfind."""
from __future__ import annotations

from typing import Protocol, Dict, Any, List
import importlib
import pkgutil
from pathlib import Path


class EveryfindPlugin(Protocol):
    """Protocol that plugins should follow."""

    def metadata(self) -> Dict[str, Any]:
        ...

    def run(self, *args, **kwargs) -> Any:
        ...


def load_plugins() -> List[EveryfindPlugin]:
    """Dynamically load plugins from the everyfind.plugins package.

    Returns a list of plugin modules or objects that implement the protocol.
    """
    plugins = []
    package = 'everyfind.plugins'
    for finder, name, ispkg in pkgutil.iter_modules(importlib.import_module(package).__path__):
        try:
            mod = importlib.import_module(f"{package}.{name}")
            if hasattr(mod, 'Plugin'):
                plugins.append(mod.Plugin())
        except Exception:
            continue
    return plugins
