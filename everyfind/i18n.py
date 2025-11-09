#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i18n helper for Everyfind

Initializes gettext translations using the local `locale/` directory.
"""
from __future__ import annotations

import gettext
from pathlib import Path
from typing import Optional

LOCALE_DIR = Path(__file__).parent.parent / "locale"
DOMAIN = "everyfind"


def init_gettext(language: Optional[str] = None):
    """Initialize gettext translation.

    Args:
        language: language code (e.g. 'de', 'en') or 'system' to use system locale.
    """
    try:
        if language and language != "system":
            t = gettext.translation(DOMAIN, localedir=str(LOCALE_DIR), languages=[language], fallback=True)
            t.install()
        else:
            # Use system locale; install will raise if domain not found, so catch below
            gettext.install(DOMAIN, localedir=str(LOCALE_DIR))
    except Exception:
        # Fallback to basic installation (no translations)
        gettext.install(DOMAIN)


__all__ = ["init_gettext"]
