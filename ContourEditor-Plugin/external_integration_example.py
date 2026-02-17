import os
import sys

from PyQt6.QtWidgets import QApplication

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Use WorkpieceEditorBuilder from workpiece_editor package
from workpiece_editor import (
    WorkpieceEditorBuilder,
    BezierSegmentManager,
    SettingsConfig,
    SettingsGroup,
    ISettingsProvider,
    CaptureDataHandler,
    ContourEditorData,
    WorkpieceAdapter
)


class ContourEditorIntegration:
    """
    Example integration using the WorkpieceEditorBuilder.
    The builder provides a clean, fluent API for configuring the editor
    with workpiece-specific functionality.
    """

    def __init__(self, parent=None, controller=None):
        self.controller = controller

        # Build editor using workpiece-aware fluent API
        self.editor = (WorkpieceEditorBuilder()
                       .with_parent(parent)
                       .with_segment_manager(BezierSegmentManager)
                       .with_settings(*self._create_settings_config())
                       .with_form(self._create_form_factory())
                       .on_save(self.on_save_workpiece)
                       .on_capture(self.on_capture)
                       .on_execute(self.on_execute)
                       .on_update_camera_feed(self.on_update_camera_feed)
                       .build())

    def _create_settings_config(self):
        """Create settings configuration and provider for the builder"""
        material_types = ["Material A", "Material B", "Material C"]
        config = SettingsConfig(
            default_settings={
                "speed": "100",
                "power": "50",
                "temperature": "25",
                "material_type": "Material A"
            },
            groups=[
                SettingsGroup("Motion", ["speed", "power"]),
                SettingsGroup("Advanced", ["temperature", "material_type"])
            ],
            combo_field_key="material_type"
        )

        class StandaloneSettingsProvider(ISettingsProvider):
            def __init__(self, config, available_materials):
                self._config = config
                self._materials = available_materials

            def get_all_setting_keys(self):
                return list(self._config.default_settings.keys())

            def get_default_values(self):
                return self._config.default_settings.copy()

            def get_material_type_key(self):
                return self._config.combo_field_key or ""

            def get_available_material_types(self):
                return self._materials

            def get_default_material_type(self):
                return self._materials[0] if self._materials else ""

            def get_setting_label(self, key: str):
                return key.replace('_', ' ').title()

            def get_settings_tabs_config(self):
                return [(group.title, group.keys) for group in self._config.groups]

        provider = StandaloneSettingsProvider(config, material_types)
        return config, provider

    def _create_form_factory(self):
        """Create workpiece form factory for the builder"""
        from simple_workpiece_form import SimpleWorkpieceFormFactory
        return SimpleWorkpieceFormFactory()

    def on_capture(self):
        """Handle capture request"""
        print("📸 Capture requested")
        # In real app: get image from camera, load into editor

    def on_save_workpiece(self, form_data):
        """Handle workpiece save request"""
        print(f"💾 Save requested with data: {list(form_data.keys())}")
        # form_data already contains merged form + contour data from editor
        # YOUR save logic here
        if self.controller:
            try:
                # self.controller.save_workpiece(form_data)
                print("✅ Workpiece saved successfully")
            except Exception as e:
                print(f"❌ Save failed: {e}")
        else:
            print("✅ Save completed (no controller configured)")

    def on_execute(self, workpiece):
        """
        Handle workpiece execution.

        Args:
            workpiece: Workpiece object to execute
        """
        print(f"▶️ Execute requested: {workpiece}")

        # YOUR execution logic here:
        # - Load workpiece path data
        # - Send to robot controller
        # - Start execution
        # etc.

    def on_update_camera_feed(self):
        """
        Handle camera feed update request.

        Called periodically when the editor requests a camera feed update.
        """
        print("📹 Camera feed update requested")

        # YOUR camera update logic here:
        # image = camera.get_latest_frame()
        # self.editor.set_image(image)

    def load_workpiece(self, workpiece):
        """
        Load a workpiece object into the editor.

        The workpiece must implement the following interface:
        - get_main_contour() -> np.ndarray: Main outline contour
        - get_main_contour_settings() -> dict: Settings for main contour
        - get_spray_pattern_contours() -> list: List of spray pattern contours
        - get_spray_pattern_fills() -> list: List of fill patterns

        Args:
            workpiece: Workpiece object implementing the required interface

        Example:
            class MyWorkpiece:
                def get_main_contour(self):
                    return np.array([[0,0], [100,0], [100,100], [0,100]], dtype=np.float32)
                def get_main_contour_settings(self):
                    return {"speed": "100"}
                def get_spray_pattern_contours(self):
                    return []
                def get_spray_pattern_fills(self):
                    return []

            wp = MyWorkpiece()
            integration.load_workpiece(wp)

        See WORKPIECE_FORMAT_GUIDE.md for complete documentation.
        """
        self.editor.contourEditor.load_workpiece(workpiece)

    def set_image(self, image):
        """Set background image"""
        self.editor.set_image(image)

    def get_editor_data(self) -> ContourEditorData:
        """Get current editor data"""
        return self.editor.contourEditor.workpiece_manager.export_editor_data()

    def get_workpiece_dict(self) -> dict:
        """Convert editor data to workpiece dict"""
        editor_data = self.get_editor_data()
        return WorkpieceAdapter.to_workpiece_data(editor_data)


# Usage example
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Create integration
    integration = ContourEditorIntegration()
    # Show editor
    integration.editor.show()
    sys.exit(app.exec())
