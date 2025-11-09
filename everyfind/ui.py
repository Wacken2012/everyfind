#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Everyfind - GTK UI Module
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
from pathlib import Path
from typing import Optional, List
import threading

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk, GLib
except ImportError as e:
    print(f"Error: PyGObject not installed. Install with: pip install PyGObject")
    raise

from .indexer import FileIndexer
from .actions import FileActions
from .settings import load_settings, save_settings
from .ui_settings import SettingsDialog

logger = logging.getLogger(__name__)


class IndexProgressDialog(Gtk.Dialog):
    """Dialog showing indexing progress with cancel button."""
    
    def __init__(self, parent):
        """
        Initialize the progress dialog.
        
        Args:
            parent: Parent GTK window
        """
        super().__init__(title="Indexierung läuft…", parent=parent, modal=True)
        self.set_default_size(400, 150)
        self.set_border_width(10)
        
        # Stop event for cancellation
        self.stop_event = threading.Event()
        self.cancelled = False
        
        # Create widgets
        box = self.get_content_area()
        box.set_spacing(10)
        
        # Status label
        self.status_label = Gtk.Label(label="Initialisiere Indexierung…")
        self.status_label.set_line_wrap(True)
        box.pack_start(self.status_label, False, False, 0)
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        box.pack_start(self.progress_bar, False, False, 0)
        
        # File count label
        self.file_label = Gtk.Label(label="0 Dateien indexiert")
        box.pack_start(self.file_label, False, False, 0)
        
        # Cancel button
        self.cancel_button = Gtk.Button(label="Abbrechen")
        self.cancel_button.connect("clicked", self._on_cancel)
        box.pack_start(self.cancel_button, False, False, 0)
        
        self.show_all()
    
    def _on_cancel(self, widget):
        """Handle cancel button click."""
        self.stop_event.set()
        self.cancelled = True
        self.status_label.set_text("Abbrechen…")
        self.cancel_button.set_sensitive(False)
    
    def update_progress(self, count: int, current_path: str = ""):
        """
        Update progress display (called from indexer callback).
        
        Args:
            count: Number of files indexed so far
            current_path: Current file being indexed
        """
        def _update():
            self.file_label.set_text(f"{count} Dateien indexiert")
            if current_path:
                # Show only filename to keep dialog clean
                filename = Path(current_path).name
                self.status_label.set_text(f"Indexiere: {filename}")
            self.progress_bar.pulse()  # Indeterminate progress
            return False
        
        GLib.idle_add(_update)
    
    def finish(self, count: int, cancelled: bool = False):
        """
        Mark indexing as finished.
        
        Args:
            count: Total files indexed
            cancelled: Whether indexing was cancelled
        """
        def _finish():
            if cancelled:
                self.status_label.set_text("Abgebrochen")
                self.file_label.set_text(f"{count} Dateien indexiert (abgebrochen)")
            else:
                self.status_label.set_text("Fertig")
                self.file_label.set_text(f"{count} Dateien indexiert")
                self.progress_bar.set_fraction(1.0)
            
            self.cancel_button.set_label("Schließen")
            self.cancel_button.set_sensitive(True)
            self.cancel_button.disconnect_by_func(self._on_cancel)
            self.cancel_button.connect("clicked", lambda w: self.destroy())
            return False
        
        GLib.idle_add(_finish)


