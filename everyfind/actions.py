#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Everyfind - Actions Module
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
import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FileActions:
    """File operations: open, terminal, copy path, show details."""
    
    @staticmethod
    def open_file(file_path: str) -> bool:
        """
        Open a file with the default application.
        
        Args:
            file_path: Path to the file to open
        
        Returns:
            True if successful, False otherwise
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"File does not exist: {file_path}")
            return False
        
        try:
            if os.name == 'posix':  # Linux/Unix
                subprocess.Popen(['xdg-open', str(path)])
            elif os.name == 'nt':  # Windows
                os.startfile(str(path))
            else:
                logger.error(f"Unsupported OS: {os.name}")
                return False
            
            logger.info(f"Opened file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to open file {file_path}: {e}")
            return False
    
    @staticmethod
    def open_in_terminal(file_path: str, terminal: Optional[str] = None) -> bool:
        """
        Open a terminal in the directory containing the file.
        
        Args:
            file_path: Path to the file
            terminal: Terminal emulator to use (auto-detect if None)
        
        Returns:
            True if successful, False otherwise
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"Path does not exist: {file_path}")
            return False
        
        # Use parent directory if path is a file
        directory = path.parent if path.is_file() else path
        
        try:
            if terminal is None:
                # Auto-detect terminal
                terminals = [
                    'gnome-terminal',
                    'konsole',
                    'xfce4-terminal',
                    'xterm',
                    'terminator',
                    'alacritty',
                    'kitty'
                ]
                
                for term in terminals:
                    if FileActions._has_command(term):
                        terminal = term
                        break
                
                if terminal is None:
                    logger.error("No terminal emulator found")
                    return False
            
            # Different terminals have different syntax
            if terminal in ['gnome-terminal', 'terminator']:
                subprocess.Popen([terminal, '--working-directory', str(directory)])
            elif terminal == 'konsole':
                subprocess.Popen([terminal, '--workdir', str(directory)])
            elif terminal in ['xfce4-terminal', 'alacritty', 'kitty']:
                subprocess.Popen([terminal, '--working-directory', str(directory)])
            else:
                # Fallback: change directory in shell
                subprocess.Popen([terminal], cwd=str(directory))
            
            logger.info(f"Opened terminal in: {directory}")
            return True
        except Exception as e:
            logger.error(f"Failed to open terminal: {e}")
            return False
    
    @staticmethod
    def copy_path_to_clipboard(file_path: str) -> bool:
        """
        Copy file path to clipboard.
        
        Args:
            file_path: Path to copy
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to use xclip or xsel on Linux
            if FileActions._has_command('xclip'):
                process = subprocess.Popen(
                    ['xclip', '-selection', 'clipboard'],
                    stdin=subprocess.PIPE
                )
                process.communicate(file_path.encode('utf-8'))
                logger.info(f"Copied to clipboard (xclip): {file_path}")
                return True
            elif FileActions._has_command('xsel'):
                process = subprocess.Popen(
                    ['xsel', '--clipboard', '--input'],
                    stdin=subprocess.PIPE
                )
                process.communicate(file_path.encode('utf-8'))
                logger.info(f"Copied to clipboard (xsel): {file_path}")
                return True
            else:
                logger.warning("No clipboard utility found (install xclip or xsel)")
                return False
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            return False
    
    @staticmethod
    def show_file_details(file_path: str) -> dict:
        """
        Get detailed information about a file.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Dictionary with file details
        """
        path = Path(file_path)
        
        if not path.exists():
            return {'error': 'File does not exist'}
        
        try:
            stat = path.stat()
            
            from datetime import datetime
            
            details = {
                'path': str(path.absolute()),
                'name': path.name,
                'size': stat.st_size,
                'size_human': FileActions._human_readable_size(stat.st_size),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'is_link': path.is_symlink(),
                'permissions': oct(stat.st_mode)[-3:],
            }
            
            if path.is_file():
                details['extension'] = path.suffix
            
            return details
        except Exception as e:
            logger.error(f"Failed to get file details: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def open_file_manager(file_path: str) -> bool:
        """
        Open the file manager and select the file.
        
        Args:
            file_path: Path to the file
        
        Returns:
            True if successful, False otherwise
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"Path does not exist: {file_path}")
            return False
        
        try:
            # Use parent directory
            directory = path.parent if path.is_file() else path
            
            if FileActions._has_command('nautilus'):  # GNOME
                subprocess.Popen(['nautilus', str(directory)])
            elif FileActions._has_command('dolphin'):  # KDE
                subprocess.Popen(['dolphin', str(directory)])
            elif FileActions._has_command('thunar'):  # XFCE
                subprocess.Popen(['thunar', str(directory)])
            elif FileActions._has_command('pcmanfm'):  # LXDE
                subprocess.Popen(['pcmanfm', str(directory)])
            else:
                # Fallback to xdg-open
                subprocess.Popen(['xdg-open', str(directory)])
            
            logger.info(f"Opened file manager for: {directory}")
            return True
        except Exception as e:
            logger.error(f"Failed to open file manager: {e}")
            return False
    
    @staticmethod
    def _has_command(cmd: str) -> bool:
        """Check if a command is available in PATH."""
        import shutil
        return shutil.which(cmd) is not None
    
    @staticmethod
    def _human_readable_size(size: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    actions = FileActions()
    
    # Test with a common file
    test_file = "/etc/hosts"
    
    print("File details:")
    details = actions.show_file_details(test_file)
    for key, value in details.items():
        print(f"  {key}: {value}")
