#!/usr/bin/env bash
# Quick Creator Pro - Release Builder

set -Eeuo pipefail

# ==============================
# CONFIG
# ==============================
APP_NAME="quick_creator"
ENTRY_FILE="quick_creator.py"
PROJECT_DIR="$(pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

# ==============================
# COLORS
# ==============================
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
CYAN="\033[1;36m"
MAGENTA="\033[1;35m"
NC="\033[0m"

echo -e "${CYAN}====================================${NC}"
echo -e "${MAGENTA}  Quick Creator Pro Release Build  ${NC}"
echo -e "${CYAN}====================================${NC}"
echo

# ==============================
# Detect python binary
# ==============================
PYTHON_BIN=""
if command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
    PYTHON_BIN="python"
else
    echo -e "${RED}❌ Python not found. Please install python3.${NC}"
    exit 1
fi
echo -e "${GREEN}✔ Python found:${NC} $($PYTHON_BIN --version)"

# ==============================
# Check python3-venv / venv module
# ==============================
if ! "$PYTHON_BIN" -m venv --help &>/dev/null; then
    echo -e "${RED}❌ python3-venv not available.${NC}"
    echo -e "${YELLOW}   On Debian/Ubuntu: sudo apt install python3-venv${NC}"
    exit 1
fi
echo -e "${GREEN}✔ venv module available.${NC}"

# ==============================
# Clean old builds
# ==============================
echo
echo -e "${CYAN}🧹 Cleaning old build files...${NC}"
rm -rf "$PROJECT_DIR/build" "$PROJECT_DIR/dist" "$PROJECT_DIR/__pycache__" "$PROJECT_DIR"/*.spec || true

# ==============================
# Create .venv
# ==============================
echo
echo -e "${CYAN}🐍 Creating virtual environment...${NC}"
"$PYTHON_BIN" -m venv "$VENV_DIR"
VENV_PIP="$VENV_DIR/bin/pip"
VENV_PYTHON="$VENV_DIR/bin/python"

# ==============================
# Install dependencies inside venv
# ==============================
echo -e "${CYAN}📦 Installing PyInstaller and PyQt6...${NC}"
"$VENV_PIP" install --upgrade pip --quiet
"$VENV_PIP" install pyinstaller pyqt6 --quiet
echo -e "${GREEN}✔ Dependencies installed.${NC}"

# ==============================
# Build
# ==============================
echo
echo -e "${GREEN}🚀 Building binary...${NC}"

"$VENV_PYTHON" -m PyInstaller \
    --onefile \
    --windowed \
    --clean \
    --noconfirm \
    --name "$APP_NAME" \
    "$ENTRY_FILE"

# ==============================
# Move binary to root
# ==============================
if [[ -f "$PROJECT_DIR/dist/$APP_NAME" ]]; then
    if [[ -f "$PROJECT_DIR/$APP_NAME" ]]; then
        echo -e "${YELLOW}🗑  Removing old binary...${NC}"
        rm -f "$PROJECT_DIR/$APP_NAME"
    fi
    echo -e "${CYAN}➜ Moving binary to project root...${NC}"
    mv -f "$PROJECT_DIR/dist/$APP_NAME" "$PROJECT_DIR/"
    chmod +x "$PROJECT_DIR/$APP_NAME"
else
    echo -e "${RED}❌ Build failed. Binary not found in dist/.${NC}"
    # Cleanup venv before exit
    rm -rf "$VENV_DIR"
    exit 1
fi

# ==============================
# Final Cleanup
# ==============================
echo
echo -e "${CYAN}🧼 Removing build artifacts...${NC}"
rm -rf "$PROJECT_DIR/build" "$PROJECT_DIR/dist" "$PROJECT_DIR/__pycache__" "$PROJECT_DIR"/*.spec || true

echo -e "${CYAN}🗑  Removing virtual environment...${NC}"
rm -rf "$VENV_DIR"

echo
echo -e "${GREEN}✅ Release Ready!${NC}"
echo -e "${CYAN}Binary Location:${NC} $PROJECT_DIR/$APP_NAME"
echo
