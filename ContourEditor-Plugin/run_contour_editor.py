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
class GenericSettingsProvider(ISettingsProvider):
    """Simple settings provider for generic contour editing"""
    def __init__(self):
        self._default_settings = {
            "speed": "100",
            "power": "50",
            "passes": "1"
        }
    def get_all_setting_keys(self):
        return list(self._default_settings.keys())
    def get_default_values(self):
        return self._default_settings.copy()
    def get_material_type_key(self):
        return ""
    def get_available_material_types(self):
        return []
    def get_default_material_type(self):
        return ""
    def get_setting_label(self, key: str):
        return key.replace('_', ' ').title()
    def get_settings_tabs_config(self):
        return [("Settings", list(self._default_settings.keys()))]
def main():
    print("=" * 60)
    print("LAUNCHING DOMAIN-AGNOSTIC CONTOUR EDITOR")
    print("=" * 60)
    print("This is the PURE contour editor without workpiece functionality.")
    print("Use this for generic contour editing tasks.")
    print("=" * 60 + "\n")
    app = QApplication(sys.argv)
    # Configure settings
    config = SettingsConfig(
        default_settings={
            "speed": "100",
            "power": "50",
            "passes": "1"
        },
        groups=[
            SettingsGroup("Basic Settings", ["speed", "power", "passes"])
        ]
    )
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
    print("   ✓ Pure contour editing\n")
    print("💡 For workpiece-specific features (forms, etc),")
    print("   use run_workpiece_editor.py instead.\n")
    sys.exit(app.exec())
if __name__ == '__main__':
    main()
