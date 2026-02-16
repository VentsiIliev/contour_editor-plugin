#!/usr/bin/env python3
"""
Automated migration script for ContourEditor package restructuring.
Performs Phase 1: Create new structure with backward compatibility.
"""
import os
import shutil
from pathlib import Path
# Base directory
BASE_DIR = Path(__file__).parent / "src" / "contour_editor"
# Migration map: (source, destination)
MIGRATIONS = [
    # Config files
    ("constants.py", "config/constants.py"),
    ("ConstantsManager.py", "config/constants_manager.py"),
    ("contour_editor_settings.json", "config/contour_editor_settings.json"),
    ("global_segment_settings.json", "config/global_segment_settings.json"),
    # Core editor components
    ("contourEditorDecorators/ContourEditor.py", "core/editor.py"),
    ("contourEditorDecorators/ContourEditorWithRulers.py", "core/editor_with_rulers.py"),
    ("contourEditorDecorators/ContourEditorWithBottomToolBar.py", "core/editor_with_toolbar.py"),
    ("ContourEditor.py", "core/main_frame.py"),
    ("Ruler.py", "core/ruler.py"),
    # Data models
    ("EditorDataModel.py", "data/editor_data_model.py"),
    ("segment_provider.py", "data/segment_provider.py"),
    ("settings_provider_registry.py", "data/settings_provider_registry.py"),
    # State machine
    ("EditorStateMachine/EditorStateMachine.py", "state/state_machine.py"),
    ("EditorStateMachine/State.py", "state/state.py"),
    ("EditorStateMachine/modes.py", "state/modes.py"),
    ("EditorStateMachine/Modes/BaseMode.py", "state/mode_handlers/base_mode.py"),
    ("EditorStateMachine/Modes/MultiPointSelectMode.py", "state/mode_handlers/multi_select_mode.py"),
    ("EditorStateMachine/Modes/PanMode.py", "state/mode_handlers/pan_mode.py"),
    ("EditorStateMachine/Modes/PointDragMode.py", "state/mode_handlers/point_drag_mode.py"),
    ("EditorStateMachine/Modes/RectangleSelectMode.py", "state/mode_handlers/rectangle_select_mode.py"),
    ("EditorStateMachine/Modes/RulerMode.py", "state/mode_handlers/ruler_mode.py"),
    # Tests/examples
    ("test.py", "tests/examples/radial_menu_demo.py"),
    ("mockWorkpieceData.py", "tests/examples/mock_workpiece.py"),
    # Assets (rename icons to assets)
    ("icons", "assets/icons"),
    ("dxf", "assets/dxf"),
]
# Import replacements for new files
IMPORT_REPLACEMENTS = {
    "from .. import constants": "from ..config import constants",
    "from ..constants import": "from ..config.constants import",
    "from . import constants": "from .config import constants",
    "from .constants import": "from .config.constants import",
    "from ..ConstantsManager import": "from ..config.constants_manager import",
    "from .ConstantsManager import": "from .config.constants_manager import",
    "from ..EditorDataModel import": "from ..data.editor_data_model import",
    "from .EditorDataModel import": "from .data.editor_data_model import",
    "from ..segment_provider import": "from ..data.segment_provider import",
    "from .segment_provider import": "from .data.segment_provider import",
    "from ..settings_provider_registry import": "from ..data.settings_provider_registry import",
    "from .settings_provider_registry import": "from .data.settings_provider_registry import",
    "from ..contourEditorDecorators.ContourEditor import": "from ..core.editor import",
    "from .contourEditorDecorators.ContourEditor import": "from .core.editor import",
    "from ..contourEditorDecorators.ContourEditorWithRulers import": "from ..core.editor_with_rulers import",
    "from .contourEditorDecorators.ContourEditorWithRulers import": "from .core.editor_with_rulers import",
    "from ..contourEditorDecorators.ContourEditorWithBottomToolBar import": "from ..core.editor_with_toolbar import",
    "from .contourEditorDecorators.ContourEditorWithBottomToolBar import": "from .core.editor_with_toolbar import",
    "from ..Ruler import": "from ..core.ruler import",
    "from .Ruler import": "from .core.ruler import",
    "from ..EditorStateMachine.EditorStateMachine import": "from ..state.state_machine import",
    "from ..EditorStateMachine.Modes.": "from ..state.mode_handlers.",
}
def create_directory_structure():
    """Create new directory structure"""
    dirs = [
        "config",
        "core",
        "data",
        "state",
        "state/mode_handlers",
        "assets",
        "assets/icons",
        "assets/dxf",
        "tests",
        "tests/examples",
    ]
    for dir_name in dirs:
        dir_path = BASE_DIR / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        # Create __init__.py if it doesn't exist
        init_file = dir_path / "__init__.py"
        if not init_file.exists() and dir_name not in ["assets", "assets/icons", "assets/dxf"]:
            init_file.write_text("")
            print(f"✓ Created {init_file.relative_to(BASE_DIR.parent)}")
def copy_and_update_file(source, dest):
    """Copy file and update imports"""
    source_path = BASE_DIR / source
    dest_path = BASE_DIR / dest
    if not source_path.exists():
        print(f"⚠ Source not found: {source}")
        return False
    # Read source content
    if source_path.is_file():
        content = source_path.read_text()
        # Update imports
        for old_import, new_import in IMPORT_REPLACEMENTS.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
        # Write to destination
        dest_path.write_text(content)
        print(f"✓ Copied and updated: {source} → {dest}")
    else:
        # It's a directory
        if dest_path.exists():
            shutil.rmtree(dest_path)
        shutil.copytree(source_path, dest_path)
        print(f"✓ Copied directory: {source} → {dest}")
    return True
def create_compatibility_shim(original, new_location):
    """Create a compatibility shim at the original location"""
    source_path = BASE_DIR / original
    # Don't create shim for directories or JSON files
    if not original.endswith('.py'):
        return
    # Determine the import path for the new location
    new_import_path = new_location.replace('/', '.').replace('.py', '')
    module_name = original.replace('.py', '').split('/')[-1]
    shim_content = f'''"""
Compatibility shim for backward compatibility.
This module has been moved to contour_editor.{new_import_path}
"""
import warnings
warnings.warn(
    "Importing from contour_editor.{original.replace('.py', '')} is deprecated. "
    "Use contour_editor.{new_import_path} instead.",
    DeprecationWarning,
    stacklevel=2
)
from .{new_import_path} import *
'''
    source_path.write_text(shim_content)
    print(f"✓ Created compatibility shim: {original}")
def main():
    print("=" * 70)
    print("ContourEditor Package Restructuring - Phase 1")
    print("=" * 70)
    print()
    print("Step 1: Creating new directory structure...")
    create_directory_structure()
    print()
    print("Step 2: Copying and updating files...")
    for source, dest in MIGRATIONS:
        copy_and_update_file(source, dest)
    print()
    print("Step 3: Creating compatibility shims...")
    for source, dest in MIGRATIONS:
        if source.endswith('.py') and not source.startswith('EditorStateMachine/'):
            create_compatibility_shim(source, dest)
    print()
    print("=" * 70)
    print("✅ Phase 1 migration complete!")
    print()
    print("Next steps:")
    print("1. Test that imports still work")
    print("2. Run your application to verify functionality")
    print("3. When ready, run Phase 2 to update public API")
    print("=" * 70)
if __name__ == "__main__":
    main()
