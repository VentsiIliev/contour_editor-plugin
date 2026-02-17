#!/usr/bin/env python3
"""
Workpiece Editor Launcher
This script launches the workpiece editor with workpiece-specific functionality.
Includes forms, workpiece adapters, and domain-specific features.
"""
import os
import sys

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton
from workpiece_editor import WorkpieceEditorBuilder
from workpiece_editor.handlers import SaveWorkpieceHandler
from contour_editor import BezierSegmentManager, SettingsConfig, SettingsGroup, ISettingsProvider


class WorkpieceSettingsProvider(ISettingsProvider):
    """Settings provider for workpiece editing"""

    def __init__(self):
        self._default_settings = {
            "speed": "100",
            "power": "50",
            "passes": "1",
            "glue_type": "Type A"
        }

    def get_all_setting_keys(self):
        return list(self._default_settings.keys())

    def get_default_values(self):
        return self._default_settings.copy()

    def get_material_type_key(self):
        return "glue_type"

    def get_available_material_types(self):
        return ["Type A", "Type B", "Type C"]

    def get_default_material_type(self):
        return "Type A"

    def get_setting_label(self, key: str):
        return key.replace('_', ' ').title()

    def get_settings_tabs_config(self):
        return [("Settings", list(self._default_settings.keys()))]


