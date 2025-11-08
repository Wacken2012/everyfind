# Everyfind - Project Instructions

## Project Overview
- **Name**: Everyfind
- **Type**: Python application with GTK GUI and CLI
- **License**: GNU GPL v3
- **Target**: Linux (x86 + Raspberry Pi)
- **Purpose**: Ultra-fast file search using fzf backend with SQLite indexing

## Core Components
- `indexer.py`: Recursive directory scanning and SQLite storage
- `search_backend.py`: fzf-py (iterfzf) wrapper with PTY support
- `ui.py`: GTK window with result list, double-click handler, context menu
- `actions.py`: File operations (open, terminal, copy path, show details)
- `build.sh`: AppImage creation script with embedded venv and fzf binary

## Development Guidelines
- All files must include GPL v3 license headers
- Ensure Raspberry Pi compatibility (no unnecessary dependencies)
- Use portable code (no hardcoded paths)
- Include logging for indexing and search operations
- Ensure UTF-8 and Unicode compatibility
- Keep modules decoupled and testable

## Dependencies
- Python >= 3.10
- fzf-py (iterfzf) for fuzzy search
- PyGObject for GTK GUI
- SQLite for file indexing
- watchdog for directory monitoring (optional)

## Build & Distribution
- AppImage-compatible
- Virtual environment ready
- Cross-architecture support (x86_64 + ARM)

## License Compatibility
- fzf: MIT License ✓
- PyGObject: LGPL ✓
- SQLite: Public Domain ✓
- All compatible with GPL v3
