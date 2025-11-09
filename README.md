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
# GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
-->

# Everyfind

[![Build](https://github.com/Wacken2012/everyfind/actions/workflows/build.yml/badge.svg)](https://github.com/Wacken2012/everyfind/actions/workflows/build.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/Wacken2012/everyfind/releases)

🇩🇪 [Deutsch](#-deutsch) | 🇬🇧 [English](#-english)

---

## 🇩🇪 Deutsch

Everyfind ist eine ultraschnelle Dateisuche für Linux, inspiriert von "Everything" unter Windows. Es kombiniert die Geschwindigkeit von `fzf` mit einer GTK-Oberfläche und bietet sowohl eine CLI- als auch eine GUI-Oberfläche.

### ✨ Features

- **🚀 Ultraschnelle Suche** mit `fzf` (Fuzzy-Suche über PTY)
- **🖥️ Zwei Modi**: Kommandozeile (CLI) und grafische Oberfläche (GTK)
- **💾 Effiziente Indexierung** mit SQLite
- **🌍 Mehrsprachig**: Deutsch, Englisch, Französisch, Spanisch, Polnisch
- **📦 AppImage-fähig** – portable Installation ohne root
- **🍓 Raspberry Pi kompatibel** (ARM-Unterstützung)
- **⚙️ Hochgradig konfigurierbar** – Dateifilter, Ausschlüsse, Auto-Reindex

### 🤖 Hinweis zur Entstehung

Die Architektur dieses Projekts wurde gemeinsam mit einer KI (Microsoft Copilot) entworfen. Teile des Codes wurden mithilfe von GitHub Copilot in VS Code generiert. Alle von Copilot erzeugten Teile wurden überprüft und angepasst.

### 📥 Installation

#### AppImage (empfohlen)

1. Lade das AppImage für deine Architektur herunter:
   - [everyfind-0.1.0-x86_64.AppImage](https://github.com/Wacken2012/everyfind/releases/latest)
   - [everyfind-0.1.0-aarch64.AppImage](https://github.com/Wacken2012/everyfind/releases/latest) (ARM64)
   - [everyfind-0.1.0-armv7.AppImage](https://github.com/Wacken2012/everyfind/releases/latest) (ARM32)

2. Mache es ausführbar und starte es:

```bash
chmod +x everyfind-0.1.0-x86_64.AppImage
./everyfind-0.1.0-x86_64.AppImage
```

> ⚠️ **Hinweis zur Sprache im AppImage**: Das AppImage unterstützt derzeit nur Englisch. Für vollständige Mehrsprachigkeit bitte aus dem Quellcode installieren.

#### Von Quellcode bauen

1. Repository klonen und Build-Skript ausführen:

```bash
git clone https://github.com/Wacken2012/everyfind.git
cd everyfind
./build.sh x86_64      # oder: ./build.sh aarch64 / armv7
```

2. Für Entwicklung (virtuelle Umgebung):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 🚀 Nutzung

#### Häufige Befehle

```bash
# Index erstellen für Verzeichnis
everyfind index /pfad/zum/durchsuchen

# Interaktive Suche in der Kommandozeile
everyfind search

# GUI starten
everyfind gui

# Index-Statistiken anzeigen
everyfind stats

# Index löschen
everyfind clear
```

#### GUI-Modus

Im GUI-Modus kannst du:
- Dateien durch Fuzzy-Suche finden
- Doppelklick zum Öffnen von Dateien
- Rechtsklick-Kontextmenü:
  - Datei öffnen
  - In Terminal öffnen
  - Pfad kopieren
  - Details anzeigen
- Einstellungen konfigurieren (Menü → Einstellungen)

### 🔧 Konfiguration

Everyfind speichert seine Einstellungen in `~/.config/everyfind/settings.json`. Diese Datei wird automatisch erstellt, wenn du die Einstellungen in der GUI änderst.

#### Beispielkonfiguration

```json
{
  "indexed_paths": ["/home/stefan/Dokumente", "/home/stefan/Bilder"],
  "file_filters": ["*.pdf", "*.txt", "*.doc", "*.odt"],
  "excluded_paths": ["/home/stefan/Dokumente/temp", "/mnt", "/media"],
  "auto_reindex": true,
  "reindex_interval_minutes": 60,
  "language": "de"
}
```

#### Erklärung der Optionen

- **`indexed_paths`**: Liste von Verzeichnissen, die indexiert werden sollen
- **`file_filters`**: Liste von Dateiendungen oder Wildcard-Mustern
  - Beispiele: `*.txt`, `.pdf`, `*.py`
  - Ohne Filter werden alle Dateien indexiert
- **`excluded_paths`**: Verzeichnisse, die ignoriert werden
  - Standard-Ausschlüsse: `.git`, `__pycache__`, `.venv`, `node_modules`
- **`auto_reindex`**: Automatische Neuindexierung beim Start (true/false)
- **`reindex_interval_minutes`**: Minuten zwischen Auto-Reindex
- **`language`**: Sprache der Benutzeroberfläche
  - `"system"` – Systemsprache (Standard)
  - `"de"` – Deutsch
  - `"en"` – Englisch
  - `"fr"` – Französisch
  - `"es"` – Spanisch
  - `"pl"` – Polnisch

### 🌍 Übersetzungen

Everyfind ist mehrsprachig! Die Benutzeroberfläche ist in folgenden Sprachen verfügbar:

- 🇩🇪 **Deutsch** (de)
- 🇬🇧 **Englisch** (en)
- 🇫🇷 **Französisch** (fr)
- 🇪�� **Spanisch** (es)
- 🇵🇱 **Polnisch** (pl)

#### Sprache ändern

Du kannst die Sprache in den Einstellungen ändern:
1. Öffne die GUI: `everyfind gui`
2. Gehe zu **Datei** → **Einstellungen**
3. Wähle deine Sprache im Dropdown-Menü
4. Klicke auf **Speichern** und starte Everyfind neu

#### Mitwirken bei Übersetzungen

Möchtest du eine neue Sprache hinzufügen oder eine bestehende Übersetzung verbessern?

1. Erstelle/bearbeite eine `.po`-Datei in `po/<sprachcode>/everyfind.po`
2. Kompiliere sie mit `msgfmt po/<sprachcode>/everyfind.po -o locale/<sprachcode>/LC_MESSAGES/everyfind.mo`
3. Teste die Übersetzung lokal
4. Erstelle einen Pull Request!

Siehe [CONTRIBUTING.md#übersetzungen](CONTRIBUTING.md#übersetzungen-hinzufügen) für detaillierte Anweisungen.

### 🛣️ Roadmap

Geplante Features für zukünftige Versionen:

#### v0.2.0
- 🧰 **Plugin-System** – Erweiterbare Architektur
  - OCR-Plugin für Texterkennung in Bildern/PDFs
  - Dateivorschau-Plugin
  - Cloud-Integration (Nextcloud, Google Drive)
- 🧠 **Gewichtetes Ranking** – Intelligente Suchergebnisse basierend auf:
  - Zugriffshäufigkeit
  - Letzte Änderungen
  - Dateinamen-Übereinstimmung
- 🔍 **Erweiterte Suchfilter** – Größe, Datum, MIME-Type

#### v0.3.0+
- 📦 **Alternative Distributionen**
  - Flatpak-Package
  - Snap-Package
  - AUR (Arch User Repository)
- 🧪 **GUI-Tests** – Automatisierte UI-Tests mit pytest-gtk/dogtail
- 🌐 **Community-Übersetzungen** – Weblate-Integration
- 📊 **Erweiterte Statistiken** – Dashboard mit Visualisierungen
- 🎨 **Themes** – Dunkles Design, benutzerdefinierte Farbschemata

Hast du Feature-Wünsche? [Erstelle ein Feature-Request](https://github.com/Wacken2012/everyfind/issues/new?labels=enhancement)!

### 📜 Lizenz

Dieses Projekt steht unter der **GNU General Public License v3** (GPLv3).  
Siehe [LICENSE](LICENSE) für Details.

#### Lizenzhinweise für gebündelte Komponenten

- **fzf**: MIT License
- **PyGObject**: LGPL
- **SQLite**: Public Domain

Bei Fragen zur Lizenzierung öffne bitte ein Issue.

### 🤝 Mitwirken

Beiträge sind willkommen! Siehe [CONTRIBUTING.md](CONTRIBUTING.md) für:
- Entwicklungs-Workflow
- Code-Stil-Richtlinien
- Pull-Request-Prozess

### 📫 Kontakt & Support

- **Issues**: [GitHub Issues](https://github.com/Wacken2012/everyfind/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/Wacken2012/everyfind/discussions)

---

## 🇬🇧 English

Everyfind is a blazing-fast file search tool for Linux, inspired by "Everything" on Windows. It combines `fzf` speed with a GTK interface and provides both CLI and GUI frontends.

### ✨ Features

- **🚀 Lightning-fast search** powered by `fzf` (fuzzy search via PTY)
- **🖥️ Dual interfaces**: Command-line (CLI) and graphical (GTK)
- **�� Efficient indexing** using SQLite
- **🌍 Multilingual**: German, English, French, Spanish, Polish
- **📦 AppImage-ready** – portable installation without root
- **🍓 Raspberry Pi compatible** (ARM support)
- **⚙️ Highly configurable** – file filters, exclusions, auto-reindex

### 🤖 Note on Development

The architecture of this project was co-designed with AI (Microsoft Copilot). Portions of the code were generated using GitHub Copilot in VS Code and have been reviewed and adapted.

### 📥 Installation

#### AppImage (recommended)

1. Download the AppImage for your architecture:
   - [everyfind-0.1.0-x86_64.AppImage](https://github.com/Wacken2012/everyfind/releases/latest)
   - [everyfind-0.1.0-aarch64.AppImage](https://github.com/Wacken2012/everyfind/releases/latest) (ARM64)
   - [everyfind-0.1.0-armv7.AppImage](https://github.com/Wacken2012/everyfind/releases/latest) (ARM32)

2. Make it executable and run:

```bash
chmod +x everyfind-0.1.0-x86_64.AppImage
./everyfind-0.1.0-x86_64.AppImage
```

> ⚠️ **AppImage Language Support**: The AppImage currently supports English only. For full multilingual support, please install from source.

#### Build from Source

1. Clone the repository and run the build script:

```bash
git clone https://github.com/Wacken2012/everyfind.git
cd everyfind
./build.sh x86_64      # or: ./build.sh aarch64 / armv7
```

2. For development (virtual environment):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 🚀 Usage

#### Common Commands

```bash
# Index a directory
everyfind index /path/to/index

# Interactive CLI search
everyfind search

# Launch GUI
everyfind gui

# Show index statistics
everyfind stats

# Clear index
everyfind clear
```

#### GUI Mode

In GUI mode, you can:
- Find files using fuzzy search
- Double-click to open files
- Right-click context menu:
  - Open file
  - Open in terminal
  - Copy path
  - Show details
- Configure settings (Menu → Settings)

### 🔧 Configuration

Everyfind stores its settings in `~/.config/everyfind/settings.json`. This file is automatically created when you change settings in the GUI.

#### Example Configuration

```json
{
  "indexed_paths": ["/home/user/Documents", "/home/user/Pictures"],
  "file_filters": ["*.pdf", "*.txt", "*.doc", "*.odt"],
  "excluded_paths": ["/home/user/Documents/temp", "/mnt", "/media"],
  "auto_reindex": true,
  "reindex_interval_minutes": 60,
  "language": "en"
}
```

#### Configuration Options

- **`indexed_paths`**: List of directories to index
- **`file_filters`**: List of file extensions or wildcard patterns
  - Examples: `*.txt`, `.pdf`, `*.py`
  - Without filters, all files are indexed
- **`excluded_paths`**: Directories to ignore
  - Default exclusions: `.git`, `__pycache__`, `.venv`, `node_modules`
- **`auto_reindex`**: Automatically reindex on startup (true/false)
- **`reindex_interval_minutes`**: Minutes between auto-reindex
- **`language`**: User interface language
  - `"system"` – System language (default)
  - `"de"` – German
  - `"en"` – English
  - `"fr"` – French
  - `"es"` – Spanish
  - `"pl"` – Polish

### 🌍 Translations

Everyfind is multilingual! The user interface is available in:

- 🇬🇧 **English** (en)
- 🇩🇪 **German** (de)
- 🇫🇷 **French** (fr)
- 🇪🇸 **Spanish** (es)
- 🇵🇱 **Polish** (pl)

#### Changing Language

You can change the language in Settings:
1. Open the GUI: `everyfind gui`
2. Go to **File** → **Settings**
3. Select your language from the dropdown
4. Click **Save** and restart Everyfind

#### Contributing to Translations

Want to add a new language or improve an existing translation?

1. Create/edit a `.po` file in `po/<language_code>/everyfind.po`
2. Compile it with `msgfmt po/<language_code>/everyfind.po -o locale/<language_code>/LC_MESSAGES/everyfind.mo`
3. Test the translation locally
4. Create a pull request!

See [CONTRIBUTING.md#adding-translations](CONTRIBUTING.md#adding-translations) for detailed instructions.

### 🛣️ Roadmap

Planned features for future versions:

#### v0.2.0
- 🧰 **Plugin System** – Extensible architecture
  - OCR plugin for text recognition in images/PDFs
  - File preview plugin
  - Cloud integration (Nextcloud, Google Drive)
- 🧠 **Weighted Ranking** – Smart search results based on:
  - Access frequency
  - Recent modifications
  - Filename match quality
- 🔍 **Advanced Search Filters** – Size, date, MIME type

#### v0.3.0+
- 📦 **Alternative Distributions**
  - Flatpak package
  - Snap package
  - AUR (Arch User Repository)
- 🧪 **GUI Tests** – Automated UI testing with pytest-gtk/dogtail
- 🌐 **Community Translations** – Weblate integration
- 📊 **Extended Statistics** – Dashboard with visualizations
- 🎨 **Themes** – Dark mode, custom color schemes

Have a feature request? [Create a feature request](https://github.com/Wacken2012/everyfind/issues/new?labels=enhancement)!

### 📜 License

This project is released under the **GNU General Public License v3** (GPLv3).  
See [LICENSE](LICENSE) for details.

#### License Notes for Bundled Components

- **fzf**: MIT License
- **PyGObject**: LGPL
- **SQLite**: Public Domain

If you have questions about licensing, please open an issue.

### 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development workflow
- Code style guidelines
- Pull request process

### 📫 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/Wacken2012/everyfind/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Wacken2012/everyfind/discussions)

---

## 🖼️ Screenshots

### Main Window / Hauptfenster

![Everyfind Main Window](assets/screenshots/everyfind-main.png)

---

**Made with ❤️ and 🤖 for the Linux community**
