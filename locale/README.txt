This directory is intended to contain compiled gettext message catalogs (.mo files).

To compile .po files into .mo files for distribution, use msgfmt or pygettext tooling.

Example (msgfmt):
  msgfmt -o locale/de/LC_MESSAGES/everyfind.mo po/de/everyfind.po

Alternatively, you can add a build step to compile the PO files during packaging.
