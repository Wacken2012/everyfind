#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Everyfind - Search Backend Module
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

import logging
from typing import Optional, List
from pathlib import Path

try:
    from iterfzf import iterfzf
except ImportError:
    iterfzf = None

logger = logging.getLogger(__name__)


class FzfSearchBackend:
    """Wrapper for fzf-based fuzzy search with PTY support."""
    
    def __init__(self):
        """Initialize the fzf search backend."""
        if iterfzf is None:
            raise ImportError(
                "iterfzf (fzf-py) is not installed. "
                "Install it with: pip install iterfzf"
            )
    
    def search(
        self,
        items: List[str],
        multi: bool = False,
        prompt: str = "Search: ",
        preview: Optional[str] = None,
        query: str = ""
    ) -> Optional[str | List[str]]:
        """
        Perform fuzzy search using fzf.
        
        Args:
            items: List of items to search through
            multi: Allow multiple selections
            prompt: Prompt text to display
            preview: Preview command (e.g., "cat {}")
            query: Initial query string
        
        Returns:
            Selected item(s) or None if cancelled
        """
        if not items:
            logger.warning("No items to search")
            return None
        
        try:
            result = iterfzf(
                items,
                multi=multi,
                prompt=prompt,
                preview=preview,
                query=query,
                exact=False,
                case_sensitive=False
            )
            return result
        except Exception as e:
            logger.error(f"fzf search error: {e}")
            return None
    
    def search_files(
        self,
        file_paths: List[str],
        multi: bool = False,
        query: str = ""
    ) -> Optional[str | List[str]]:
        """
        Search through file paths with optimized display.
        
        Args:
            file_paths: List of file paths to search
            multi: Allow multiple selections
            query: Initial query string
        
        Returns:
            Selected file path(s) or None if cancelled
        """
        if not file_paths:
            logger.warning("No file paths to search")
            return None
        
        # Convert to Path objects for better display
        display_items = []
        for path_str in file_paths:
            path = Path(path_str)
            # Show filename prominently with directory path
            display = f"{path.name} ({path.parent})"
            display_items.append((display, path_str))
        
        # Extract display strings for fzf
        display_list = [item[0] for item in display_items]
        
        try:
            result = iterfzf(
                display_list,
                multi=multi,
                prompt="Files: ",
                query=query,
                exact=False,
                case_sensitive=False,
                preview="cat -n {}" if self._has_command("cat") else None
            )
            
            if result is None:
                return None
            
            # Map back to original paths
            if multi and isinstance(result, list):
                selected_indices = [display_list.index(r) for r in result]
                return [display_items[i][1] for i in selected_indices]
            else:
                selected_index = display_list.index(result)
                return display_items[selected_index][1]
                
        except Exception as e:
            logger.error(f"File search error: {e}")
            return None
    
    @staticmethod
    def _has_command(cmd: str) -> bool:
        """Check if a command is available in PATH."""
        import shutil
        return shutil.which(cmd) is not None


class SimpleSearchBackend:
    """Simple fallback search backend without fzf."""
    
    def search(
        self,
        items: List[str],
        multi: bool = False,
        prompt: str = "Search: ",
        query: str = ""
    ) -> Optional[str | List[str]]:
        """
        Simple CLI-based search (fallback when fzf is not available).
        
        Args:
            items: List of items to search through
            multi: Allow multiple selections
            prompt: Prompt text to display
            query: Initial query string
        
        Returns:
            Selected item(s) or None if cancelled
        """
        if not items:
            return None
        
        print(f"\n{prompt}")
        search_term = input(f"Enter search term [{query}]: ").strip() or query
        
        if not search_term:
            return None
        
        # Simple case-insensitive substring matching
        matches = [item for item in items if search_term.lower() in item.lower()]
        
        if not matches:
            print("No matches found.")
            return None
        
        print(f"\nFound {len(matches)} matches:")
        for i, match in enumerate(matches[:20], 1):  # Show first 20
            print(f"{i}. {match}")
        
        if len(matches) > 20:
            print(f"... and {len(matches) - 20} more")
        
        try:
            selection = input("\nSelect number (or 'q' to quit): ").strip()
            if selection.lower() == 'q':
                return None
            
            index = int(selection) - 1
            if 0 <= index < len(matches):
                return matches[index]
            else:
                print("Invalid selection.")
                return None
        except (ValueError, IndexError):
            print("Invalid input.")
            return None


def get_search_backend() -> FzfSearchBackend | SimpleSearchBackend:
    """
    Get the appropriate search backend.
    
    Returns:
        FzfSearchBackend if available, otherwise SimpleSearchBackend
    """
    try:
        return FzfSearchBackend()
    except ImportError:
        logger.warning("fzf not available, using simple search backend")
        return SimpleSearchBackend()


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    backend = get_search_backend()
    
    test_items = [
        "/home/user/Documents/project.txt",
        "/home/user/Pictures/photo.jpg",
        "/home/user/Downloads/archive.zip",
        "/etc/config/settings.conf"
    ]
    
    result = backend.search(test_items, prompt="Test search: ")
    print(f"Selected: {result}")
