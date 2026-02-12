#!/bin/bash
# =============================================================================
# JARVIS INSTALLATION SCRIPT FOR TERMUX (ROOTED ANDROID)
# =============================================================================
# 
# Purpose: Install all dependencies and setup JARVIS on Termux
#
# Requirements:
#   - Termux (from F-Droid, NOT Play Store)
#   - Rooted Android device (Magisk recommended)
#   - 4GB+ RAM
#   - 2GB+ free storage
#   - Internet connection for initial setup
#
# Usage:
#   chmod +x install.sh
#   ./install.sh
#
# Rollback:
#   If installation fails, run: ./uninstall.sh
#   Or manually: rm -rf ~/jarvis
#
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${2}${1}${NC}"
}

print_success() {
    print_msg "✓ $1" "$GREEN"
}

print_error() {
    print_msg "✗ $1" "$RED"
}

print_warning() {
    print_msg "⚠ $1" "$YELLOW"
}

print_info() {
    print_msg "ℹ $1" "$BLUE"
}

# =============================================================================
# STEP 1: CHECK REQUIREMENTS
# =============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "           JARVIS INSTALLATION FOR TERMUX"
echo "═══════════════════════════════════════════════════════════════"
echo ""

print_info "Step 1: Checking requirements..."
echo ""

# Check if running in Termux
if [ -z "$TERMUX_VERSION" ]; then
    print_warning "Not running in Termux. Some features may not work."
else
    print_success "Running in Termux $TERMUX_VERSION"
fi

# Check architecture
ARCH=$(uname -m)
print_info "Architecture: $ARCH"
if [ "$ARCH" != "aarch64" ] && [ "$ARCH" != "arm64" ]; then
    print_warning "Architecture $ARCH may not be fully supported"
fi

# Check available storage
AVAILABLE_STORAGE=$(df -h ~ | tail -1 | awk '{print $4}' | sed 's/G//')
print_info "Available storage: ${AVAILABLE_STORAGE}GB"
if [ "$(echo "$AVAILABLE_STORAGE < 2" | bc)" -eq 1 ]; then
    print_error "Insufficient storage. Need at least 2GB free."
    exit 1
fi

# Check RAM
TOTAL_MEM=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MEM_MB=$((TOTAL_MEM / 1024))
print_info "Total RAM: ${MEM_MB}MB"
if [ "$MEM_MB" -lt 3000 ]; then
    print_warning "Low RAM. AI features may be slow."
fi

# Check root access
print_info "Checking root access..."
if [ -f "/system/bin/su" ] || [ -f "/system/xbin/su" ] || [ -f "/sbin/su" ]; then
    if su -c "id" 2>/dev/null | grep -q "uid=0"; then
        print_success "Root access available"
        ROOT_AVAILABLE=true
    else
        print_warning "Root binary found but access denied"
        ROOT_AVAILABLE=false
    fi
else
    print_warning "No root access - Focus module will be limited"
    ROOT_AVAILABLE=false
fi

echo ""
read -p "Continue with installation? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Installation cancelled."
    exit 0
fi

# =============================================================================
# STEP 2: UPDATE SYSTEM
# =============================================================================

echo ""
print_info "Step 2: Updating system packages..."
echo ""

pkg update -y
pkg upgrade -y
print_success "System packages updated"

# =============================================================================
# STEP 3: INSTALL BASE DEPENDENCIES
# =============================================================================

echo ""
print_info "Step 3: Installing base dependencies..."
echo ""

# Core packages
pkg install -y python python-pip git wget curl
pkg install -y build-essential cmake clang
pkg install -y sqlite
print_success "Base dependencies installed"

# Python development
pkg install -y python-dev libffi-dev openssl-dev
print_success "Python development packages installed"

# Termux extras
pkg install -y termux-api termux-exec
if [ "$ROOT_AVAILABLE" = true ]; then
    pkg install -y root-repo tsu
    print_success "Root packages installed"
fi

# =============================================================================
# STEP 4: INSTALL PYTHON DEPENDENCIES
# =============================================================================

echo ""
print_info "Step 4: Installing Python packages..."
echo ""

# Create requirements.txt if not exists
REQUIREMENTS_FILE="$HOME/jarvis/requirements.txt"

if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install -r "$REQUIREMENTS_FILE"
    print_success "Python packages installed from requirements.txt"
else
    # Install core packages manually
    pip install textual==0.47.1
    pip install aiosqlite==0.19.0
    pip install python-dateutil==2.8.2
    pip install pydantic==2.5.3
    pip install pytest==7.4.3 pytest-asyncio==0.21.1
    print_success "Python packages installed"
fi

# =============================================================================
# STEP 5: BUILD LLAMA.CPP (FOR LOCAL AI)
# =============================================================================

echo ""
print_info "Step 5: Building llama.cpp for local AI..."
echo ""

LLAMA_DIR="$HOME/llama.cpp"

if [ -d "$LLAMA_DIR" ]; then
    print_info "llama.cpp already exists, skipping..."
else
    print_info "Cloning llama.cpp..."
    git clone https://github.com/ggml-org/llama.cpp "$LLAMA_DIR"
    cd "$LLAMA_DIR"
    
    print_info "Building llama.cpp (this may take 10-15 minutes)..."
    cmake -B build
    cmake --build build --config Release -j$(nproc)
    
    print_success "llama.cpp built successfully"
    
    # Test the binary
    if [ -f "$LLAMA_DIR/build/bin/llama-cli" ]; then
        print_success "llama-cli binary verified"
    else
        print_error "llama-cli binary not found"
    fi
    
    cd ~
fi

