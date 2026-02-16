from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

from .SegmentSettingsWidget import (
    SegmentSettingsWidget, update_default_settings, get_default_settings, get_combo_field_key
)


class GlobalSettingsDialog(QDialog):
    def __init__(self, point_manager_widget, glue_type_names, parent=None):
        super().__init__(parent)
        self.point_manager_widget = point_manager_widget
        self.contour_editor = point_manager_widget.contour_editor
        self.glue_type_names = glue_type_names
        self.setWindowTitle("Global Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(700)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title_label = QLabel("Global Settings - Apply to All Segments")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        default_settings = get_default_settings()
        combo_key = get_combo_field_key()
        inputKeys = [k for k in default_settings.keys() if k != combo_key]

        glue_type_names = self.glue_type_names
        comboEnums = [[combo_key, glue_type_names]] if combo_key else []

        all_keys = inputKeys + ([combo_key] if combo_key else [])
        self.segment_settings_widget = SegmentSettingsWidget(
            all_keys,
            comboEnums,
            parent=self,
            segment=None,
            global_settings=True,
            pointManagerWidget=self.point_manager_widget
        )

        layout.addWidget(self.segment_settings_widget)

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply to All Segments")
        apply_button.clicked.connect(self.apply_settings_to_all_segments)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def apply_settings_to_all_segments(self):
        settings_dict = self.segment_settings_widget.get_global_values()

        update_default_settings(settings_dict)

        if self.point_manager_widget:
            self.point_manager_widget.update_all_segments_settings(settings_dict)

        self.accept()
