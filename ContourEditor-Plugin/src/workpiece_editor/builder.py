"""
Workpiece Editor Builder
Wraps ContourEditorBuilder and adds workpiece-specific functionality.
This builder automatically configures workpiece-specific handlers, adapters,
and managers.
"""
from typing import Optional, Callable, Any
from contour_editor import ContourEditorBuilder, BezierSegmentManager, SettingsConfig, SettingsGroup
from contour_editor.core.main_frame import MainApplicationFrame
from .managers.workpiece_manager import WorkpieceManager
from .handlers import StartHandler, CaptureHandler
from .config.segment_settings_provider import SegmentSettingsProvider
from .config.workpiece_form_factory import WorkpieceFormFactory


class WorkpieceEditorBuilder:
    """
    Builder for configuring and creating a workpiece-aware ContourEditor instance.
    This builder wraps ContourEditorBuilder and automatically injects
    workpiece-specific dependencies (WorkpieceAdapter, WorkpieceManager, handlers).
    Example:
        editor = (WorkpieceEditorBuilder()
                  .with_segment_manager(MySegmentManager)
                  .with_settings(my_config, my_provider)
                  .with_form(my_form_factory)
                  .on_save_workpiece(my_save_handler)
                  .on_capture_workpiece(my_capture_handler)
                  .build())
    """

    def __init__(self):
        self._base_builder = ContourEditorBuilder()
        self._editor: Optional[MainApplicationFrame] = None
        self._workpiece_manager: Optional[WorkpieceManager] = None
        self._start_handler: Optional[StartHandler] = None
        self._capture_handler: Optional[CaptureHandler] = None

    def with_parent(self, parent):
        """Set parent widget"""
        self._base_builder.with_parent(parent)
        return self

    def with_segment_manager(self, manager_class):
        """Configure segment manager backend (REQUIRED)"""
        self._base_builder.with_segment_manager(manager_class)
        return self

    def with_settings(self, config, provider=None):
        """Configure segment settings (optional)"""
        self._base_builder.with_settings(config, provider)
        return self

    def with_form(self, form_factory):
        """Configure workpiece form (optional)"""
        self._base_builder.with_form(form_factory)
        return self

    def with_widgets(self, widget_factory):
        """Configure custom widgets (optional)"""
        self._base_builder.with_widgets(widget_factory)
        return self

    def on_save(self, callback: Callable[[dict], None]):
        """
        Set callback for save events.
        Callback receives merged form data + workpiece contour data.
        """
        self._base_builder.on_save(callback)
        return self

    def on_capture(self, callback: Callable[[], None]):
        """Set callback for capture events"""
        self._base_builder.on_capture(callback)
        return self

    def on_execute(self, callback: Callable[[Any], None]):
        """Set callback for execute events"""
        self._base_builder.on_execute(callback)
        return self

    def on_update_camera_feed(self, callback: Callable[[], None]):
        """Set callback for camera feed update events"""
        self._base_builder.on_update_camera_feed(callback)
        return self

    def build(self) -> MainApplicationFrame:
        """Build and return configured editor instance with workpiece support"""
        # Build the base editor
        self._editor = self._base_builder.build()
        # Inject WorkpieceManager (wraps the editor)
        self._workpiece_manager = WorkpieceManager(self._editor.contourEditor.editor_with_rulers.editor)
        self._editor.contourEditor.workpiece_manager = self._workpiece_manager

        # Create and connect StartHandler for workpiece-specific start logic
        self._start_handler = StartHandler(self._editor)
        self._editor.start_requested.connect(self._start_handler.handle_start)

        # Create and connect CaptureHandler for workpiece-specific capture logic
        self._capture_handler = CaptureHandler(self._editor)
        self._editor.capture_data_received.connect(self._capture_handler.handle_capture_data)

        print("✅ Workpiece Editor built successfully with WorkpieceManager, StartHandler, and CaptureHandler")
        return self._editor

    def load_workpiece(self, workpiece):
        """
        Load a workpiece into the editor.
        Must be called after build().
        """
        if not self._workpiece_manager:
            raise RuntimeError("Cannot load workpiece before building editor. Call build() first.")
        return self._workpiece_manager.load_workpiece(workpiece)

    def export_workpiece_data(self) -> dict:
        """
        Export current editor state as workpiece-compatible data.
        Must be called after build().
        """
        if not self._workpiece_manager:
            raise RuntimeError("Cannot export workpiece data before building editor. Call build() first.")
        return self._workpiece_manager.export_to_workpiece_data()

    def get_workpiece_manager(self) -> Optional[WorkpieceManager]:
        """Get the WorkpieceManager instance (available after build())"""
        return self._workpiece_manager


def build_workpiece_editor():
    provider = SegmentSettingsProvider()

    config = SettingsConfig(
        default_settings=provider.get_default_values(),
        groups=[
            SettingsGroup("Workpiece Settings", provider.get_all_setting_keys())
        ]
    )
    # Create workpiece form factory
    print("📝 Creating workpiece form factory...")
    form_factory = WorkpieceFormFactory(glue_types=provider.get_available_material_types())
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
        print("SAVE CALLBACK TRIGGERED")

        # Extract form_data and editor_data from the package
        form_data = data_package.get('form_data', {})
        editor_data = data_package.get('editor_data')

        # Convert editor_data to workpiece format using WorkpieceAdapter
        try:
            from .adapters import WorkpieceAdapter

            # Convert ContourEditorData to workpiece data format
            workpiece_data = WorkpieceAdapter.to_workpiece_data(editor_data)

            complete_data = {**form_data, **workpiece_data}
            print(f"Complete data: {complete_data}")

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

    return editor
