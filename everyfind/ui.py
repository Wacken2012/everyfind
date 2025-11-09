#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Everyfind - GTK UI Module
Copyright (C) 2025 Stefan

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
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
    print(f"Error: PyGObject not installed")
    raise

from .indexer import FileIndexer
from .actions import FileActions
from .settings import load_settings, save_settings
from .ui_settings import SettingsDialog
from . import i18n
from gettext import gettext as _

logger = logging.getLogger(__name__)


class IndexProgressDialog(Gtk.Dialog):
    """Dialog showing indexing progress with cancel button."""
    
    def __init__(self, parent):
        super().__init__(title=_("Indexing…"), parent=parent, modal=True)
        self.set_default_size(400, 150)
        self.set_border_width(10)
        
        self.stop_event = threading.Event()
        self.cancelled = False
        
        box = self.get_content_area()
        box.set_spacing(10)
        
        self.status_label = Gtk.Label(label=_("Initializing indexing…"))
        self.status_label.set_line_wrap(True)
        box.pack_start(self.status_label, False, False, 0)
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        box.pack_start(self.progress_bar, False, False, 0)
        
        self.file_label = Gtk.Label(label=_("0 files indexed"))
        box.pack_start(self.file_label, False, False, 0)
        
        self.cancel_button = Gtk.Button(label=_("Cancel"))
        self.cancel_button.connect("clicked", self._on_cancel)
        box.pack_start(self.cancel_button, False, False, 0)
        
        self.show_all()
    
    def _on_cancel(self, widget):
        self.stop_event.set()
        self.cancelled = True
        self.status_label.set_text(_("Cancelling…"))
        self.cancel_button.set_sensitive(False)
    
    def update_progress(self, count: int, current_path: str = ""):
        def _update():
            self.file_label.set_text(_("{count} files indexed").format(count=count))
            if current_path:
                filename = Path(current_path).name
                self.status_label.set_text(_("Indexing: {filename}").format(filename=filename))
            self.progress_bar.pulse()
            return False
        GLib.idle_add(_update)
    
    def finish(self, count: int, cancelled: bool = False):
        def _finish():
            if cancelled:
                self.status_label.set_text(_('Cancelled'))
                self.file_label.set_text(_("{count} files indexed (cancelled)").format(count=count))
            else:
                self.status_label.set_text(_('Done'))
                self.file_label.set_text(_("{count} files indexed").format(count=count))
                self.progress_bar.set_fraction(1.0)
            
            self.cancel_button.set_label(_('Close'))
            self.cancel_button.set_sensitive(True)
            try:
                self.cancel_button.disconnect_by_func(self._on_cancel)
            except:
                pass
            self.cancel_button.connect("clicked", lambda w: self.destroy())
            return False
        GLib.idle_add(_finish)