class EveryfindWindow(Gtk.Window):
    """Main GTK window for Everyfind."""
    
    def __init__(self, indexer: FileIndexer):
        """
        Initialize the Everyfind window.
        
        Args:
            indexer: FileIndexer instance
        """
        super().__init__(title="Everyfind")
        
        self.indexer = indexer
        self.actions = FileActions()
        self.current_results: List[str] = []
        # Load settings
        try:
            self.settings = load_settings()
        except Exception:
            self.settings = {}
        
        # Window settings
        self.set_default_size(800, 600)
        self.set_border_width(10)
        
        # Create UI
        self._create_widgets()
        self._setup_layout()
        self._connect_signals()
        
        # Load initial results
        self._load_all_files()
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Menu bar
        self.menu_bar = Gtk.MenuBar()
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)

        settings_item = Gtk.MenuItem(label="Einstellungen...")
        settings_item.connect("activate", self._on_open_settings)
        file_menu.append(settings_item)

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", lambda w: Gtk.main_quit())
        file_menu.append(quit_item)

        self.menu_bar.append(file_item)

        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search files...")
        
        # Result count label
        self.result_label = Gtk.Label()
        self.result_label.set_xalign(0)
        
        # TreeView for results
        self.store = Gtk.ListStore(str, str)  # filename, full_path
        self.tree_view = Gtk.TreeView(model=self.store)
        
        # Filename column
        renderer_text = Gtk.CellRendererText()
        column_filename = Gtk.TreeViewColumn("Filename", renderer_text, text=0)
        column_filename.set_sort_column_id(0)
        column_filename.set_resizable(True)
        self.tree_view.append_column(column_filename)
        
        # Path column
        column_path = Gtk.TreeViewColumn("Path", renderer_text, text=1)
        column_path.set_sort_column_id(1)
        column_path.set_resizable(True)
        column_path.set_expand(True)
        self.tree_view.append_column(column_path)
        
        # Scrolled window for TreeView
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.add(self.tree_view)
        
        # Status bar
        self.status_bar = Gtk.Statusbar()
        self.status_context = self.status_bar.get_context_id("status")
        
        # Context menu
        self.context_menu = Gtk.Menu()
        self._create_context_menu()
    
    def _create_context_menu(self):
        """Create the right-click context menu."""
        menu_items = [
            ("Open File", self._on_menu_open),
            ("Open in File Manager", self._on_menu_open_file_manager),
            ("Open in Terminal", self._on_menu_open_terminal),
            ("Copy Path", self._on_menu_copy_path),
            ("Show Details", self._on_menu_show_details),
        ]
        
        for label, callback in menu_items:
            item = Gtk.MenuItem(label=label)
            item.connect("activate", callback)
            self.context_menu.append(item)
        
        self.context_menu.show_all()
    
    def _setup_layout(self):
        """Setup the window layout."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # Menu bar at very top
        vbox.pack_start(self.menu_bar, False, False, 0)

        # Search entry below menu
        vbox.pack_start(self.search_entry, False, False, 0)
        
        # Result count
        vbox.pack_start(self.result_label, False, False, 0)
        
        # Results in scrolled window
        vbox.pack_start(self.scrolled_window, True, True, 0)
        
        # Status bar at bottom
        vbox.pack_start(self.status_bar, False, False, 0)
        
        self.add(vbox)

        # Apply settings: optionally start indexing
        try:
            if self.settings.get("auto_reindex") and self.settings.get("indexed_paths"):
                # Show progress dialog and run indexing
                self._run_indexing_with_progress(self.settings.get("indexed_paths", []))
        except Exception:
            pass
    
    def _connect_signals(self):
        """Connect widget signals to handlers."""
        # Search entry
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.search_entry.connect("activate", self._on_search_activate)
        
        # TreeView
        self.tree_view.connect("row-activated", self._on_row_activated)
        self.tree_view.connect("button-press-event", self._on_button_press)
        
        # Window
        self.connect("destroy", Gtk.main_quit)
        self.connect("key-press-event", self._on_key_press)

    def _on_open_settings(self, widget):
        """Open the settings dialog and apply/save settings on OK."""
        dialog = SettingsDialog(self, self.settings or {})
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            new_settings = dialog.get_settings()
            try:
                save_settings(new_settings)
                self.settings = new_settings
                # If there are new indexed paths and auto_reindex is enabled, index them
                if new_settings.get("auto_reindex") and new_settings.get("indexed_paths"):
                    self._run_indexing_with_progress(new_settings.get("indexed_paths", []))
            except Exception as e:
                logger.error(f"Failed to save settings: {e}")

        dialog.destroy()
    
    def _load_all_files(self):
        """Load all files from the index."""
        try:
            paths = self.indexer.get_all_paths()
            self._update_results(paths)
        except Exception as e:
            logger.error(f"Failed to load files: {e}")
            self._show_status(f"Error loading files: {e}")
    
    def _update_results(self, paths: List[str]):
        """Update the TreeView with search results."""
        self.store.clear()
        self.current_results = paths
        
        for path_str in paths:
            path = Path(path_str)
            self.store.append([path.name, str(path.parent)])
        
        # Update result label
        count = len(paths)
        self.result_label.set_text(f"Results: {count}")
        
        self._show_status(f"Showing {count} files")
    
    def _on_search_changed(self, entry: Gtk.SearchEntry):
        """Handle search text changes."""
        search_text = entry.get_text().strip()
        
        if not search_text:
            self._load_all_files()
            return
        
        try:
            # Search in database
            results = self.indexer.search_files(search_text)
            self._update_results(results)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            self._show_status(f"Search error: {e}")
    
    def _on_search_activate(self, entry: Gtk.SearchEntry):
        """Handle Enter key in search entry."""
        # Select first result if available
        if len(self.store) > 0:
            self.tree_view.set_cursor(0)
            self.tree_view.grab_focus()
    
    def _on_row_activated(self, tree_view: Gtk.TreeView, path, column):
        """Handle double-click on a row."""
        model = tree_view.get_model()
        iter = model.get_iter(path)
        
        if iter:
            row_index = path.get_indices()[0]
            file_path = self.current_results[row_index]
            
            if self.actions.open_file(file_path):
                self._show_status(f"Opened: {file_path}")
            else:
                self._show_status(f"Failed to open: {file_path}")
    
    def _on_button_press(self, tree_view: Gtk.TreeView, event: Gdk.EventButton):
        """Handle mouse button press (for right-click menu)."""
        if event.button == 3:  # Right click
            path_info = tree_view.get_path_at_pos(int(event.x), int(event.y))
            
            if path_info:
                path, column, cell_x, cell_y = path_info
                tree_view.set_cursor(path)
                self.context_menu.popup_at_pointer(event)
                return True
        
        return False
    
    def _on_key_press(self, widget, event: Gdk.EventKey):
        """Handle keyboard shortcuts."""
        # Ctrl+F to focus search
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            if event.keyval == Gdk.KEY_f:
                self.search_entry.grab_focus()
                return True
            # Ctrl+Q to quit
            elif event.keyval == Gdk.KEY_q:
                Gtk.main_quit()
                return True
        
        # ESC to clear search
        if event.keyval == Gdk.KEY_Escape:
            self.search_entry.set_text("")
            self.search_entry.grab_focus()
            return True
        
        return False
    
    def _get_selected_path(self) -> Optional[str]:
        """Get the currently selected file path."""
        selection = self.tree_view.get_selection()
        model, iter = selection.get_selected()
        
        if iter:
            path = model.get_path(iter)
            row_index = path.get_indices()[0]
            return self.current_results[row_index]
        
        return None
    
    def _on_menu_open(self, menu_item):
        """Menu: Open file."""
        path = self._get_selected_path()
        if path:
            self.actions.open_file(path)
    
    def _on_menu_open_file_manager(self, menu_item):
        """Menu: Open in file manager."""
        path = self._get_selected_path()
        if path:
            self.actions.open_file_manager(path)
    
    def _on_menu_open_terminal(self, menu_item):
        """Menu: Open in terminal."""
        path = self._get_selected_path()
        if path:
            self.actions.open_in_terminal(path)
    
    def _on_menu_copy_path(self, menu_item):
        """Menu: Copy path to clipboard."""
        path = self._get_selected_path()
        if path:
            if self.actions.copy_path_to_clipboard(path):
                self._show_status(f"Copied: {path}")
            else:
                self._show_status("Failed to copy path (install xclip or xsel)")
    
    def _on_menu_show_details(self, menu_item):
        """Menu: Show file details."""
        path = self._get_selected_path()
        if path:
            details = self.actions.show_file_details(path)
            self._show_details_dialog(details)
    
    def _show_details_dialog(self, details: dict):
        """Show a dialog with file details."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="File Details"
        )
        
        details_text = "\n".join([f"{k}: {v}" for k, v in details.items()])
        dialog.format_secondary_text(details_text)
        dialog.run()
        dialog.destroy()
    
    def _run_indexing_with_progress(self, paths: List[str]):
        """
        Run indexing with progress dialog.
        
        Args:
            paths: List of directory paths to index
        """
        if not paths:
            return
        
        # Create progress dialog
        progress_dialog = IndexProgressDialog(self)
        
        filters = self.settings.get("file_filters", [])
        excludes = self.settings.get("excluded_paths", [])
        
        def _run_index():
            """Background indexing thread."""
            total_count = 0
            try:
                for p in paths:
                    if progress_dialog.stop_event.is_set():
                        break
                    try:
                        count = self.indexer.index_directory(
                            p, 
                            filters=filters, 
                            excludes=excludes,
                            progress_callback=lambda c, path: progress_dialog.update_progress(total_count + c, path),
                            stop_event=progress_dialog.stop_event
                        )
                        total_count += count
                    except Exception as e:
                        logger.error(f"Indexing {p} failed: {e}")
                
                # Mark as finished
                progress_dialog.finish(total_count, progress_dialog.cancelled)
                
                # Reload results in main window
                GLib.idle_add(self._load_all_files)
                
            except Exception as e:
                logger.error(f"Indexing thread error: {e}")
                progress_dialog.finish(total_count, True)
        
        # Start indexing thread
        t = threading.Thread(target=_run_index, daemon=True)
        t.start()
        
        # Show dialog (blocks until closed)
        progress_dialog.run()
        progress_dialog.destroy()
    
    def _show_status(self, message: str):
        """Show a status message."""
        self.status_bar.pop(self.status_context)
        self.status_bar.push(self.status_context, message)


def run_gui(db_path: Optional[str] = None):
    """
    Run the GTK GUI.
    
    Args:
        db_path: Path to SQLite database
    """
    logging.basicConfig(level=logging.INFO)
    
    indexer = FileIndexer(db_path)
    window = EveryfindWindow(indexer)
    window.show_all()
    
    try:
        Gtk.main()
    finally:
        indexer.close()


if __name__ == "__main__":
    run_gui()
