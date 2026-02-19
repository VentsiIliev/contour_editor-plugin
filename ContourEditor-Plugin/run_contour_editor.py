#!/usr/bin/env python3
"""
Domain-Agnostic Contour Editor Launcher
This script launches the PURE contour editor without any workpiece-specific functionality.
Use this when you need generic contour editing without workpiece concepts.
"""
import os
import sys
# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
from PyQt6.QtWidgets import QApplication
from contour_editor import (
    ContourEditorBuilder,
    BezierSegmentManager,
    SettingsConfig,
    SettingsGroup,
    ISettingsProvider
)
from contour_editor.ui.new_widgets.SegmentSettingsWidget import configure_segment_settings
class GenericSettingsProvider(ISettingsProvider):
    """Comprehensive settings provider for generic contour editing"""
    def __init__(self):
        self._default_settings = {
            # Material Settings
            "Material Type": "Type A",
            "Pressure": "100",
            "Temperature": "25.5",
            # Machine Settings
            "Speed": "50.0",
            "Feed Rate": "10.0",
            "Tool Diameter": "5.0",
            # Advanced Settings
            "Acceleration": "500.0",
            "Deceleration": "450.0",
            "Jerk": "1000.0",
            "Corner Radius": "2.5",
            # Quality Settings
            "Resolution": "0.1",
            "Tolerance": "0.05",
            "Surface Finish": "3.2",
            "Layer Height": "0.2",
            # Safety Settings
            "Max Force": "1000.0",
            "Min Clearance": "5.0",
            "Emergency Stop Distance": "10.0",
            # Process Settings
            "Dwell Time": "1.5",
            "Retract Distance": "3.0",
            "Prime Amount": "0.5",
            "Flow Rate": "100.0",
        }

    def get_all_setting_keys(self):
        return list(self._default_settings.keys())

    def get_default_values(self):
        return self._default_settings.copy()

    def get_material_type_key(self):
        return "Material Type"

    def get_available_material_types(self):
        return ["Type A", "Type B", "Type C"]

    def get_default_material_type(self):
        return "Type A"

    def get_setting_label(self, key: str):
        return key

    def get_settings_tabs_config(self):
        return [
            ("Material Settings", ["Material Type", "Pressure", "Temperature"]),
            ("Machine Settings", ["Speed", "Feed Rate", "Tool Diameter"]),
            ("Advanced Settings", ["Acceleration", "Deceleration", "Jerk", "Corner Radius"]),
            ("Quality Settings", ["Resolution", "Tolerance", "Surface Finish", "Layer Height"]),
            ("Safety Settings", ["Max Force", "Min Clearance", "Emergency Stop Distance"]),
            ("Process Settings", ["Dwell Time", "Retract Distance", "Prime Amount", "Flow Rate"]),
        ]
def main():
    print("=" * 60)
    print("LAUNCHING DOMAIN-AGNOSTIC CONTOUR EDITOR")
    print("=" * 60)
    print("This is the PURE contour editor without workpiece functionality.")
    print("Use this for generic contour editing tasks.")
    print("=" * 60 + "\n")
    app = QApplication(sys.argv)

    # Configure comprehensive settings with 6 groups and 21 parameters
    config = SettingsConfig(
        default_settings={
            # Material Settings
            "Material Type": "Type A",
            "Pressure": "100",
            "Temperature": "25.5",
            # Machine Settings
            "Speed": "50.0",
            "Feed Rate": "10.0",
            "Tool Diameter": "5.0",
            # Advanced Settings
            "Acceleration": "500.0",
            "Deceleration": "450.0",
            "Jerk": "1000.0",
            "Corner Radius": "2.5",
            # Quality Settings
            "Resolution": "0.1",
            "Tolerance": "0.05",
            "Surface Finish": "3.2",
            "Layer Height": "0.2",
            # Safety Settings
            "Max Force": "1000.0",
            "Min Clearance": "5.0",
            "Emergency Stop Distance": "10.0",
            # Process Settings
            "Dwell Time": "1.5",
            "Retract Distance": "3.0",
            "Prime Amount": "0.5",
            "Flow Rate": "100.0",
        },
        groups=[
            SettingsGroup("Material Settings", ["Material Type", "Pressure", "Temperature"]),
            SettingsGroup("Machine Settings", ["Speed", "Feed Rate", "Tool Diameter"]),
            SettingsGroup("Advanced Settings", ["Acceleration", "Deceleration", "Jerk", "Corner Radius"]),
            SettingsGroup("Quality Settings", ["Resolution", "Tolerance", "Surface Finish", "Layer Height"]),
            SettingsGroup("Safety Settings", ["Max Force", "Min Clearance", "Emergency Stop Distance"]),
            SettingsGroup("Process Settings", ["Dwell Time", "Retract Distance", "Prime Amount", "Flow Rate"]),
        ],
        combo_field_key="Material Type"
    )

    # IMPORTANT: Configure segment settings BEFORE building the editor
    print("⚙️  Configuring segment settings...")
    configure_segment_settings(config)

    provider = GenericSettingsProvider()

    # Build PURE generic editor (no forms, no workpiece concepts)
    print("🔨 Building pure contour editor...")
    editor = (ContourEditorBuilder()
              .with_segment_manager(BezierSegmentManager)
              .with_settings(config, provider)
              .build())
    editor.show()
    editor.setWindowTitle("Contour Editor - Pure Generic Mode")
    print("\n✅ Pure Contour Editor launched successfully")
    print("   ✓ Domain-agnostic")
    print("   ✓ No workpiece concepts")
    print("   ✓ No forms")
    print("   ✓ Pure contour editing")
    print("   ✓ 6 settings tabs with 21 parameters configured\n")
    print("💡 Settings tabs available:")
    print("   - Material Settings (3 fields)")
    print("   - Machine Settings (3 fields)")
    print("   - Advanced Settings (4 fields)")
    print("   - Quality Settings (4 fields)")
    print("   - Safety Settings (3 fields)")
    print("   - Process Settings (4 fields)\n")
    print("💡 For workpiece-specific features (forms, etc),")
    print("   use run_workpiece_editor.py instead.\n")
    sys.exit(app.exec())
if __name__ == '__main__':
    main()
