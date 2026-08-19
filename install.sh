#!/usr/bin/env bash
# One-line installer for md2pdf
set -euo pipefail

INSTALL_DIR="${HOME}/.local/bin"
VENV_DIR="${HOME}/.local/share/md2pdf_venv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installing md2pdf ==="

mkdir -p "$INSTALL_DIR" "$VENV_DIR"

if [ ! -f "${VENV_DIR}/bin/python3" ]; then
    echo "Creating Python virtual environment in ${VENV_DIR}..."
    python3 -m venv "$VENV_DIR"
fi

echo "Installing required dependencies..."
"${VENV_DIR}/bin/pip" install --upgrade pip >/dev/null 2>&1 || true
"${VENV_DIR}/bin/pip" install -e "$SCRIPT_DIR"

# Link CLI binary to ~/.local/bin
ln -sf "${VENV_DIR}/bin/md2pdf" "${INSTALL_DIR}/md2pdf"

echo "✓ Successfully installed md2pdf to ${INSTALL_DIR}/md2pdf"
echo ""
echo "Ensure ${INSTALL_DIR} is in your PATH (e.g., export PATH=\"\$HOME/.local/bin:\$PATH\")"
echo "Try running: md2pdf --help"
