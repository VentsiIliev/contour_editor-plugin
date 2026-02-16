from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from .point_manager_coordinator import PointManagerCoordinator
class PointManagerWidget(QWidget):
    """
    Backward-compatible wrapper around PointManagerCoordinator.
    Maintains the same API for existing code while using the refactored components.
    """
    point_selected_signal = pyqtSignal(dict)
    def __init__(self, contour_editor=None, parent=None):
        super().__init__()
        # Set up layout
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        # Apply styling
        self.setStyleSheet("""
            QWidget {
                font-size: 18px;
            }
            QPushButton {
                min-width: 64px;
                min-height: 64px;
                padding: 10px;
                border: None;
            }
            QComboBox {
                min-height: 40px;
                font-size: 18px;
            }
            QListWidget {
                outline: none;
                border: 1px solid #ccc;
                background-color: white;
            }
            QListWidget::item {
                border: none;
                padding: 0px;
                margin: 0px;
            }
            QListWidget::item:selected {
                background-color: #e6f3ff;
                border: 1px solid #007acc;
            }
            QListWidget::item:hover {
                background-color: #f0f8ff;
            }
        """)
        # Create the coordinator which does all the work
        self.coordinator = PointManagerCoordinator(contour_editor, parent)
        self.layout().addWidget(self.coordinator)
        # Forward signals
        self.coordinator.point_selected_signal.connect(self.point_selected_signal.emit)
    # --- Public API (delegate to coordinator) ---
    def refresh_points(self):
        """Refresh the points display in the list"""
        self.coordinator.refresh_points()
    def update_all_segments_settings(self, settings):
        """Apply settings to all segments (called by GlobalSettingsDialog)"""
        self.coordinator.update_all_segments_settings(settings)
    def get_current_selected_layer(self):
        """Get the currently selected layer name"""
        return self.coordinator.get_current_selected_layer()