# =============================================================================
# STEP 6: DOWNLOAD AI MODEL (OPTIONAL)
# =============================================================================

echo ""
print_info "Step 6: AI Model Setup"
echo ""

MODELS_DIR="$HOME/jarvis/models"
mkdir -p "$MODELS_DIR"

print_info "The AI model (DeepSeek-R1:1.5B Q4_K_M) is ~1.1GB"
print_info "Download options:"
echo "  1. Download now (requires 1.1GB data)"
echo "  2. Download later manually"
echo "  3. Skip (use without AI features)"
echo ""
read -p "Choose option (1/2/3): " -n 1 -r MODEL_CHOICE
echo ""

if [ "$MODEL_CHOICE" = "1" ]; then
    print_info "Downloading DeepSeek-R1:1.5B Q4_K_M model..."
    print_warning "This may take 10-30 minutes depending on your connection..."
    
    MODEL_URL="https://huggingface.co/DevQuasar/deepseek-ai.DeepSeek-R1-Distill-Qwen-1.5B-GGUF/resolve/main/deepseek-ai.DeepSeek-R1-Distill-Qwen-1.5B.Q4_K_M.gguf"
    
    wget -O "$MODELS_DIR/deepseek-r1-1.5b-q4_k_m.gguf" "$MODEL_URL"
    
    if [ -f "$MODELS_DIR/deepseek-r1-1.5b-q4_k_m.gguf" ]; then
        MODEL_SIZE=$(stat -c%s "$MODELS_DIR/deepseek-r1-1.5b-q4_k_m.gguf" 2>/dev/null || echo "unknown")
        print_success "Model downloaded (${MODEL_SIZE} bytes)"
    else
        print_error "Model download failed"
    fi
else
    print_info "Model download skipped. You can download later with:"
    echo "  wget -O ~/jarvis/models/deepseek-r1-1.5b-q4_k_m.gguf [URL]"
fi

# =============================================================================
# STEP 7: INITIALIZE JARVIS DATABASE
# =============================================================================

echo ""
print_info "Step 7: Initializing JARVIS database..."
echo ""

JARVIS_DIR="$HOME/jarvis"

if [ -d "$JARVIS_DIR" ]; then
    cd "$JARVIS_DIR"
    python main.py --setup
    print_success "JARVIS database initialized"
else
    print_error "JARVIS directory not found"
    print_info "Make sure to clone/copy JARVIS to ~/jarvis"
fi

# =============================================================================
# STEP 8: CONFIGURE DISTRACTION BLOCKING (IF ROOT)
# =============================================================================

if [ "$ROOT_AVAILABLE" = true ]; then
    echo ""
    print_info "Step 8: Configuring distraction blocking..."
    echo ""
    
    # Create hosts file entries for adult sites
    print_info "Adding adult site blocks to hosts file..."
    
    HOSTS_BACKUP="/data/misc/hosts.backup"
    HOSTS_FILE="/system/etc/hosts"
    
    # Backup original hosts
    su -c "cp $HOSTS_FILE $HOSTS_BACKUP" 2>/dev/null || true
    
    # Add common adult sites (basic list)
    su -c "cat >> $HOSTS_FILE << 'EOF'
# JARVIS - Adult Content Block
127.0.0.1 pornhub.com
127.0.0.1 xvideos.com
127.0.0.1 xnxx.com
127.0.0.1 xhamster.com
127.0.0.1 redtube.com
127.0.0.1 youporn.com
EOF" 2>/dev/null && print_success "Adult sites blocked" || print_warning "Could not modify hosts file"
    
    # Set DNS to family-safe
    print_info "Consider setting DNS to 1.1.1.3 (Cloudflare Family)"
else
    print_info "Step 8: Skipped (no root access)"
fi

# =============================================================================
# STEP 9: CREATE SHORTCUTS
# =============================================================================

echo ""
print_info "Step 9: Creating shortcuts..."
echo ""

# Create launch script
cat > "$HOME/jarvis_start.sh" << 'EOF'
#!/bin/bash
cd ~/jarvis
python main.py
EOF
chmod +x "$HOME/jarvis_start.sh"
print_success "Created ~/jarvis_start.sh"

# Add alias to bashrc
if ! grep -q "alias jarvis=" "$HOME/.bashrc" 2>/dev/null; then
    echo "alias jarvis='cd ~/jarvis && python main.py'" >> "$HOME/.bashrc"
    print_success "Added 'jarvis' alias to .bashrc"
fi

# =============================================================================
# STEP 10: FINAL STATUS
# =============================================================================

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "                    INSTALLATION COMPLETE"
echo "═══════════════════════════════════════════════════════════════"
echo ""

print_info "Installation Summary:"
echo ""
echo "  JARVIS Directory:  ~/jarvis"
echo "  Models Directory:  ~/jarvis/models"
echo "  Database:          ~/jarvis/data/db/jarvis.db"
echo "  Logs:              ~/jarvis/data/logs/"
echo ""

print_info "To start JARVIS:"
echo "  Option 1: Run 'jarvis' command"
echo "  Option 2: Run '~/jarvis_start.sh'"
echo "  Option 3: cd ~/jarvis && python main.py"
echo ""

if [ "$ROOT_AVAILABLE" = true ]; then
    print_success "Root access: ENABLED (Full features available)"
else
    print_warning "Root access: DISABLED (Focus module limited)"
fi

if [ "$MODEL_CHOICE" = "1" ]; then
    print_success "AI Model: DOWNLOADED"
else
    print_warning "AI Model: NOT DOWNLOADED (Download with --setup-ai)"
fi

echo ""
print_info "Run 'jarvis --status' to check system status"
echo ""
print_success "Happy studying! 🎯"
