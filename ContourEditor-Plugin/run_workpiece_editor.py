#!/usr/bin/env python3
"""
Workpiece Editor Launcher
This script launches the workpiece editor with workpiece-specific functionality.
Includes forms, workpiece adapters, and domain-specific features.
"""
import os
import sys
from enum import Enum

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from PyQt6.QtWidgets import QApplication
from workpiece_editor import WorkpieceEditorBuilder
from workpiece_editor.handlers import SaveWorkpieceHandler
from contour_editor import BezierSegmentManager, SettingsConfig, SettingsGroup, ISettingsProvider
from workpiece_editor.ui.CreateWorkpieceForm import CreateWorkpieceForm, FormFieldConfig, GenericFormConfig


def get_icon_path(icon_name):
    base_path = os.path.join(os.path.dirname(__file__), 'src', 'workpiece_editor', 'assets', 'icons')
    icon_file = f"{icon_name}.png"
    full_path = os.path.join(base_path, icon_file)
    return full_path if os.path.exists(full_path) else ""


def get_contour_icon_path(icon_name):
    base_path = os.path.join(os.path.dirname(__file__), 'src', 'contour_editor', 'assets', 'icons')
    icon_file = f"{icon_name}.png"
    full_path = os.path.join(base_path, icon_file)
    return full_path if os.path.exists(full_path) else ""


def create_workpiece_form_config(glue_types=None) -> GenericFormConfig:
    if glue_types is None:
        glue_types = ["Type A", "Type B", "Type C"]

    fields = [
        FormFieldConfig(
            field_id="workpieceId",
            field_type="text",
            label="Workpiece ID",
            icon_path=get_icon_path("WOPIECE_ID_ICON_2"),
            placeholder="",
            mandatory=True,
            visible=True
        ),
        FormFieldConfig(
            field_id="name",
            field_type="text",
            label="Name",
            icon_path=get_icon_path("WORKPIECE_NAME_ICON"),
            placeholder="",
            mandatory=False,
            visible=True
        ),
        FormFieldConfig(
            field_id="description",
            field_type="text",
            label="Description",
            icon_path=get_icon_path("DESCRIPTION_WORKPIECE_BUTTON_SQUARE"),
            placeholder="",
            mandatory=False,
            visible=True
        ),
        FormFieldConfig(
            field_id="height",
            field_type="text",
            label="Height",
            icon_path=get_contour_icon_path("RULER_ICON"),
            placeholder="",
            mandatory=True,
            visible=True
        ),
        FormFieldConfig(
            field_id="glue_qty",
            field_type="text",
            label="Glue Quantity",
            icon_path=get_icon_path("glue_qty"),
            placeholder="g /m²",
            mandatory=False,
            visible=True
        ),
        FormFieldConfig(
            field_id="gripper_id",
            field_type="dropdown",
            label="Gripper",
            icon_path=get_icon_path("GRIPPER_ID_ICON"),
            options=["Gripper1", "Gripper2", "Gripper3"],
            mandatory=False,
            visible=True
        ),
        FormFieldConfig(
            field_id="glue_type",
            field_type="dropdown",
            label="Glue Type",
            icon_path=get_icon_path("GLUE_TYPE_ICON"),
            options=glue_types,
            mandatory=True,
            visible=True
        ),
    ]

    return GenericFormConfig(
        form_title="Create Workpiece",
        fields=fields,
        accept_button_icon="",
        cancel_button_icon="",
        config_file="settings/workpiece_form_config.json"
    )


class WorkpieceSettingsProvider(ISettingsProvider):
    """Settings provider for workpiece editing"""

    def __init__(self):
        self._default_settings = {
            "Setting 1": "100",
            "Setting 2": "50",
            "Setting 3": "1",
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


class WorkpieceFormFactory:

    def create_form(self, parent=None):
        print("🏭 Creating workpiece form...")

        glue_types = ["Type A", "Type B", "Type C"]
        try:
            from modules.shared.tools.glue_monitor_system.core.cell_manager import GlueCellsManagerSingleton
            cells_manager = GlueCellsManagerSingleton.get_instance()
            glue_types = [cell.glueType for cell in cells_manager.cells]
            if glue_types:
                print(f"   ✅ Loaded {len(glue_types)} glue types from cell configuration")
        except Exception as e:
            print(f"   ⚠️  Using default glue types (could not load from cells: {e})")

        form_config = create_workpiece_form_config(glue_types)

        form = CreateWorkpieceForm(
            parent=parent,
            form_config=form_config,
            showButtons=False
        )
        form.setFixedWidth(400)
        print("✅ Workpiece form created")
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
