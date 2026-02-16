

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox,
    QSizePolicy, QPushButton, QScrollArea, QDoubleSpinBox, QFormLayout
)
from PyQt6.QtCore import pyqtSignal

from ...api.providers import WidgetProvider
from ...domain.services.settings_service import SettingsService

import json
import os
from ...persistence.model.SettingsConfig import SettingsConfig, SettingsGroup


def configure_segment_settings(config: SettingsConfig):
    """Configure segment settings from a SettingsConfig object.
    Must be called before any SegmentSettingsWidget is created."""
    service = SettingsService.get_instance()
    service.configure(config)


def get_combo_field_key():
    """Return the key used for the combo box field (e.g. 'Glue Type')."""
    service = SettingsService.get_instance()
    return service.get_combo_field_key()


class SegmentSettingsWidget(QWidget):
    save_requested = pyqtSignal()

    def __init__(self, keys: list[str], combo_enums: list[list], parent=None,segment=None,global_settings=False,pointManagerWidget=None):
        super().__init__(parent)
        self.parent=parent
        self.segment = segment
        if self.segment is not None:
            self.segmentSettings = self.segment.settings
        else:
            self.segmentSettings = None
        self.global_settings = global_settings
        self.pointManagerWidget = pointManagerWidget
        # self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.keys = keys
        self.combo_enums = {label: enum for label, enum in combo_enums}  # Convert to dict
        self.inputs = {}  # Dict[str, QWidget]
        self.init_ui()
        self.populate_values()

        # Optional: Connect to a virtual keyboard if available
        try:
            from ...virtualKeyboard.VirtualKeyboard import VirtualKeyboardSingleton
            self.vk = VirtualKeyboardSingleton.getInstance()
            self.vk.shown.connect(self.on_virtual_keyboard_shown)
            self.vk.hidden.connect(self.on_virtual_keyboard_hidden)
        except ImportError:
            self.vk = None

    def init_ui(self):
        from PyQt6.QtWidgets import QGroupBox
        main_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.adjustSize()

        content_widget = QWidget()
        content_widget.setMinimumWidth(400)
        scroll.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)

        def build_group_box(title, keys):
            box = QGroupBox(title)
            grid = QGridLayout(box)
            grid.setColumnStretch(0, 1)
            grid.setColumnStretch(1, 1)
            grid.setHorizontalSpacing(12)
            grid.setVerticalSpacing(8)

            for idx, key in enumerate(keys):
                field_widget = QWidget()
                row_layout = QHBoxLayout(field_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)

                label = QLabel(key)
                label.setMinimumWidth(150)
                row_layout.addWidget(label)

                if key in self.combo_enums:
                    combo_box = QComboBox()
                    combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                    items_list = self.combo_enums[key]

                    if isinstance(items_list, list):
                        for item in items_list:
                            combo_box.addItem(str(item))
                    else:
                        print(f"ERROR: combo_enums[{key}] should be a list, got {type(items_list)}")
                        combo_box.addItem("Error loading values")

                    combo_box.currentTextChanged.connect(lambda val, k=key: self.on_value_changed(k, val))
                    row_layout.addWidget(combo_box)
                    self.inputs[key] = combo_box
                else:
                    spin = WidgetProvider.get().create_double_spinbox(parent=self.parent)
                    spin.setDecimals(3)
                    spin.setRange(-1e6, 1e6)
                    spin.setSingleStep(0.1)
                    spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                    spin.valueChanged.connect(lambda val, k=key: self.on_value_changed(k, str(val)))
                    row_layout.addWidget(spin)
                    self.inputs[key] = spin

                row, col = divmod(idx, 2)
                grid.addWidget(field_widget, row, col)

            return box

        service = SettingsService.get_instance()
        for group in service.get_settings_groups():
            layout.addWidget(build_group_box(group.title, group.keys))

        layout.addStretch(1)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.print_values)
        layout.addWidget(save_btn)

        main_layout.addWidget(scroll)

    def populate_values(self):
        service = SettingsService.get_instance()
        default_settings = service.get_defaults()

        if self.global_settings:
            settings_source = default_settings
        else:
            settings_source = self.segmentSettings if self.segmentSettings and self.segmentSettings != {} else default_settings

        for key, widget in self.inputs.items():
            value = settings_source.get(key, default_settings.get(key, ""))
            if isinstance(widget, QDoubleSpinBox):
                try:
                    widget.setValue(float(str(value).replace(",", "")) if str(value).strip() != "" else 0.0)
                except ValueError:
                    widget.setValue(0.0)
            elif isinstance(widget, QComboBox):
                index = widget.findText(str(value))
                if index >= 0:
                    widget.setCurrentIndex(index)

    def refresh_global_values(self):
        """Refresh the widget with current default settings (useful for global settings dialog)"""
        if self.global_settings:
            self.populate_values()

    def on_value_changed(self, key: str, value: str):
        print(f"[Value Changed] {key}: {value}")
        # if self.global_settings:
        #     self.pointManagerWidget.update_all_segments_settings()


    def print_values(self):
        values = self.get_values()
        print("[All Values]", values)
        self.save_requested.emit()

    def get_values(self) -> dict:
        """Return a dictionary with key: input text or selected combo."""
        result = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QDoubleSpinBox):
                result[key] = widget.value()
            elif isinstance(widget, QComboBox):
                result[key] = widget.currentText()

        if self.segment:
            self.segment.set_settings(result)
            print("segment settings", self.segment.settings)

        return result

    def get_global_values(self) -> dict:
        """Return a dictionary with key: input text or selected combo for global settings."""
        result = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QDoubleSpinBox):
                result[key] = widget.value()
            elif isinstance(widget, QComboBox):
                result[key] = widget.currentText()
        return result

    def set_values(self, values: dict):
        """Set values from a dict of key: value."""
        for key, val in values.items():
            widget = self.inputs.get(key)
            if isinstance(widget, QDoubleSpinBox):
                widget.setValue(float(str(val).replace(",", "")))
            elif isinstance(widget, QComboBox):
                index = widget.findText(val)
                if index >= 0:
                    widget.setCurrentIndex(index)

    def clear(self):
        """Clear all input fields."""
        for widget in self.inputs.values():
            if isinstance(widget, QDoubleSpinBox):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)

    def on_virtual_keyboard_shown(self):
        print("vk shown")
        scroll_area: QScrollArea = self.findChild(QScrollArea)
        if not scroll_area:
            return

        # Get currently focused widget
        focused_widget = self.focusWidget()
        if focused_widget and focused_widget in self.inputs.values():
            scroll_area.ensureWidgetVisible(focused_widget, xMargin=0, yMargin=20)
        else:
            # fallback: scroll to bottom (last widget)
            if self.inputs:
                last_widget = list(self.inputs.values())[-1]
                scroll_area.ensureWidgetVisible(last_widget, xMargin=0, yMargin=20)

    def on_virtual_keyboard_hidden(self):
        print("vk hidden")
        scroll_area: QScrollArea = self.findChild(QScrollArea)
        if scroll_area:
            scroll_area.ensureVisible(0, 0)  # scroll back to top


# Settings file path
SETTINGS_FILE_PATH = os.path.join(os.path.dirname(__file__), "..","global_segment_settings.json")

def save_settings_to_file(settings: dict):
    """Save settings to a JSON file"""
    service = SettingsService.get_instance()
    service.save_to_file(settings)

def load_settings_from_file():
    """Load settings from JSON file, return empty dict if file doesn't exist"""
    service = SettingsService.get_instance()
    return service.load_from_file()

def initialize_default_settings():
    """Initialize default settings by loading from file if available"""
    service = SettingsService.get_instance()
    service.initialize_default_settings()

def update_default_settings(new_settings: dict):
    """Update the global default settings dictionary and save to file"""
    service = SettingsService.get_instance()
    service.update_defaults(new_settings)

def get_default_settings():
    """Get the current default settings"""
    service = SettingsService.get_instance()
    return service.get_defaults()