class EveryfindWindow(Gtk.Window):
    """Main GTK window for Everyfind."""
    
    def __init__(self, indexer: FileIndexer):
        super().__init__(title="Everyfind")
        
        self.indexer = indexer
        self.actions = FileActions()
        self.current_results: List[str] = []
        
        try:
            self.settings = load_settings()
        except Exception:
            self.settings = {}
        
        try:
            i18n.init_gettext(self.settings.get("language", "system"))
        except Exception:
            pass
        
        self.set_default_size(800, 600)
        self.set_border_width(10)
        
        self._create_widgets()
        self._setup_layout()
        self._connect_signals()
        self._load_all_files()
    
    def _create_widgets(self):
        self.menu_bar = Gtk.MenuBar()
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)
        
        settings_item = Gtk.MenuItem(label=_("Settings…"))
        settings_item.connect("activate", self._on_open_settings)
        file_menu.append(settings_item)
        
        quit_item = Gtk.MenuItem(label=_("Quit"))
        quit_item.connect("activate", lambda w: Gtk.main_quit())
        file_menu.append(quit_item)
        
        self.menu_bar.append(file_item)
        
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(_("Search files…"))
        
        self.result_label = Gtk.Label()
        self.result_label.set_xalign(0)
        
        self.store = Gtk.ListStore(str, str)
        self.tree_view = Gtk.TreeView(model=self.store)
        
        renderer_text = Gtk.CellRendererText()
        column_filename = Gtk.TreeViewColumn(_("Filename"), renderer_text, text=0)
        column_filename.set_sort_column_id(0)
        column_filename.set_resizable(True)
        self.tree_view.append_column(column_filename)
        
        column_path = Gtk.TreeViewColumn(_("Path"), renderer_text, text=1)
        column_path.set_sort_column_id(1)
        column_path.set_resizable(True)
        column_path.set_expand(True)
        self.tree_view.append_column(column_path)
        
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.add(self.tree_view)
        
        self.status_bar = Gtk.Statusbar()
        self.status_context = self.status_bar.get_context_id("status")
        
        self.context_menu = Gtk.Menu()
        self._create_context_menu()
    
    def _create_context_menu(self):
        menu_items = [
            (_("Open File"), self._on_menu_open),
            (_("Open in File Manager"), self._on_menu_open_file_manager),
            (_("Open in Terminal"), self._on_menu_open_terminal),
            (_("Copy Path"), self._on_menu_copy_path),
            (_("Show Details"), self._on_menu_show_details),
        ]
        
        for label, callback in menu_items:
            item = Gtk.MenuItem(label=label)
            item.connect("activate", callback)
            self.context_menu.append(item)
        
        self.context_menu.show_all()
    
    def _setup_layout(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.pack_start(self.menu_bar, False, False, 0)
        vbox.pack_start(self.search_entry, False, False, 0)
        vbox.pack_start(self.result_label, False, False, 0)
        vbox.pack_start(self.scrolled_window, True, True, 0)
        vbox.pack_start(self.status_bar, False, False, 0)
        self.add(vbox)
    
    def _connect_signals(self):
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.search_entry.connect("activate", self._on_search_activate)
        self.tree_view.connect("row-activated", self._on_row_activated)
        self.tree_view.connect("button-press-event", self._on_button_press)
        self.connect("key-press-event", self._on_key_press)
    
    def _on_search_changed(self, widget):
        query = widget.get_text()
        if not query:
            self._load_all_files()
        else:
            try:
                results = self.indexer.search(query)
                self._display_results(results)
            except Exception as e:
                logger.error(f"Search error: {e}")
    
    def _on_search_activate(self, widget):
        query = widget.get_text()
        if query:
            self._on_search_changed(widget)
    
    def _on_row_activated(self, tree_view, path, column):
        model = tree_view.get_model()
        tree_iter = model.get_iter(path)
        full_path = model.get_value(tree_iter, 1)
        self.actions.open_file(full_path)
    
    def _on_button_press(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            path_info = self.tree_view.get_path_at_pos(int(event.x), int(event.y))
            if path_info:
                path = path_info[0]
                self.tree_view.get_selection().select_path(path)
                self.context_menu.popup(None, None, None, None, event.button, event.time)
            return True
        return False
    
    def _on_key_press(self, widget, event):
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            if event.keyval == Gdk.KEY_f:
                self.search_entry.grab_focus()
                return True
            elif event.keyval == Gdk.KEY_q:
                Gtk.main_quit()
                return True
        return False
    
    def _get_selected_path(self):
        selection = self.tree_view.get_selection()
        model, tree_iter = selection.get_selected()
        if tree_iter:
            return model.get_value(tree_iter, 1)
        return None
    
    def _on_menu_open(self, widget):
        path = self._get_selected_path()
        if path:
            self.actions.open_file(path)
    
    def _on_menu_open_file_manager(self, widget):
        path = self._get_selected_path()
        if path:
            self.actions.open_in_file_manager(path)
    
    def _on_menu_open_terminal(self, widget):
        path = self._get_selected_path()
        if path:
            self.actions.open_in_terminal(path)
    
    def _on_menu_copy_path(self, widget):
        path = self._get_selected_path()
        if path:
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(path, -1)
            self._show_status(_("Path copied to clipboard"))
    
    def _on_menu_show_details(self, widget):
        path = self._get_selected_path()
        if path:
            self._show_file_details(path)
    
    def _show_file_details(self, filepath: str):
        p = Path(filepath)
        if not p.exists():
            return
        
        stat = p.stat()
        details = f"{_('Name')}: {p.name}\n"
        details += f"{_('Path')}: {p.parent}\n"
        details += f"{_('Size')}: {stat.st_size} bytes\n"
        
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=_("File Details")
        )
        dialog.format_secondary_text(details)
        dialog.run()
        dialog.destroy()
    
    def _on_open_settings(self, widget):
        dialog = SettingsDialog(self)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            new_settings = dialog.get_settings()
            save_settings(new_settings)
            self.settings = new_settings
            
            try:
                i18n.init_gettext(new_settings.get("language", "system"))
            except Exception as e:
                logger.error(f"Failed to reinitialize i18n: {e}")
            
            if new_settings.get("indexed_paths"):
                self._run_indexing_with_progress(new_settings["indexed_paths"])
        
        dialog.destroy()
    
    def _run_indexing_with_progress(self, paths: List[str]):
        progress_dialog = IndexProgressDialog(self)
        
        def indexing_thread():
            try:
                def progress_callback(count, current_path):
                    if progress_dialog.stop_event.is_set():
                        raise KeyboardInterrupt("Indexing cancelled by user")
                    progress_dialog.update_progress(count, current_path)
                
                total_indexed = self.indexer.index(
                    paths,
                    progress_callback=progress_callback,
                    stop_event=progress_dialog.stop_event
                )
                
                progress_dialog.finish(total_indexed, cancelled=progress_dialog.cancelled)
                
                def reload_files():
                    self._load_all_files()
                    return False
                GLib.idle_add(reload_files)
                
            except KeyboardInterrupt:
                progress_dialog.finish(0, cancelled=True)
            except Exception as e:
                logger.error(f"Indexing error: {e}")
                progress_dialog.finish(0, cancelled=True)
        
        thread = threading.Thread(target=indexing_thread, daemon=True)
        thread.start()
    
    def _load_all_files(self):
        try:
            results = self.indexer.get_all_files()
            self._display_results(results)
        except Exception as e:
            logger.error(f"Failed to load files: {e}")
            self._display_results([])
    
    def _display_results(self, results: List[str]):
        self.store.clear()
        self.current_results = results
        
        for filepath in results:
            p = Path(filepath)
            filename = p.name
            self.store.append([filename, filepath])
        
        count = len(results)
        self.result_label.set_text(_("{count} results").format(count=count))
    
    def _show_status(self, message: str):
        self.status_bar.pop(self.status_context)
        self.status_bar.push(self.status_context, message)


def run_gui(db_path: Optional[str] = None):
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
