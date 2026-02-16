import os
import sys

# CRITICAL: Add package root to sys.path BEFORE any other imports
# This allows both relative imports (package mode) and absolute imports (standalone mode)
current_file = os.path.abspath(__file__)
core_dir = os.path.dirname(current_file)  # core/
contour_editor_dir = os.path.dirname(core_dir)  # contour_editor/
src_dir = os.path.dirname(contour_editor_dir)  # src/

# Add src to path so 'contour_editor' can be imported
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import numpy as np
from PyQt6.QtCore import (
    pyqtSignal, QSize, QEventLoop, QPointF, Qt
)
from PyQt6.QtWidgets import QFrame, QWidget, QApplication, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout
from shapely import Polygon, LineString

# Now import from package - will work in both standalone and package mode
from contour_editor.backend.default.BezierSegmentManager import BezierSegmentManager
from contour_editor.domain.services.CaptureDataHandler import CaptureDataHandler
from contour_editor.domain.services.SaveWorkpieceHandler import SaveWorkpieceHandler
from contour_editor.domain.services.contour_processing_service import ContourProcessingService
from contour_editor.core.editor_with_toolbar import ContourEditorWithBottomToolBar
from contour_editor.ui.widgets.LayerAndValueInputDialog import LayerAndValueInputDialog
from contour_editor.ui.widgets.PointManagerWidget import PointManagerWidget
from contour_editor.ui.widgets.SlidingPanel import SlidingPanel
from contour_editor.platform.utils.utils import shrink_contour_points, generate_spray_pattern
from contour_editor.ui.widgets.TopbarWidget import TopBarWidget
from contour_editor.api.providers import DialogProvider, WorkpieceFormProvider
from contour_editor.persistence.model import WorkpieceFactory


