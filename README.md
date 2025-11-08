# Everyfind

**Everyfind** ist eine ultraschnelle Dateisuche für Linux, inspiriert von „Everything“ unter Windows. Sie kombiniert die Geschwindigkeit von `fzf` mit einer modernen GTK-Oberfläche und ist vollständig GPL-lizenziert.

## Features

- 🔍 Fuzzy-Suche mit `fzf` über PTY
- 📁 Rekursive Indexierung mit SQLite
- 🖥️ GTK-GUI mit Doppelklick und Rechtsklick-Menü
- 🧰 CLI- und GUI-Modus
- 🧱 AppImage-kompatibel, Raspberry Pi-tauglich
- 🛡️ Lizenz: GPLv3

## Installation

Voraussetzungen: Python 3.10+, `pip`, `virtualenv` empfohlen.

Klonen und Build-Skript ausführen:

```bash
git clone https://github.com/deinname/everyfind.git
cd everyfind
./build.sh
```

Für Entwicklung in einem venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Nutzung

Indexieren:

```bash
everyfind index /pfad/zum/durchsuchen
```

Interaktive Suche (CLI):

```bash
everyfind search
```

GUI starten:

```bash
everyfind gui
```

## Lizenz

Dieses Projekt steht unter der GNU General Public License v3. Siehe `LICENSE` für Details.
