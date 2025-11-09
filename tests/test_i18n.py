#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Everyfind
# Copyright (C) 2025 Stefan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
Tests for internationalization (i18n) functionality.

Verifies that gettext correctly loads and uses translation files.
"""

import os
import locale
import gettext
import pytest


def test_locale_files_exist():
    """Test that .mo files exist in locale directory."""
    locales = ["de", "en", "fr", "es", "pl"]
    for locale_code in locales:
        mo_path = os.path.join("locale", locale_code, "LC_MESSAGES", "everyfind.mo")
        assert os.path.exists(mo_path), f"{locale_code.upper()} .mo file not found at {mo_path}"


def test_gettext_german_translation():
    """Test that German translations load correctly."""
    # Set locale directory
    locale_dir = os.path.abspath("locale")
    
    # Create German translation instance
    de_trans = gettext.translation('everyfind', localedir=locale_dir, languages=['de'])
    _ = de_trans.gettext
    
    # Test a known translation
    # "Settings" in English should be "Einstellungen" in German
    translated = _("Settings")
    
    # If translation file is correctly loaded and contains this string,
    # it should return the German translation
    # Note: This test assumes "Settings" is in the .po file
    # For now, test with strings we know are in everyfind.po
    
    # Test with "Cancel" which should be "Abbrechen"
    cancel_translation = _("Cancel")
    assert cancel_translation == "Abbrechen", \
        f"Expected 'Abbrechen' but got '{cancel_translation}'"


def test_gettext_english_translation():
    """Test that English translations load correctly."""
    locale_dir = os.path.abspath("locale")
    
    # Create English translation instance
    en_trans = gettext.translation('everyfind', localedir=locale_dir, languages=['en'])
    _ = en_trans.gettext
    
    # English translations should match the original strings
    cancel_translation = _("Cancel")
    assert cancel_translation == "Cancel", \
        f"Expected 'Cancel' but got '{cancel_translation}'"


def test_i18n_module_initialization():
    """Test that the i18n module initializes correctly."""
    try:
        from everyfind import i18n
        
        # The module should have init_gettext function
        assert hasattr(i18n, 'init_gettext'), "i18n module should have 'init_gettext' function"
        
        # Initialize with German
        i18n.init_gettext('de')
        
        # After initialization, _ should be available in builtins
        import builtins
        assert hasattr(builtins, '_'), "After init_gettext, '_' should be in builtins"
        
        # Test that calling the function works
        result = _("Cancel")  # noqa: F821
        assert isinstance(result, str), "Translation function should return a string"
        assert result == "Abbrechen", f"Expected 'Abbrechen' but got '{result}'"
        
    except ImportError as e:
        pytest.skip(f"i18n module not available: {e}")


def test_translation_with_format_string():
    """Test that format strings in translations work correctly."""
    locale_dir = os.path.abspath("locale")
    
    de_trans = gettext.translation('everyfind', localedir=locale_dir, languages=['de'])
    _ = de_trans.gettext
    
    # Test "Indexing: {filename}" which should be "Indexiere: {filename}" in German
    template = _("Indexing: {filename}")
    assert "{filename}" in template, "Format placeholder should be preserved"
    
    # Test that formatting works
    formatted = template.format(filename="test.txt")
    assert "test.txt" in formatted, "Formatted string should contain filename"


def test_missing_translation_fallback():
    """Test that missing translations fall back to original string."""
    locale_dir = os.path.abspath("locale")
    
    de_trans = gettext.translation('everyfind', localedir=locale_dir, languages=['de'])
    _ = de_trans.gettext
    
    # Use a string that definitely doesn't exist in translations
    non_existent = _("This string does not exist in any .po file xyz123")
    
    # Should return the original string as fallback
    assert non_existent == "This string does not exist in any .po file xyz123", \
        "Missing translations should fall back to original string"


def test_gettext_french_translation():
    """Test that French translations load correctly."""
    locale_dir = os.path.abspath("locale")
    
    fr_trans = gettext.translation('everyfind', localedir=locale_dir, languages=['fr'])
    _ = fr_trans.gettext
    
    # Test "Cancel" which should be "Annuler" in French
    cancel_translation = _("Cancel")
    assert cancel_translation == "Annuler", \
        f"Expected 'Annuler' but got '{cancel_translation}'"


def test_gettext_spanish_translation():
    """Test that Spanish translations load correctly."""
    locale_dir = os.path.abspath("locale")
    
    es_trans = gettext.translation('everyfind', localedir=locale_dir, languages=['es'])
    _ = es_trans.gettext
    
    # Test "Cancel" which should be "Cancelar" in Spanish
    cancel_translation = _("Cancel")
    assert cancel_translation == "Cancelar", \
        f"Expected 'Cancelar' but got '{cancel_translation}'"


def test_gettext_polish_translation():
    """Test that Polish translations load correctly."""
    locale_dir = os.path.abspath("locale")
    
    pl_trans = gettext.translation('everyfind', localedir=locale_dir, languages=['pl'])
    _ = pl_trans.gettext
    
    # Test "Cancel" which should be "Anuluj" in Polish
    cancel_translation = _("Cancel")
    assert cancel_translation == "Anuluj", \
        f"Expected 'Anuluj' but got '{cancel_translation}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