class TestWorkpieceForm(QWidget):
    """Test form for workpiece data"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.onSubmitCallBack = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        # Workpiece Name
        layout.addWidget(QLabel("Workpiece Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter workpiece name...")
        layout.addWidget(self.name_input)
        # Workpiece ID
        layout.addWidget(QLabel("Workpiece ID:"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter ID...")
        layout.addWidget(self.id_input)
        # Description
        layout.addWidget(QLabel("Description:"))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Enter description...")
        layout.addWidget(self.description_input)
        # Material
        layout.addWidget(QLabel("Material:"))
        self.material_input = QLineEdit()
        self.material_input.setPlaceholderText("Enter material type...")
        layout.addWidget(self.material_input)
        # Submit button
        self.submit_btn = QPushButton("Save Workpiece Data")
        self.submit_btn.clicked.connect(self.on_submit_clicked)
        layout.addWidget(self.submit_btn)
        layout.addStretch()

    def get_data(self):
        """Get form data as dictionary"""
        return {
            "name": self.name_input.text(),
            "workpieceId": self.id_input.text(),
            "description": self.description_input.text(),
            "material": self.material_input.text()
        }

    def on_submit_clicked(self):
        """Handle submit button click"""
        data = self.get_data()
        print(f"\n📋 Workpiece Data Submitted:")
        for key, value in data.items():
            print(f"   {key}: {value}")
        print()
        if self.onSubmitCallBack:
            result = self.onSubmitCallBack(data)
            print(f"   Callback result: {result}")

    def onSubmit(self):
        """Called when form should be submitted"""
        data = self.get_data()
        print(f"📝 onSubmit called with data: {data}")
        return True

    def validate(self):
        """Validate form data"""
        data = self.get_data()
        if not data["name"]:
            return False, "Workpiece name is required"
        if not data["workpieceId"]:
            return False, "Workpiece ID is required"
        return True, ""

    def clear(self):
        """Clear form fields"""
        self.name_input.clear()
        self.id_input.clear()
        self.description_input.clear()
        self.material_input.clear()
        print("🧹 Workpiece form cleared")

    def prefill_form(self, data):
        """Prefill form with data"""
        if isinstance(data, dict):
            self.name_input.setText(data.get("name", ""))
            self.id_input.setText(data.get("workpieceId", ""))
            self.description_input.setText(data.get("description", ""))
            self.material_input.setText(data.get("material", ""))
            print(f"📥 Workpiece form prefilled with: {data}")


class WorkpieceFormFactory:
    """Factory for creating workpiece forms"""

    def create_form(self, parent=None):
        print("🏭 Creating workpiece form instance...")
        form = TestWorkpieceForm(parent)
        form.setFixedWidth(400)
        return form


def main():
    print("=" * 60)
    print("LAUNCHING WORKPIECE EDITOR WITH TEST FORM")
    print("=" * 60)
    print("This is the workpiece editor with domain-specific functionality.")
    print("Includes workpiece forms, adapters, and handlers.")
    print("=" * 60 + "\n")
    app = QApplication(sys.argv)
    # Configure settings
    config = SettingsConfig(
        default_settings={
            "speed": "100",
            "power": "50",
            "passes": "1",
            "glue_type": "Type A"
        },
        groups=[
            SettingsGroup("Workpiece Settings", ["speed", "power", "passes", "glue_type"])
        ]
    )
    provider = WorkpieceSettingsProvider()
    # Create workpiece form factory
    print("📝 Creating workpiece form factory...")
    form_factory = WorkpieceFormFactory()
    # Build workpiece editor with form first (so we can access it in callback)
    print("🔨 Building workpiece editor...")
    editor = (WorkpieceEditorBuilder()
              .with_segment_manager(BezierSegmentManager)
              .with_settings(config, provider)
              .with_form(form_factory)
              .build())

    # Define save callback (receives complete package with form + editor data)
    def on_save_callback(data_package):
        """Handle save button press - receives a complete data package from the editor"""
        print("\n" + "=" * 70)
        print("💾 SAVE CALLBACK TRIGGERED")
        print("=" * 70)

        # Extract form_data and editor_data from the package
        form_data = data_package.get('form_data', {})
        editor_data = data_package.get('editor_data')

        # Print form data
        print("\n📋 FORM DATA:")
        for key, value in form_data.items():
            print(f"   {key}: {value}")

        # Print detailed editor data
        if editor_data:
            stats = editor_data.get_statistics()
            print(f"\n📊 EDITOR DATA STATISTICS:")
            print(f"   Total layers: {stats['total_layers']}")
            print(f"   Total segments: {stats['total_segments']}")
            print(f"   Total points: {stats['total_points']}")

            print(f"\n🗂️  DETAILED LAYER BREAKDOWN:")
            for layer_name, layer_info in stats['layers'].items():
                print(f"\n   Layer: '{layer_name}'")
                print(f"      Segments: {layer_info['segments']}")
                print(f"      Points: {layer_info['points']}")
                print(f"      Locked: {layer_info['locked']}")
                print(f"      Visible: {layer_info['visible']}")

                # Get the actual layer to show segment details
                layer = editor_data.get_layer(layer_name)
                if layer:
                    for idx, segment in enumerate(layer.segments):
                        print(f"\n      Segment #{idx}:")
                        print(f"         Points: {len(segment.points)}")
                        if len(segment.points) > 0:
                            print(f"         First point: ({segment.points[0].x():.2f}, {segment.points[0].y():.2f})")
                            print(f"         Last point: ({segment.points[-1].x():.2f}, {segment.points[-1].y():.2f})")
                        print(f"         Settings: {segment.settings}")
                        print(f"         Visible: {segment.visible}")

        # Convert editor_data to workpiece format using WorkpieceAdapter
        try:
            from workpiece_editor.adapters import WorkpieceAdapter

            # Convert ContourEditorData to workpiece data format
            workpiece_data = WorkpieceAdapter.to_workpiece_data(editor_data)

            # Merge form data with workpiece data
            complete_data = {**form_data, **workpiece_data}

            print("\n📦 COMPLETE DATA PACKAGE:")
            print(f"   Form fields: {list(form_data.keys())}")

            if complete_data.get('main_contour') is not None:
                main_contour = complete_data['main_contour']
                print(f"   Main contour: {len(main_contour)} points, shape: {main_contour.shape}")

            if complete_data.get('main_settings'):
                print(f"   Main settings: {complete_data['main_settings']}")

            if complete_data.get('spray_pattern'):
                contours = complete_data['spray_pattern'].get('Contour', [])
                fills = complete_data['spray_pattern'].get('Fill', [])
                print(f"   Spray pattern contours: {len(contours)}")
                print(f"   Spray pattern fills: {len(fills)}")

                for idx, contour_data in enumerate(contours):
                    contour_array = contour_data['contour']
                    settings = contour_data['settings']
                    print(f"      Contour #{idx}: {len(contour_array)} points, settings: {settings}")

                for idx, fill_data in enumerate(fills):
                    fill_array = fill_data['contour']
                    settings = fill_data['settings']
                    print(f"      Fill #{idx}: {len(fill_array)} points, settings: {settings}")

            # Here you would typically save to database or file
            print("\n✅ READY TO SAVE (implement your storage here)")
            print(f"💡 Complete data keys: {list(complete_data.keys())}")
            print("=" * 70 + "\n")

            return True, "Workpiece data prepared successfully!"

        except Exception as e:
            print(f"\n❌ ERROR PREPARING DATA: {e}")
            import traceback
            traceback.print_exc()
            print("=" * 70 + "\n")
            return False, f"Error: {str(e)}"

    # Connect to the MainApplicationFrame's save_requested signal
    # This is emitted when the form is submitted with COMPLETE package (form + editor data)
    editor.save_requested.connect(on_save_callback)
    print("✅ Save callback connected to save_requested signal")
    editor.show()
    editor.setWindowTitle("Workpiece Editor - with Test Form")
    print("\n✅ Workpiece Editor launched successfully")
    print("   ✓ Workpiece-specific functionality")
    print("   ✓ Workpiece forms enabled")
    print("   ✓ Built on top of contour_editor")
    print("   ✓ Domain-specific features\n")
    print("💡 TIP: The workpiece form allows you to enter metadata")
    print("   specific to workpieces (name, ID, material, etc).")
    print("   Look for the form in the editor's workpiece data section.\n")
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
