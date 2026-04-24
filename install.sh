#!/bin/bash
# Lightning Bottle Animator Installation Script for Linux Mint
# Run with: sudo ./install.sh

set -e

APP_NAME="lightning-bottle-animator"
APP_DIR="/opt/$APP_NAME"
BIN_LINK="/usr/local/bin/lightning-bottle-animator"
DESKTOP_FILE="/usr/share/applications/lightning-bottle-animator.desktop"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Lightning Bottle Animator - Installation Script          ║"
echo "║                    For Linux Mint                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (sudo ./install.sh)"
    exit 1
fi

# Check Python version
echo "🔍 Checking Python version..."
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "   Found Python $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo "   Found Python $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.x"
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
$PYTHON_CMD -m pip install Pillow --quiet 2>/dev/null || {
    echo "   Installing pip first..."
    apt-get update -qq
    apt-get install -y python3-pip python3-tk -qq
    $PYTHON_CMD -m pip install Pillow --quiet
}

# Create application directory
echo ""
echo "📁 Creating application directory..."
mkdir -p "$APP_DIR"

# Copy application files
echo "📂 Copying application files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_DIR/src" "$APP_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$APP_DIR/" 2>/dev/null || true

# Create launcher script
echo "🚀 Creating launcher script..."
cat > "$APP_DIR/launch.sh" << 'LAUNCH_SCRIPT'
#!/bin/bash
cd /opt/lightning-bottle-animator
python3 src/main.py "$@"
LAUNCH_SCRIPT
chmod +x "$APP_DIR/launch.sh"

# Create symbolic link
echo "🔗 Creating symbolic link..."
ln -sf "$APP_DIR/launch.sh" "$BIN_LINK"

# Create desktop entry
echo "🖥️  Creating desktop entry..."
mkdir -p /usr/share/applications
cat > "$DESKTOP_FILE" << 'DESKTOP_ENTRY'
[Desktop Entry]
Version=1.0
Name=Lightning Bottle Animator
Comment=Retro-styled animation and drawing application
Exec=lightning-bottle-animator
Icon=applications-graphics
Terminal=false
Type=Application
Categories=Graphics;2DGraphics;RasterGraphics;Art;
Keywords=animation;drawing;paint;graphics;retro;cartoon;
StartupNotify=true
DESKTOP_ENTRY

# Set permissions
chmod 644 "$DESKTOP_FILE"

# Update desktop database
echo "📋 Updating desktop database..."
update-desktop-database /usr/share/applications 2>/dev/null || true

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ Installation Complete!                   ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  Lightning Bottle Animator is now installed!                 ║"
echo "║                                                              ║"
echo "║  🚀 Launch from:                                             ║"
echo "║     • Menu → Graphics → Lightning Bottle Animator           ║"
echo "║     • Terminal: lightning-bottle-animator                    ║"
echo "║                                                              ║"
echo "║  📁 Installed to: $APP_DIR"
echo "║                                                              ║"
echo "║  🗑️  To uninstall: sudo ./uninstall.sh                       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"