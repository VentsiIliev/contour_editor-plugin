#!/bin/bash
# BUILD_WHEEL.sh
# Builds wheel and source distribution for the package

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=================================================="
echo "🔨 Building Contour Editor Plugin Package"
echo "=================================================="
echo ""

# Check if we're in package-dist or project root
if [[ -f "$SCRIPT_DIR/pyproject.toml" ]] && [[ ! -d "$SCRIPT_DIR/src" ]]; then
    echo "📋 Deploying package files from package-dist/ to project root..."
    echo ""

    # Run deploy script
    if [[ -f "$SCRIPT_DIR/deploy_package_files.sh" ]]; then
        bash "$SCRIPT_DIR/deploy_package_files.sh"
        echo ""
    else
        echo "❌ Error: deploy_package_files.sh not found"
        exit 1
    fi

    # Now change to project root for building
    cd "$PROJECT_ROOT"
elif [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Error: pyproject.toml not found"
    exit 1
fi

# Check if build module is installed
echo "📦 Checking build tools..."
if ! python3 -c "import build" 2>/dev/null; then
    echo "   ⚠️  'build' module not found"
    echo ""
    echo "   Please install it using ONE of these methods:"
    echo ""
    echo "   1. System package (recommended):"
    echo "      sudo apt install python3-build"
    echo ""
    echo "   2. Using pip with --break-system-packages:"
    echo "      pip install build --break-system-packages"
    echo ""
    echo "   3. Or run python3 -m build directly (if already installed):"
    echo "      python3 -m build"
    echo ""
    exit 1
fi

# Clean previous builds
if [[ -d "dist" ]]; then
    echo "🧹 Cleaning previous builds..."
    rm -rf dist/
fi

if [[ -d "build" ]]; then
    rm -rf build/
fi

if [[ -d "*.egg-info" ]]; then
    rm -rf *.egg-info
fi

echo ""
echo "🔨 Building wheel and source distribution..."
echo ""

# Build the package
python3 -m build

echo ""
echo "=================================================="
echo "✅ Build Complete!"
echo "=================================================="
echo ""

# Show what was built
if [[ -d "dist" ]]; then
    echo "📦 Built packages in dist/:"
    ls -lh dist/
    echo ""

    # Show file details
    for file in dist/*; do
        if [[ -f "$file" ]]; then
            filename=$(basename "$file")
            size=$(ls -lh "$file" | awk '{print $5}')
            echo "   ✓ $filename ($size)"
        fi
    done

    echo ""
    echo "🚀 Installation options:"
    echo ""
    echo "   Local install:"
    echo "   pip install dist/contour_editor_plugin-1.0.0-py3-none-any.whl"
    echo ""
    echo "   Or from source:"
    echo "   pip install dist/contour-editor-plugin-1.0.0.tar.gz"
    echo ""
    echo "   Upgrade existing:"
    echo "   pip install --upgrade dist/contour_editor_plugin-1.0.0-py3-none-any.whl"
    echo ""
else
    echo "❌ Error: dist/ directory not created"
    exit 1
fi

echo "=================================================="

