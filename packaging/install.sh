#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="${HOME}/.local/share/plasma-domotik"
PLASMOID_ID="io.github.davvore33.PlasmaDomotik"

echo "=== Plasma Domotik Installer ==="
echo ""

# Check dependencies
echo "Checking dependencies..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Install it with: sudo pacman -S nodejs npm"
    exit 1
fi
echo "  Node.js: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is not installed"
    exit 1
fi

# Install project dependencies
echo ""
echo "Installing Node.js dependencies..."
cd "$SCRIPT_DIR"
npm install --omit=dev

# Install Python dependencies (optional, for backend tests)
if command -v python3 &> /dev/null; then
    echo ""
    echo "Installing Python dependencies..."
    python3 -m venv "$SCRIPT_DIR/venv"
    source "$SCRIPT_DIR/venv/bin/activate"
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
    pip install -q pytest
    deactivate
fi

# Install Node adapter
echo ""
echo "Installing Node adapter to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/backend" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/node_modules" "$INSTALL_DIR/"

# Install systemd service
echo ""
echo "Installing systemd user service..."
SYSTEMD_DIR="${HOME}/.config/systemd/user"
mkdir -p "$SYSTEMD_DIR"
cp "$SCRIPT_DIR/packaging/plasma-domotik-adapter.service" "$SYSTEMD_DIR/"
systemctl --user daemon-reload
systemctl --user enable plasma-domotik-adapter.service
echo "  Service enabled. Start with: systemctl --user start plasma-domotik-adapter"

# Install plasmoid
echo ""
echo "Installing Plasma plasmoid..."
PLASMOID_DIR="${HOME}/.local/share/plasma/plasmoids/${PLASMOID_ID}"
rm -rf "$PLASMOID_DIR"
cp -r "$SCRIPT_DIR/plasmoid/package" "$PLASMOID_DIR"
echo "  Plasmoid installed to: $PLASMOID_DIR"

echo ""
echo "=== Installation complete ==="
echo ""
echo "Next steps:"
echo "1. Start the adapter: systemctl --user start plasma-domotik-adapter"
echo "2. Check status: systemctl --user status plasma-domotik-adapter"
echo "3. Add the widget to your panel via 'Add Widgets' → 'Plasma Domotik'"
echo "4. Configure the widget with your gateway IP and security code"
echo ""
echo "To uninstall:"
echo "  systemctl --user disable --now plasma-domotik-adapter"
echo "  rm -rf $INSTALL_DIR"
echo "  rm -rf $PLASMOID_DIR"
echo "  rm $SYSTEMD_DIR/plasma-domotik-adapter.service"
