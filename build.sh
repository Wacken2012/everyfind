echo "Cleaning previous build..."
echo "Creating AppDir structure..."
echo "Creating Python virtual environment..."
echo "Installing Python dependencies..."
echo "Creating launcher script..."
echo "Creating desktop file..."
echo "Creating application icon..."
echo "Building AppImage..."
#!/usr/bin/env bash
# Everyfind - AppImage Build Script
# Copyright (C) 2025 Stefan
# Licensed under GPL-3.0-or-later

set -euo pipefail

APP_NAME="everyfind"
APP_DISPLAY_NAME="Everyfind"
APP_VERSION="0.1.0"
BUILD_DIR="build"
ASSETS_DIR="assets"

usage() {
    cat <<EOF
Usage: $0 [arch]

Build an AppImage for Everyfind. arch can be one of:
  x86_64    (default)
  aarch64   (ARM64)
  armv7     (ARMv7/armhf)
  --all     build all supported architectures (may require native machines)

Example: $0 x86_64
EOF
}

TARGETS=()
if [ "${1:-}" = "--all" ]; then
    TARGETS=(x86_64 aarch64 armv7)
elif [ -n "${1:-}" ]; then
    TARGETS=($1)
else
    TARGETS=(x86_64)
fi

mkdir -p "${BUILD_DIR}"
mkdir -p "${ASSETS_DIR}"

FZF_VERSION="0.44.1"
APPIMAGETOOL_BASE_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous"

for TARGET in "${TARGETS[@]}"; do
    echo "\n===== Building AppImage for: ${TARGET} ====="

    case "${TARGET}" in
        x86_64)
            FZF_ARCH="amd64"; APPIMAGETOOL_NAME="appimagetool-x86_64.AppImage"; APPARCH="x86_64" ;;
        aarch64)
            FZF_ARCH="arm64"; APPIMAGETOOL_NAME="appimagetool-aarch64.AppImage"; APPARCH="aarch64" ;;
        armv7)
            FZF_ARCH="armv7"; APPIMAGETOOL_NAME="appimagetool-armhf.AppImage"; APPARCH="armv7" ;;
        *)
            echo "Unknown target: ${TARGET}"; continue ;;
    esac

    APPDIR="${BUILD_DIR}/${APP_NAME}-${TARGET}.AppDir"
    rm -rf "${APPDIR}"
    mkdir -p "${APPDIR}/usr/bin" "${APPDIR}/usr/lib" "${APPDIR}/usr/share/applications" "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

    # Create virtualenv inside AppDir so it becomes portable
    echo "Creating virtualenv inside AppDir..."
    python3 -m venv "${APPDIR}/usr/venv"
    # Activate and install dependencies into venv
    set +u
    source "${APPDIR}/usr/venv/bin/activate"
    set -u

    echo "Upgrading pip and installing requirements into venv..."
    pip install --upgrade pip wheel setuptools
    if [ -f "requirements.txt" ]; then
        pip install --no-cache-dir -r requirements.txt
    fi
    # Install local package into venv (editable not required for runtime)
    pip install --no-cache-dir .

    # Ensure python binary is present (symlink to venv python)
    ln -sf ../venv/bin/python3 "${APPDIR}/usr/bin/python3"

    # Download fzf binary for target
    FZF_TAR="/tmp/fzf-${FZF_VERSION}-${FZF_ARCH}.tar.gz"
    FZF_BIN_TARGET="${APPDIR}/usr/bin/fzf"
    if [ -f "${FZF_BIN_TARGET}" ]; then
        echo "fzf already present in AppDir"
    else
        echo "Downloading fzf (${FZF_ARCH})..."
        wget -q -O "${FZF_TAR}" \
            "https://github.com/junegunn/fzf/releases/download/${FZF_VERSION}/fzf-${FZF_VERSION}-linux_${FZF_ARCH}.tar.gz"
        tar -xzf "${FZF_TAR}" -C "${APPDIR}/usr/bin"
        chmod +x "${FZF_BIN_TARGET}" || true
        rm -f "${FZF_TAR}"
    fi

    # Create AppRun launcher
    cat > "${APPDIR}/AppRun" <<'APP_RUN_EOF'
#!/usr/bin/env bash
APPDIR="$(dirname "$(readlink -f "$0")")"
export PATH="$APPDIR/usr/bin:$PATH"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$LD_LIBRARY_PATH"

