#!/usr/bin/env python3
"""
Workpiece-Aware Contour Editor Launcher
This script launches the workpiece-aware contour editor with full workpiece functionality.
Use this when you need workpiece concepts like main contour, spray patterns, etc.
"""
import os
import sys
# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
from PyQt6.QtWidgets import QApplication
from workpiece_editor import (
    WorkpieceEditorBuilder,
    BezierSegmentManager,
    SettingsConfig,
    SettingsGroup,
    ISettingsProvider,
    WorkpieceAdapter,
    GenericWorkpiece
)
class WorkpieceSettingsProvider(ISettingsProvider):
    """Settings provider with material types for workpiece editing"""
    def __init__(self):
        self._default_settings = {
            "speed": "100",
            "power": "50",
            "temperature": "25",
            "material_type": "Steel"
        }
        self._materials = ["Steel", "Aluminum", "Plastic", "Wood"]
    def get_all_setting_keys(self):
        return list(self._default_settings.keys())
    def get_default_values(self):
        return self._default_settings.copy()
    def get_material_type_key(self):
        return "material_type"
    def get_available_material_types(self):
        return self._materials
    def get_default_material_type(self):
        return self._materials[0]
    def get_setting_label(self, key: str):
        return key.replace('_', ' ').title()
    def get_settings_tabs_config(self):
        return [
            ("Motion", ["speed", "power"]),
            ("Advanced", ["temperature", "material_type"])
        ]
def on_save_workpiece(form_data):
    """Handle workpiece save"""
    print("\n💾 Save workpiece requested")
    print(f"   Form data keys: {list(form_data.keys())}")
    # In real application, save to database or file
    print("   ✅ Workpiece saved (demo mode)\n")
def on_capture():
    """Handle capture request"""
    print("\n📸 Capture requested")
    print("   In real application, would capture from camera")
    print("   ✅ Capture completed (demo mode)\n")
def on_execute(workpiece):
    """Handle workpiece execution"""
    print("\n▶️ Execute workpiece requested")
    print(f"   Workpiece: {workpiece}")
    print("   In real application, would send to robot controller")
    print("   ✅ Execution started (demo mode)\n")
def on_update_camera_feed():
    """Handle camera feed update"""
    print("📹 Camera feed update requested")
def main():
    print("=" * 60)
    print("LAUNCHING WORKPIECE-AWARE CONTOUR EDITOR")
    print("=" * 60)
    print("This editor includes workpiece-specific functionality:")
    print("  - Workpiece adapter for data transformation")
    print("  - Workpiece manager for loading/saving")
    print("  - Layer-based organization (Workpiece/Contour/Fill)")
    print("  - Spray pattern support")
    print("=" * 60 + "\n")
    app = QApplication(sys.argv)
    # Configure settings
    config = SettingsConfig(
        default_settings={
            "speed": "100",
            "power": "50",
            "temperature": "25",
            "material_type": "Steel"
        },
        groups=[
            SettingsGroup("Motion", ["speed", "power"]),
            SettingsGroup("Advanced", ["temperature", "material_type"])
        ],
        combo_field_key="material_type"
    )
    provider = WorkpieceSettingsProvider()
    # Build workpiece-aware editor
    editor = (WorkpieceEditorBuilder()
              .with_segment_manager(BezierSegmentManager)
              .with_settings(config, provider)
              .on_save(on_save_workpiece)
              .on_capture(on_capture)
              .on_execute(on_execute)
              .on_update_camera_feed(on_update_camera_feed)
              .build())
    editor.show()
    editor.setWindowTitle("Contour Editor - Workpiece Mode")
    print("\n✅ Workpiece Editor launched successfully")
    print("   - Full workpiece support")
    print("   - WorkpieceAdapter for data transformation")
    print("   - WorkpieceManager integrated")
    print("   - Layer organization: Workpiece/Contour/Fill")
    print("\nTip: Use the toolbar to:")
    print("   - Capture workpiece contours")
    print("   - Edit spray patterns")
    print("   - Save workpiece data")
    print("   - Execute workpiece\n")
    sys.exit(app.exec())
if __name__ == '__main__':
    main()
