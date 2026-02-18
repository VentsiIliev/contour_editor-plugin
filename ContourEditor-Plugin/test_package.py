#!/usr/bin/env python3
"""
Test script to verify the package installation and imports
"""
import sys

print("=" * 70)
print("Testing Contour Editor Plugin Package")
print("=" * 70)
print()

# Test 1: Import contour_editor
print("✓ Test 1: Import contour_editor...")
try:
    import contour_editor
    print(f"  SUCCESS - Version: {contour_editor.__version__}")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# Test 2: Import workpiece_editor
print("✓ Test 2: Import workpiece_editor...")
try:
    import workpiece_editor
    print(f"  SUCCESS - Version: {workpiece_editor.__version__}")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# Test 3: Import key contour_editor components
print("✓ Test 3: Import contour_editor components...")
try:
    from contour_editor import (
        MainApplicationFrame,
        ContourEditorBuilder,
        BezierSegmentManager,
        ContourEditorData,
        Segment,
        Layer
    )
    print("  SUCCESS - All key components imported")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# Test 4: Import key workpiece_editor components
print("✓ Test 4: Import workpiece_editor components...")
try:
    from workpiece_editor import (
        WorkpieceEditorBuilder,
        WorkpieceAdapter,
        WorkpieceManager,
        build_workpiece_editor
    )
    print("  SUCCESS - All key components imported")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# Test 5: Import handlers
print("✓ Test 5: Import workpiece handlers...")
try:
    from workpiece_editor.handlers import (
        StartHandler,
        CaptureHandler,
        SaveWorkpieceHandler,
        CaptureDataHandler
    )
    print("  SUCCESS - All handlers imported")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# Test 6: Import config components
print("✓ Test 6: Import config components...")
try:
    from workpiece_editor.config import (
        SegmentSettingsProvider,
        WorkpieceFormFactory,
        create_workpiece_form_config
    )
    print("  SUCCESS - All config components imported")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# Test 7: Import models
print("✓ Test 7: Import workpiece models...")
try:
    from workpiece_editor.models import (
        BaseWorkpiece,
        GenericWorkpiece,
        WorkpieceFactory,
        WorkpieceField,
        WorkpieceFieldProvider
    )
    print("  SUCCESS - All models imported")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print()
print("Package is ready to use!")
print()
print("Quick Start:")
print("  from contour_editor import build_contour_editor")
print("  from workpiece_editor import build_workpiece_editor")
print()

