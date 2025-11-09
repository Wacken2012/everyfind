git clone https://github.com/deinname/everyfind.git
everyfind index /pfad/zum/durchsuchen
git clone https://github.com/deinname/everyfind.git
everyfind index /pfad/zum/durchsuchen
everyfind search
everyfind gui
<!--
Everyfind – ultraschnelle Dateisuche für Linux
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
-->

# Everyfind

[![Build](https://github.com/Wacken2012/everyfind/actions/workflows/build.yml/badge.svg)](https://github.com/Wacken2012/everyfind/actions/workflows/build.yml)

🇩🇪 Deutsch | 🇬🇧 English

## 🇩🇪 Deutsch

Everyfind ist eine ultraschnelle Dateisuche für Linux, inspiriert von "Everything" unter Windows. Es kombiniert die Geschwindigkeit von `fzf` mit einer GTK-Oberfläche und bietet sowohl eine CLI- als auch eine GUI-Oberfläche.

Features
- CLI- und GUI-Modus (GTK)
- Fuzzy-Suche mit `fzf` (über PTY)
- Schnelle Indexierung mit SQLite
- AppImage-fähig, Raspberry Pi tauglich (ARM)

Hinweis zur Entstehung
Die Architektur dieses Projekts wurde gemeinsam mit einer KI (Microsoft Copilot) entworfen. Teile des Codes wurden mithilfe von GitHub Copilot in VS Code generiert. Alle von Copilot erzeugten Teile wurden überprüft und angepasst.

Installation (lokal)

1. Klonen und Build-Skript ausführen (erzeugt AppImage):

```bash
git clone https://github.com/yourname/everyfind.git
cd everyfind
./build.sh x86_64      # oder: ./build.sh aarch64
```

2. Entwicklung (virtuelle Umgebung):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Häufige Befehle

```bash
everyfind index /pfad/zum/durchsuchen    # Index erstellen
everyfind search                         # Interaktive fzf-Suche (CLI)
everyfind gui                            # GTK-GUI starten
everyfind stats                          # Statistik über Index
everyfind clear                          # Index löschen
```

### 🔧 Konfiguration

Everyfind speichert seine Einstellungen in `~/.config/everyfind/settings.json`. Diese Datei wird automatisch erstellt, wenn du die Einstellungen in der GUI änderst.

Beispielkonfiguration:

```json
{
  "indexed_paths": ["/home/stefan/Dokumente", "/home/stefan/Bilder"],
  "file_filters": ["*.pdf", "*.txt", ".doc", ".odt"],
  "excluded_paths": ["/home/stefan/Dokumente/temp", "/mnt", "/media"],
  "auto_reindex": true,
  "reindex_interval": 60,
  "language": "de"
}
```

**Erklärung der Optionen:**

- **`indexed_paths`**: Liste von Verzeichnissen, die indexiert werden sollen
- **`file_filters`**: Liste von Dateiendungen oder Wildcard-Mustern (z.B. `*.txt`, `.pdf`, `*.py`)
  - Ohne Filters werden alle Dateien indexiert
  - Wildcards: `*.txt` findet alle .txt-Dateien
  - Einfache Endungen: `.pdf` oder `pdf` funktionieren beide
- **`excluded_paths`**: Verzeichnispfade, die bei der Indexierung ignoriert werden
  - Absolute Pfade oder Präfixe (z.B. `/mnt`, `/media`)
  - Standardmäßig ausgeschlossen: `.git`, `__pycache__`, `.venv`, `node_modules`
- **`auto_reindex`**: Beim Programmstart automatisch neu indexieren (true/false)
- **`reindex_interval`**: Zeit in Minuten zwischen automatischen Neuindexierungen
- **`language`**: Sprache der Benutzeroberfläche
  - `"de"` für Deutsch
  - `"en"` für Englisch
  - `"system"` für Systemsprache

Du kannst die Einstellungen entweder manuell in der JSON-Datei bearbeiten oder bequem über die GUI ändern (Menü → Einstellungen).

Lizenz
Dieses Projekt steht unter der GNU General Public License v3 (GPLv3). Siehe `LICENSE` im Repository.

Mitwirken
Wenn du beitragen möchtest, siehe `CONTRIBUTING.md` für Hinweise zum Entwicklungsworkflow, Code-Stil und Pull-Requests.

## 🇬🇧 English

Everyfind is a blazing-fast file search tool for Linux, inspired by "Everything" on Windows. It combines `fzf` speed with a GTK interface and provides both CLI and GUI frontends.

Features
- CLI and GUI (GTK)
- Fuzzy search powered by `fzf` (via PTY)
- Fast indexing using SQLite
- AppImage-ready, Raspberry Pi (ARM) support

Note on development
The architecture of this project was co-designed with AI (Microsoft Copilot). Portions of the code were generated using GitHub Copilot in VS Code and have been reviewed and adapted.

Installation (local)

1. Clone and run the build script (produces AppImage):

```bash
git clone https://github.com/yourname/everyfind.git
cd everyfind
./build.sh x86_64      # or: ./build.sh aarch64
```

2. Development (virtualenv):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Common commands

```bash
everyfind index /path/to/index   # create index
everyfind search                 # interactive fzf search (CLI)
everyfind gui                    # launch GTK GUI
everyfind stats                  # show index stats
everyfind clear                  # clear index
```

### 🔧 Configuration

Everyfind stores its settings in `~/.config/everyfind/settings.json`. This file is automatically created when you change settings in the GUI.

Example configuration:

```json
{
  "indexed_paths": ["/home/user/Documents", "/home/user/Pictures"],
  "file_filters": ["*.pdf", "*.txt", ".doc", ".odt"],
  "excluded_paths": ["/home/user/Documents/temp", "/mnt", "/media"],
  "auto_reindex": true,
  "reindex_interval": 60,
  "language": "en"
}
```

**Configuration options:**

- **`indexed_paths`**: List of directories to index
- **`file_filters`**: List of file extensions or wildcard patterns (e.g., `*.txt`, `.pdf`, `*.py`)
  - Without filters, all files are indexed
  - Wildcards: `*.txt` matches all .txt files
  - Simple extensions: `.pdf` or `pdf` both work
- **`excluded_paths`**: Directory paths to ignore during indexing
  - Absolute paths or prefixes (e.g., `/mnt`, `/media`)
  - Default exclusions: `.git`, `__pycache__`, `.venv`, `node_modules`
- **`auto_reindex`**: Automatically reindex on program startup (true/false)
- **`reindex_interval`**: Time in minutes between automatic reindexing
- **`language`**: User interface language
  - `"de"` for German
  - `"en"` for English
  - `"system"` for system language

You can edit settings manually in the JSON file or conveniently change them via the GUI (Menu → Settings).

License
Everyfind is released under the GNU General Public License v3 (GPLv3). See `LICENSE`.

Contributing
See `CONTRIBUTING.md` for contribution guidelines, coding style, and the pull request workflow.

---

## 🖼️ Screenshots

### Hauptfenster

![Everyfind Hauptfenster](assets/screenshots/everyfind-main.png)

### Dateidetails

![Details-Dialog](assets/screenshots/everyfind-details.png)
If you use or distribute Everyfind, please respect the licenses of bundled components (e.g., fzf: MIT, PyGObject: LGPL, SQLite: Public Domain). If you have questions about licensing, open an issue.