class MainApplicationFrame(QFrame):
    capture_requested = pyqtSignal()
    update_camera_feed_requested = pyqtSignal()
    save_workpiece_requested = pyqtSignal(dict)
    execute_workpiece_requested = pyqtSignal(object)  # Signal to request workpiece execution

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # State management
        self.current_view = "point_manager"  # "point_manager" or "create_workpiece"
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        self.contourEditor = ContourEditorWithBottomToolBar(None, image_path="imageDebug.png", workpiece=None)
        self.contourEditor.update_camera_feed_requested.connect(self.update_camera_feed_requested.emit)

        # Initialize ContourProcessingService with the actual editor's manager
        actual_editor = self.contourEditor.editor_with_rulers.editor

        self.contour_processing_service = ContourProcessingService(actual_editor.manager)

        # Top bar widget
        self.topbar = TopBarWidget(self.contourEditor, None)
        self.topbar.save_requested.connect(self.on_first_save_clicked)
        self.topbar.capture_requested.connect(self.capture_requested.emit)
        self.topbar.start_requested.connect(self.onStart)
        self.topbar.zigzag_requested.connect(self.generateLineGridPattern)
        self.topbar.offset_requested.connect(self.shrink)
        self.topbar.undo_requested.connect(self.on_undo)
        self.topbar.redo_requested.connect(self.on_redo)
        self.topbar.preview_requested.connect(self.show_preview)
        self.topbar.multi_select_mode_requested.connect(self.on_multi_select_mode_requested)
        self.topbar.remove_points_requested.connect(self.contourEditor.remove_selected_points)
        self.topbar.settings_requested.connect(self.contourEditor.open_settings_dialog)
        self.topbar.tools_requested.connect(self.contourEditor.show_tools_menu)
        mainLayout.addWidget(self.topbar)

        # Horizontal layout for the main content
        horizontal_widget = QWidget()
        horizontalLayout = QHBoxLayout(horizontal_widget)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)

        horizontalLayout.addWidget(self.contourEditor, stretch=1)

        # Create the right panel widgets
        self.pointManagerWidget = PointManagerWidget(self.contourEditor, self.parent)
        self.pointManagerWidget.point_selected_signal.connect(lambda point_info:self.contourEditor.selection_manager.set_single_selection_from_dict(point_info))
        self.topbar.point_manager = self.pointManagerWidget
        self.contourEditor.point_manager_widget = self.pointManagerWidget

        # Set point manager widget reference in the settings manager for Ctrl+G shortcut
        self.contourEditor.settings_manager.set_point_manager_widget(self.pointManagerWidget)

        self.pointManagerWidget.setFixedWidth(400)

        # Wrap point manager in a sliding panel
        self.sliding_panel = SlidingPanel(self.pointManagerWidget, parent=horizontal_widget)
        #
        # self.createWorkpieceForm = CreateWorkpieceForm(parent=self)
        # self.createWorkpieceForm.setFixedWidth(400)
        self.createWorkpieceForm = None # will be created on demand

        # Add sliding panel to layout (no stretch - it will use its size hints)
        horizontalLayout.addWidget(self.sliding_panel, stretch=0)

        mainLayout.addWidget(horizontal_widget)

    def on_save_workpiece_requested(self, data):
        """
        Handle workpiece save request.

        Uses SaveWorkpieceHandler to extract and merge contour data with form data.
        This method prepares the data and emits it for the controller to handle.
        """
        print(f"on_save_workpiece_requested called with data: {data}")

        try:

            # Prepare complete workpiece data using the handler
            complete_data = SaveWorkpieceHandler.prepare_workpiece_data(
                workpiece_manager=self.contourEditor.workpiece_manager,
                form_data=data
            )

            print("Workpiece data prepared for save:", complete_data.keys())
            self.save_workpiece_requested.emit(complete_data)

        except Exception as e:
            print(f"❌ Error preparing workpiece data: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to prepare workpiece data: {e}")

    def on_capture_requested(self):
        # clear the point manager and contour editor before capturing
        self.pointManagerWidget.refresh_points()
        self.contourEditor.reset_editor()

    def show_preview(self):
        self.contourEditor.save_robot_path_to_txt("preview.txt", samples_per_segment=5)
        self.contourEditor.plot_robot_path("preview.txt")

    def reset_zoom(self):
        if not self.contourEditor:
            raise ValueError("Contour editor is not set.")


        self.contourEditor.editor_with_rulers.editor.viewport_controller.reset_zoom()



    def on_redo(self):
        if not self.contourEditor:
            return

        from contour_editor.commands import CommandHistory
        from contour_editor.core.event_bus import EventBus

        history = CommandHistory.get_instance()

        if history.can_redo():
            # Use CommandHistory for segment-level operations
            history.redo()
            EventBus.get_instance().redo_executed.emit()
        else:
            # Fall back to manager's snapshot redo for point-level operations
            try:
                self.contourEditor.manager.redo()
                self.pointManagerWidget.refresh_points()
            except Exception:
                return

        # Qt's standard update mechanism - no forced repaints
        self.contourEditor.editor.update()
        self.contourEditor.update()

    def on_undo(self):
        if not self.contourEditor:
            return

        from contour_editor.commands import CommandHistory
        from contour_editor.core.event_bus import EventBus

        history = CommandHistory.get_instance()

        if history.can_undo():
            # Use CommandHistory for segment-level operations
            history.undo()
            EventBus.get_instance().undo_executed.emit()
        else:
            # Fall back to manager's snapshot undo for point-level operations
            try:
                self.contourEditor.manager.undo()
                self.pointManagerWidget.refresh_points()
            except Exception:
                return

        # Qt's standard update mechanism - no forced repaints
        self.contourEditor.editor.update()
        self.contourEditor.update()


    def on_multi_select_mode_requested(self):
        """Handle multi-select mode toggle request from toolbar"""
        if not self.contourEditor:
            print("Error: Contour editor is not set.")
            return

        # Toggle multi-select mode in the editor
        is_active = self.contourEditor.toggle_multi_select_mode()

        # Update toolbar UI to reflect the new state
        self.topbar.update_multi_select_ui(is_active)



    def set_create_workpiece_for_on_submit_callback(self, callback):
        """
        Set the callback for when the create workpiece button is clicked.
        This allows the main application to handle the creation of a workpiece.
        """
        self.createWorkpieceForm.onSubmitCallBack = callback
        print("Set create workpiece callback in main application frame.")

    def shrink(self):
        contour_points = self.contour_processing_service.get_workpiece_contour_points()

        if contour_points is None:
            DialogProvider.get().show_info(
                self,
                "No Workpiece",
                "No Workpiece contour found.",
                "No Workpiece contour found."
            )
            return

        shrink_dialog = LayerAndValueInputDialog(
            dialog_title="Shrink Contour",
            layer_label="Select layer for shrunk contour:",
            input_labels=["Enter shrink value (mm):"],
            input_defaults=[5],
            input_ranges=[(1, 50)]
        )

        shrink_dialog.show()
        loop = QEventLoop()
        shrink_dialog.finished.connect(loop.quit)
        loop.exec()

        if shrink_dialog.result() != QDialog.DialogCode.Accepted:
            print("Shrink operation canceled.")
            return

        vals = shrink_dialog.get_values()
        if not vals or len(vals) < 2:
            print("Invalid dialog return values.")
            return

        selected_layer = vals[0]
        try:
            shrink_amount = float(vals[1])
        except Exception:
            print("Invalid shrink amount provided.")
            return

        if shrink_amount <= 0:
            print("Shrink amount must be positive.")
            return

        print(f"Shrinking contour by: {shrink_amount} to layer: {selected_layer}")

        segment_point_lists = self.contour_processing_service.shrink_contour(contour_points, shrink_amount)

        if segment_point_lists is None or len(segment_point_lists) == 0:
            print("Shrink amount too large — polygon disappeared or invalid result!")
            return

        self.contour_processing_service.create_segments_from_points(segment_point_lists, selected_layer)

        self.contourEditor.update()
        self.pointManagerWidget.refresh_points()
        print(f"Added shrunk contour inward by {shrink_amount} units as new segments in {selected_layer} layer.")

    def generateLineGridPattern(self):
        """Generate zig-zag lines aligned to the Workpiece contour using minimum area bounding box orientation."""

        contour_points = self.contour_processing_service.get_workpiece_contour_points()

        if contour_points is None:
            DialogProvider.get().show_info(
                self,
                "No Workpiece",
                "No Workpiece contour found.",
                "No Workpiece contour found."
            )
            return

        dialog = LayerAndValueInputDialog(
            dialog_title="Spray Pattern Settings",
            layer_label="Select layer type:",
            input_labels=["Line grid spacing (mm):", "Shrink offset (mm):"],
            input_defaults=[20, 0.0],
            input_ranges=[(1, 1000), (0.0, 50.0)]
        )
        dialog.show()

        loop = QEventLoop()
        dialog.finished.connect(loop.quit)
        loop.exec()

        if dialog.result() != QDialog.DialogCode.Accepted:
            print("Zig-zag pattern generation cancelled by user.")
            return

        selected_layer, spacing, shrink_offset = dialog.get_values()

        # Clear segments in the selected layer (modify in-place to preserve reference)
        segments_to_keep = [
            s for s in self.contourEditor.manager.get_segments()
            if getattr(s.layer, "name", "") != selected_layer
        ]
        self.contourEditor.manager.segments.clear()
        self.contourEditor.manager.segments.extend(segments_to_keep)
        self.contourEditor.update()

        if shrink_offset < 1:
            shrink_offset = 1

        zigzag_segments = self.contour_processing_service.generate_spray_pattern(
            contour_points, spacing, shrink_offset
        )

        if zigzag_segments is None or len(zigzag_segments) == 0:
            print("Failed to generate spray pattern")
            return

        if selected_layer == "Fill":
            self.contour_processing_service.create_fill_pattern(
                zigzag_segments, selected_layer, contour_points
            )
        else:
            self.contour_processing_service.create_contour_pattern(
                zigzag_segments, selected_layer
            )

        self.contourEditor.update()
        self.pointManagerWidget.refresh_points()
        print("Generated zig-zag grid aligned to Workpiece contour.")

    def on_first_save_clicked(self):
        """Handle the first save button click - switch from point manager to create workpiece form"""
        if self.current_view == "point_manager":

            if self.createWorkpieceForm is None:
                # Try to create form using provider
                self.createWorkpieceForm = WorkpieceFormProvider.get().create_form(parent=self)

                if self.createWorkpieceForm is not None:
                    # Form was successfully created via provider
                    self.createWorkpieceForm.setFixedWidth(400)
                    # Connect data_submitted signal if it exists
                    if hasattr(self.createWorkpieceForm, 'data_submitted'):
                        self.createWorkpieceForm.data_submitted.connect(
                            lambda data: self.save_workpiece_requested.emit(data)
                        )
                    print("[ContourEditor] CreateWorkpieceForm successfully created via provider")

            # Try to create form using WorkpieceFormProvider
            if self.createWorkpieceForm is not None:
                if self.contourEditor.workpiece is not None:
                    # prefill a form with existing workpiece data
                    self.createWorkpieceForm.clear_form()
                    self.createWorkpieceForm.prefill_form(self.contourEditor.workpiece)
                else:
                    # clear the form in case it has old data
                    self.createWorkpieceForm.clear_form()
                    print("No workpiece data to prefill the form.")

                self.sliding_panel.replace_content_widget(self.createWorkpieceForm)
                # Update the save button callback to handle workpiece saving
                self.topbar.save_requested.disconnect()
                self.topbar.save_requested.connect(self.on_workpiece_save_clicked)
                self.current_view = "create_workpiece"
                print("Switched to Create Workpiece form")
            else:
                # Show the message that this functionality requires CreateWorkpieceForm provider
                DialogProvider.get().show_info(
                    self,
                    "Feature Not Available",
                    "Create Workpiece form is not configured.",
                    "This feature requires CreateWorkpieceForm to be injected via provider pattern."
                )
                print("CreateWorkpieceForm not available - feature disabled")

        # if the sliding panel is hidden, show it
        if not self.sliding_panel.is_visible:
            self.sliding_panel.toggle_panel()

    def onStart(self):
        """
        Quick start function for testing - creates mock workpiece and executes.

        Uses SaveWorkpieceHandler to extract contour data consistently.
        Validates glue types before proceeding.
        """

        # ✅ Step 1: Request glue types via signal (will be fetched by ContourEditorAppWidget)
        print("[onStart] Requesting glue types via signal...")
        if hasattr(self.contourEditor, 'editor_with_rulers'):
            if hasattr(self.contourEditor.editor_with_rulers, 'editor'):
                editor = self.contourEditor.editor_with_rulers.editor
                if hasattr(editor, 'fetch_glue_types_requested'):
                    editor.fetch_glue_types_requested.emit()
                    # Wait briefly for signal to be processed (Qt event loop)
                    QApplication.processEvents()

                    # Get the updated glue types
                    registered_glue_types = editor.glue_type_names
                    print(f"[onStart] Registered glue types: {registered_glue_types}")
                else:
                    print("[onStart] ERROR: fetch_glue_types_requested signal not found")
                    registered_glue_types = []
            else:
                print("[onStart] ERROR: editor not found")
                registered_glue_types = []
        else:
            print("[onStart] ERROR: editor_with_rulers not found")
            registered_glue_types = []

        # ✅ Step 2: Check if any glue types are registered
        if not registered_glue_types:
            QMessageBox.critical(
                self,
                "No Glue Types Configured",
                "No glue types are registered in the system!\n\n"
                "Please configure glue types in:\n"
                "1. Glue Cell Settings (Settings → Glue Cells)\n"
                "2. Assign types to cells with motor addresses\n\n"
                "Cannot start execution without glue type configuration.",
                QMessageBox.StandardButton.Ok
            )
            print("[onStart] Execution aborted: No glue types registered")
            return

        # ✅ Step 3: Validate each segment's glue type settings
        segments = self.contourEditor.manager.get_segments()
        invalid_segments = []

        for idx, segment in enumerate(segments):
            segment_settings = segment.settings if hasattr(segment, 'settings') and segment.settings else {}
            segment_glue_type = segment_settings.get('Glue Type', None)

            # Check if segment has a glue type set
            if not segment_glue_type:
                invalid_segments.append(f"Segment {idx}: No glue type set")
            # Check if the glue type is registered
            elif segment_glue_type not in registered_glue_types:
                invalid_segments.append(f"Segment {idx}: Invalid glue type '{segment_glue_type}'")

        # ✅ Step 4: Show error if any invalid segments found
        if invalid_segments:
            error_message = "Invalid glue type configuration found:\n\n"
            error_message += "\n".join(invalid_segments)
            error_message += f"\n\nRegistered glue types: {', '.join(registered_glue_types)}"
            error_message += "\n\nPlease fix segment settings before starting execution."

            QMessageBox.critical(
                self,
                "Invalid Segment Configuration",
                error_message,
                QMessageBox.StandardButton.Ok
            )
            print(f"[onStart] Execution aborted: {len(invalid_segments)} invalid segment(s)")
            return

        print(f"[onStart] ✅ All {len(segments)} segments have valid glue types")

        # ✅ Step 5: Use the first registered glue type as default for mock data
        default_glue_type = registered_glue_types[0]

        # Mock form data
        mock_data = {
            "workpieceId": "WP123",
            "name": "Test Workpiece",
            "description": "Sample description",
            "offset": "10,20,30",
            "height": "50",
            "glueQty": "100",
            "sprayWidth": "5",
            "toolId": "0",
            "gripperId": "0",
            "glueType": default_glue_type,  # ✅ Use a validated glue type
            "program": "Trace",
            "material": "Material1",
            "contourArea": "1000",
        }

        # Add pickup point if set
        if self.contourEditor.pickup_point is not None:
            pickup_point_str = f"{self.contourEditor.pickup_point.x():.2f},{self.contourEditor.pickup_point.y():.2f}"
            mock_data["pickup_point"] = pickup_point_str
            print(f"Pickup point included: {pickup_point_str}")
        else:
            print("No pickup point set")

        # Use SaveWorkpieceHandler to extract and merge contour data
        try:

            complete_data = SaveWorkpieceHandler.prepare_workpiece_data(
                workpiece_manager=self.contourEditor.workpiece_manager,
                form_data=mock_data
            )

        except Exception as e:
            print(f"❌ Error preparing workpiece data: {e}")
            QMessageBox.warning(self, "Error", f"Failed to prepare workpiece data: {e}")
            return

        # Validate spray pattern data
        spray_pattern = complete_data.get("sprayPattern", {})
        contour_data = spray_pattern.get("Contour", [])
        fill_data = spray_pattern.get("Fill", [])

        def has_valid_contours(contour_list):
            """Check if contour list has valid contour data"""
            if not contour_list or len(contour_list) == 0:
                return False
            for item in contour_list:
                if isinstance(item, dict) and 'contour' in item:
                    contour = item['contour']
                    if contour.size > 0 and len(contour) > 0:
                        return True
            return False

        if not has_valid_contours(contour_data) and not has_valid_contours(fill_data):
            QMessageBox.warning(self, "No Spray Pattern", "No valid contour or fill patterns found!")
            return

        # Create workpiece using factory
        try:
            wp = WorkpieceFactory.create_workpiece(complete_data)
            print("Workpiece created:", wp)
            print("Start button pressed: CONTOUR EDITOR ")
            # Emit signal to request execution instead of direct controller call
            self.execute_workpiece_requested.emit(wp)
        except Exception as e:
            QMessageBox.critical(self, "Workpiece Creation Failed",
                               f"Failed to create workpiece: {e}")
            import traceback
            traceback.print_exc()

    def on_workpiece_save_clicked(self):
        """Handle the second save button click - save the workpiece"""
        # Pass pickup point data to the form before submitting
        if self.contourEditor.pickup_point is not None:
            pickup_point_str = f"{self.contourEditor.pickup_point.x():.2f},{self.contourEditor.pickup_point.y():.2f}"
            # Store pickup point in the form's data
            self.createWorkpieceForm.pickup_point = pickup_point_str
            print(f"Pickup point passed to form: {pickup_point_str}")
        else:
            # Clear pickup point if none is set
            self.createWorkpieceForm.pickup_point = None
            print("No pickup point set, clearing form attribute")

        # Call the workpiece form's submit method and show confirmation
        try:
            success = self.createWorkpieceForm.onSubmit()
            if success:
                QMessageBox.information(self, "Saved", "Workpiece saved successfully.")
                print("Workpiece saved!")
            else:
                # Error already shown by form validation, just return
                print("Workpiece form validation failed")
                return
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Failed to save workpiece: {e}")
            return

        # Optionally, you could reset back to point manager or keep the form
        # For now, we'll keep the create workpiece form visible
        # Switch back to point manager view
        try:
            # Hide the create workpiece form and show point manager
            self.contourEditor.camera_feed_update_timer.start()
            self.contourEditor.reset_editor()
            self.pointManagerWidget.refresh_points()

            self.sliding_panel.replace_content_widget(self.pointManagerWidget)

            # Restore the topbar save button callback to the first-save behavior
            try:
                self.topbar.save_requested.disconnect()
            except Exception:
                # ignore if not connected
                pass
            self.topbar.save_requested.connect(self.on_first_save_clicked)

            self.current_view = "point_manager"
            print("Switched back to point manager view")
        except Exception as e:
            QMessageBox.warning(self, "View Switch Failed", f"Saved but failed to switch view: {e}")
            import traceback
            traceback.print_exc()
            print(f"Error switching to point manager: {e}")

    def set_image(self, image):
        self.contourEditor.set_image(image)

    def init_contours(self, contours):
        """
        Initialize contours using legacy format.

        DEPRECATED: Use load_capture_data() for new code.
        """
        print("in contour editor.py")
        self.contourEditor.initContour(contours)

    def load_capture_data(self, capture_data, close_contour=True):
        """
        Load camera capture data into the editor using ContourEditorData.

        This is the preferred method for loading capture data as it uses
        the centralized CaptureDataHandler.

        Args:
            capture_data: Dictionary with keys:
                - "contours": numpy array or list of contours
                - "image": optional image data
                - "height": optional height measurement
            close_contour: Whether to close the contour

        Returns:
            ContourEditorData instance that was loaded
        """

        return CaptureDataHandler.handle_capture_data(
            workpiece_manager=self.contourEditor.workpiece_manager,
            capture_data=capture_data,
            close_contour=close_contour
        )

    def resizeEvent(self, event):
        """Resize content and side menu dynamically."""
        super().resizeEvent(event)
        new_width = self.width()

        # Guard against resizeEvent being called before initialization completes
        if not hasattr(self, 'topbar'):
            return

        # Adjust icon sizes of the sidebar buttons
        icon_size = int(new_width * 0.05)  # 5% of the new window width
        for button in self.topbar.buttons:
            button.setIconSize(QSize(icon_size, icon_size))

        if self.createWorkpieceForm is not None:

            if hasattr(self.createWorkpieceForm, 'buttons'):
                for button in self.createWorkpieceForm.buttons:
                    button.setIconSize(QSize(icon_size, icon_size))

            # Resize the icons in the labels
            if hasattr(self.createWorkpieceForm, 'icon_widgets'):
                for label, original_pixmap in self.createWorkpieceForm.icon_widgets:
                    scaled_pixmap = original_pixmap.scaled(
                        int(icon_size / 2), int(icon_size / 2),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    label.setPixmap(scaled_pixmap)