# Activate virtualenv shipped inside AppDir
if [ -f "$APPDIR/usr/venv/bin/activate" ]; then
    # shellcheck disable=SC1090
    source "$APPDIR/usr/venv/bin/activate"
fi

# Dispatch to CLI or GUI depending on args
if [ "$#" -gt 0 ]; then
    case "$1" in
        index|search|stats|clear|--cli)
            exec python3 -m everyfind.cli "$@"
            ;;
    esac
fi

# Default: start GUI
exec python3 -m everyfind.ui "$@"
APP_RUN_EOF

    chmod +x "${APPDIR}/AppRun"

    # Create desktop file
    DESKTOP_FILE="${APPDIR}/usr/share/applications/${APP_NAME}.desktop"
    cat > "${DESKTOP_FILE}" <<DESK_EOF
[Desktop Entry]
Type=Application
Name=${APP_DISPLAY_NAME}
Comment=Ultra-fast file search for Linux
Exec=AppRun
Icon=${APP_NAME}
Categories=Utility;GTK;
Terminal=false
DESK_EOF

    cp "${DESKTOP_FILE}" "${APPDIR}/${APP_NAME}.desktop"

    # Create or copy icon
    ICON_SRC="${ASSETS_DIR}/${APP_NAME}.png"
    if [ -f "${ICON_SRC}" ]; then
        cp "${ICON_SRC}" "${APPDIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
        cp "${ICON_SRC}" "${APPDIR}/${APP_NAME}.png"
    else
        echo "No icon in ${ICON_SRC}. Attempting to generate placeholder if 'convert' is available..."
        if command -v convert >/dev/null 2>&1; then
            convert -size 256x256 xc:'#2d6cdf' -gravity center -pointsize 96 -fill white -annotate +0+0 "EF" \
                "${APPDIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
            cp "${APPDIR}/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png" "${APPDIR}/${APP_NAME}.png"
        else
            echo "ImageMagick not available; please add ${ASSETS_DIR}/${APP_NAME}.png to include an icon."
        fi
    fi

    # Include AppStream metadata if available
    APPSTREAM_SRC="${ASSETS_DIR}/${APP_NAME}.appdata.xml"
    if [ -f "${APPSTREAM_SRC}" ]; then
        mkdir -p "${APPDIR}/usr/share/metainfo"
        cp "${APPSTREAM_SRC}" "${APPDIR}/usr/share/metainfo/${APP_NAME}.appdata.xml"
        echo "Included AppStream metadata: ${APPSTREAM_SRC}"
    else
        echo "No AppStream metadata found at ${APPSTREAM_SRC}; continuing without it."
    fi

    # Download appimagetool
    APPIMAGETOOL_PATH="${BUILD_DIR}/${APPIMAGETOOL_NAME}"
    if [ ! -f "${APPIMAGETOOL_PATH}" ]; then
        echo "Downloading ${APPIMAGETOOL_NAME}..."
        wget -q -O "${APPIMAGETOOL_PATH}" "${APPIMAGETOOL_BASE_URL}/${APPIMAGETOOL_NAME}"
        chmod +x "${APPIMAGETOOL_PATH}"
    fi

    # Build AppImage
    OUT_IMAGE="${BUILD_DIR}/${APP_NAME}-${APP_VERSION}-${APPARCH}.AppImage"
    echo "Building AppImage -> ${OUT_IMAGE}"

    # appimagetool usually must run on the target architecture. If building cross-arch, this may fail.
    "${APPIMAGETOOL_PATH}" "${APPDIR}" "${OUT_IMAGE}"

    echo "Built: ${OUT_IMAGE}"

    echo "Cleaning up venv activation in shell..."
    # deactivate venv in current shell
    set +u
    deactivate 2>/dev/null || true
    set -u

done

echo "\nAll requested builds finished. Artifacts in ${BUILD_DIR}/"

echo "Notes:"
echo " - The AppImage bundles the Python venv (site-packages) and the fzf binary."
echo " - PyGObject (GTK) may require system libraries (libgtk-3) on target systems; bundling full GTK runtime is non-trivial."
echo " - For offline runtime, ensure target systems have GTK runtime installed or build on a compatible environment and include required libs."

