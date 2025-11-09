# 🎉 Everyfind v0.1.0 - Initial Release

Welcome to the first official release of **Everyfind** – a blazing-fast file search tool for Linux! 🚀

## ✨ What's New

### 🌍 Multilingual Support (i18n)
Everyfind speaks your language! The UI is now available in:
- 🇩🇪 **German** (Deutsch)
- 🇬🇧 **English**
- 🇫🇷 **French** (Français)
- 🇪🇸 **Spanish** (Español)
- 🇵🇱 **Polish** (Polski)

Change the language in **Settings** → **Language** or set it via `settings.json`.

### 🖥️ Dual Interface
- **CLI Mode** – Fuzzy search in your terminal with `everyfind search`
- **GUI Mode** – Beautiful GTK interface with `everyfind gui`

### 🚀 Core Features
- ⚡ **Lightning-fast search** powered by `fzf` (fuzzy finder)
- 💾 **SQLite indexing** for instant results
- 🔍 **Configurable filters** – file types, excluded paths
- 🔄 **Auto-reindexing** – keep your index up-to-date
- 📦 **Portable** – AppImage support (no installation needed!)
- 🍓 **Raspberry Pi compatible** – ARM architecture support

### 🎨 User Interface
- Double-click to open files
- Right-click context menu:
  - 📂 Open file
  - 🖥️ Open in terminal
  - 📋 Copy path
  - ℹ️ Show details
- Comprehensive settings dialog

## 📦 Downloads

### Debian Package (Recommended for Debian/Ubuntu)

**Full multilingual support included!** 🌍

| Format | Download | Size |
|--------|----------|------|
| **DEB** | [everyfind_0.1.0-1_all.deb](https://github.com/Wacken2012/everyfind/releases/download/v0.1.0/everyfind_0.1.0-1_all.deb) | 24 KB |

**Installation:**
```bash
# Download the package
wget https://github.com/Wacken2012/everyfind/releases/download/v0.1.0/everyfind_0.1.0-1_all.deb

# Install (automatically resolves dependencies)
sudo dpkg -i everyfind_0.1.0-1_all.deb
sudo apt-get install -f

# Run the application
everyfind gui
```

**Advantages:**
- ✅ Includes all 5 language translations
- ✅ Desktop integration (application menu)
- ✅ Automatic dependency management
- ✅ Easy system-wide installation

### AppImage (Portable)

**For systems without package manager:**

| Architecture | Download | Size |
|--------------|----------|------|
| **x86_64** (Intel/AMD 64-bit) | [everyfind-0.1.0-x86_64.AppImage](https://github.com/Wacken2012/everyfind/releases/download/v0.1.0/everyfind-0.1.0-x86_64.AppImage) | 9.8 MB |

**Quick Start:**
```bash
# Download and make executable
chmod +x everyfind-0.1.0-x86_64.AppImage

# Run the application
./everyfind-0.1.0-x86_64.AppImage
```

> ⚠️ **Note**: The AppImage currently supports **English only**. For full multilingual support, use the Debian package or [install from source](https://github.com/Wacken2012/everyfind#build-from-source).

### Build from Source

See the [README](https://github.com/Wacken2012/everyfind#installation) for complete instructions.

## 🔧 Configuration

Everyfind stores settings in `~/.config/everyfind/settings.json`:

```json
{
  "indexed_paths": ["/home/user/Documents"],
  "file_filters": ["*.pdf", "*.txt", "*.doc"],
  "excluded_paths": ["/tmp", "/var"],
  "auto_reindex": true,
  "reindex_interval_minutes": 60,
  "language": "de"
}
```

## 🐛 Known Issues

### AppImage Locale Files
The AppImage does not currently include locale files due to an `appimagetool` limitation. This means:
- ❌ Language selection in AppImage shows only English
- ✅ All other functionality works perfectly
- ✅ Full i18n support available when installed from source

**Workaround**: Install from source for multilingual support:
```bash
git clone https://github.com/Wacken2012/everyfind.git
cd everyfind
pip install -e .
everyfind gui
```

We're actively investigating solutions for the next release.

## 🧪 Testing

This release includes:
- ✅ **28 automated tests** (19 core + 9 i18n)
- ✅ All tests passing
- ✅ Tested on x86_64 Linux

## 🤝 Contributing

We welcome contributions! Check out:
- [CONTRIBUTING.md](https://github.com/Wacken2012/everyfind/blob/main/CONTRIBUTING.md) – Development guidelines
- [Open Issues](https://github.com/Wacken2012/everyfind/issues) – Help wanted!
- [Discussions](https://github.com/Wacken2012/everyfind/discussions) – Share ideas

### 🌍 Help Translate
Want to add your language? We'd love to have:
- 🇮🇹 Italian
- 🇯🇵 Japanese
- 🇷🇺 Russian
- 🇨🇳 Chinese
- And many more!

See [CONTRIBUTING.md#translations](https://github.com/Wacken2012/everyfind/blob/main/CONTRIBUTING.md#übersetzungen-hinzufügen) for instructions.

## 🛣️ Roadmap

### Planned for v0.2.0
- 🧰 Plugin system (OCR, file preview)
- 🧠 Weighted search ranking
- 🔍 Advanced filters (size, date, MIME type)
- 🌐 Weblate integration for community translations

### Future Ideas
- 📦 Flatpak/Snap packages
- 🧪 Automated GUI tests
- 🎨 Dark theme
- 📊 Statistics dashboard

## 📊 Statistics

- **Lines of Code**: ~2,000 (excluding tests)
- **Test Coverage**: 28 tests, all passing
- **Languages Supported**: 5
- **Translation Strings**: ~50 per language
- **AppImage Size**: 9.8 MB

## 📜 License

Everyfind is licensed under **GNU GPL v3**.

This ensures the software remains free and open-source forever. See [LICENSE](https://github.com/Wacken2012/everyfind/blob/main/LICENSE) for details.

### Bundled Components
- **fzf**: MIT License ✅
- **PyGObject**: LGPL ✅
- **SQLite**: Public Domain ✅

## 🙏 Acknowledgments

- Inspired by [Everything](https://www.voidtools.com/) for Windows
- Built with [fzf](https://github.com/junegunn/fzf) by Junegunn Choi
- Developed with assistance from AI (GitHub Copilot)
- Thanks to all contributors and testers!

## 📫 Support

- 🐛 [Report a Bug](https://github.com/Wacken2012/everyfind/issues/new?labels=bug)
- 💡 [Request a Feature](https://github.com/Wacken2012/everyfind/issues/new?labels=enhancement)
- 💬 [Join Discussion](https://github.com/Wacken2012/everyfind/discussions)

---

**Made with ❤️ and 🤖 for the Linux community**

*Enjoy searching at the speed of thought!* ⚡

