#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GTK settings dialog for Everyfind
"""

from __future__ import annotations

from typing import List
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from .settings import DEFAULT_SETTINGS


class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent: Gtk.Window, settings: dict):
        super().__init__(title="Einstellungen", transient_for=parent, flags=0)
        self.set_default_size(600, 400)

        self.settings = settings.copy()

        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_SAVE, Gtk.ResponseType.OK)

        box = self.get_content_area()
        grid = Gtk.Grid(column_spacing=12, row_spacing=8, margin=12)

        # Directories to index: simple listbox + add/remove
        lbl_dirs = Gtk.Label(label="Verzeichnisse zum Indexieren:", xalign=0)
        grid.attach(lbl_dirs, 0, 0, 2, 1)

        self.dir_store = Gtk.ListStore(str)
        for p in self.settings.get("indexed_paths", []):
            self.dir_store.append([p])

        self.dir_view = Gtk.TreeView(model=self.dir_store)
        renderer = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn("Pfad", renderer, text=0)
        self.dir_view.append_column(col)
        scrolled_dirs = Gtk.ScrolledWindow()
        scrolled_dirs.set_min_content_height(80)
        scrolled_dirs.add(self.dir_view)
        grid.attach(scrolled_dirs, 0, 1, 1, 1)

        vbox_dirs = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add_dir_button = Gtk.Button(label="Hinzufügen...")
        self.remove_dir_button = Gtk.Button(label="Entfernen")
        vbox_dirs.pack_start(self.add_dir_button, False, False, 0)
        vbox_dirs.pack_start(self.remove_dir_button, False, False, 0)
        grid.attach(vbox_dirs, 1, 1, 1, 1)

        # File type filters
        lbl_filters = Gtk.Label(label="Dateitypen-Filter (Komma-getrennt):", xalign=0)
        grid.attach(lbl_filters, 0, 2, 2, 1)
        self.filters_entry = Gtk.Entry()
        self.filters_entry.set_text(",".join(self.settings.get("file_filters", [])))
        grid.attach(self.filters_entry, 0, 3, 2, 1)

        # Excluded paths
        lbl_exclude = Gtk.Label(label="Ausgeschlossene Pfade (Komma-getrennt):", xalign=0)
        grid.attach(lbl_exclude, 0, 4, 2, 1)
        self.exclude_entry = Gtk.Entry()
        self.exclude_entry.set_text(",".join(self.settings.get("excluded_paths", [])))
        grid.attach(self.exclude_entry, 0, 5, 2, 1)

        # Auto reindex
        self.auto_reindex_check = Gtk.CheckButton(label="Automatische Re-Indexierung aktivieren")
        self.auto_reindex_check.set_active(bool(self.settings.get("auto_reindex", False)))
        grid.attach(self.auto_reindex_check, 0, 6, 2, 1)

        lbl_interval = Gtk.Label(label="Intervall (Minuten):", xalign=0)
        self.interval_spin = Gtk.SpinButton.new_with_range(1, 24*60, 1)
        self.interval_spin.set_value(self.settings.get("reindex_interval_minutes", 60))
        grid.attach(lbl_interval, 0, 7, 1, 1)
        grid.attach(self.interval_spin, 1, 7, 1, 1)

        # Language selection
        lbl_lang = Gtk.Label(label="Sprache der Oberfläche:", xalign=0)
        grid.attach(lbl_lang, 0, 8, 1, 1)
        self.lang_combo = Gtk.ComboBoxText()
        self.lang_combo.append_text("system")
        self.lang_combo.append_text("de")
        self.lang_combo.append_text("en")
        cur_lang = self.settings.get("language", "system")
        self.lang_combo.set_active(0 if cur_lang == "system" else (1 if cur_lang == "de" else 2))
        grid.attach(self.lang_combo, 1, 8, 1, 1)

        # Reset button
        self.reset_button = Gtk.Button(label="Zurücksetzen auf Standard")
        grid.attach(self.reset_button, 0, 9, 2, 1)

        box.add(grid)
        self.show_all()

        # Signals
        self.add_dir_button.connect("clicked", self.on_add_dir)
        self.remove_dir_button.connect("clicked", self.on_remove_dir)
        self.reset_button.connect("clicked", self.on_reset)

    def on_add_dir(self, button):
        chooser = Gtk.FileChooserDialog(
            title="Verzeichnis auswählen",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK),
            transient_for=self,
        )

        res = chooser.run()
        if res == Gtk.ResponseType.OK:
            folder = chooser.get_filename()
            if folder:
                self.dir_store.append([folder])
        chooser.destroy()

    def on_remove_dir(self, button):
        selection = self.dir_view.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter:
            model.remove(treeiter)

    def on_reset(self, button):
        # Reset UI elements to defaults
        self.dir_store.clear()
        for p in DEFAULT_SETTINGS.get("indexed_paths", []):
            self.dir_store.append([p])

        self.filters_entry.set_text(",".join(DEFAULT_SETTINGS.get("file_filters", [])))
        self.exclude_entry.set_text(",".join(DEFAULT_SETTINGS.get("excluded_paths", [])))
        self.auto_reindex_check.set_active(bool(DEFAULT_SETTINGS.get("auto_reindex", False)))
        self.interval_spin.set_value(DEFAULT_SETTINGS.get("reindex_interval_minutes", 60))
        lang = DEFAULT_SETTINGS.get("language", "system")
        self.lang_combo.set_active(0 if lang == "system" else (1 if lang == "de" else 2))

    def get_settings(self) -> dict:
        """Collect settings from the dialog UI and return as dict."""
        indexed_paths: List[str] = []
        for row in self.dir_store:
            indexed_paths.append(row[0])

        file_filters = [f.strip() for f in self.filters_entry.get_text().split(",") if f.strip()]
        excluded = [p.strip() for p in self.exclude_entry.get_text().split(",") if p.strip()]

        lang_text = self.lang_combo.get_active_text() or "system"

        return {
            "indexed_paths": indexed_paths,
            "file_filters": file_filters or ["*"],
            "excluded_paths": excluded,
            "auto_reindex": bool(self.auto_reindex_check.get_active()),
            "reindex_interval_minutes": int(self.interval_spin.get_value()),
            "language": lang_text,
        }
