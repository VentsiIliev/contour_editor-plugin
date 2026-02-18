# Contour Editor Plugin - Build Instructions

## ✅ Clean Structure - No Duplicates!

All package files are in the **ROOT** directory (standard Python layout):

```
ContourEditor-Plugin/
├── pyproject.toml          # Package configuration
├── setup.py                # Setup script
├── MANIFEST.in             # File inclusion rules
├── LICENSE                 # MIT License
├── BUILD_WHEEL.sh          # Build script
├── test_package.py         # Verification script
├── src/                    # Source code
│   ├── contour_editor/
│   └── workpiece_editor/
├── tests/                  # Test suite
└── package-dist/           # Documentation only
    ├── WHEEL_BUILDING.md
    └── DEBIAN_BUILD_FIX.md
```

## Building the Wheel

Simply run from the root:

```bash
cd /home/ilv/contour_editor-plugin/ContourEditor-Plugin
python3 -m build
```

**Result:**
```
dist/
├── contour_editor_plugin-1.0.0-py3-none-any.whl  ✅
└── contour-editor-plugin-1.0.0.tar.gz            ✅
```

## Installation

```bash
# Install from wheel
pip install dist/contour_editor_plugin-1.0.0-py3-none-any.whl --user

# Or in a virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install dist/contour_editor_plugin-1.0.0-py3-none-any.whl
```

## Testing

```bash
# Test imports
PYTHONPATH=src python3 test_package.py

# Run test suite
pytest tests/
```

## Updating Version

1. Edit `pyproject.toml` - change version number
2. Edit `src/contour_editor/_version.py`
3. Edit `src/workpiece_editor/_version.py`
4. Build: `python3 -m build`

## Installation in Other Projects

### From Local Wheel
```bash
pip install /path/to/dist/contour_editor_plugin-1.0.0-py3-none-any.whl
```

### From SVN (after committing)
```bash
pip install svn+https://your-svn-server/svn/contour-editor-plugin/trunk
```

### In requirements.txt
```
# Add this line
svn+https://your-svn-server/svn/contour-editor-plugin/trunk
```

## Usage

```python
from contour_editor import build_contour_editor, BezierSegmentManager
from workpiece_editor import build_workpiece_editor

# Create editors
editor = build_contour_editor(parent=widget, segment_manager=BezierSegmentManager)
workpiece_editor = build_workpiece_editor()

# Check version
import contour_editor
print(f"Version: {contour_editor.__version__}")  # 1.0.0
```

## SVN Commit

```bash
svn add pyproject.toml setup.py MANIFEST.in LICENSE BUILD_WHEEL.sh
svn commit -m "Add package configuration v1.0.0"
```

## Documentation

- `package-dist/WHEEL_BUILDING.md` - Detailed wheel building guide
- `package-dist/DEBIAN_BUILD_FIX.md` - Debian/Ubuntu specific fixes
- `FIXED_README.md` - Recent fixes applied

---

**Status:** ✅ Clean, standard Python project layout with no duplicate files!

