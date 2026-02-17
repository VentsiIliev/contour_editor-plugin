#!/usr/bin/env python3
"""
Domain-Agnostic Contour Editor Launcher
This script launches the pure contour editor without any workpiece-specific functionality.
Use this when you need generic contour editing without workpiece concepts.
"""
import os
import sys
# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton
from contour_editor import (
    ContourEditorBuilder,
    BezierSegmentManager,
    SettingsConfig,
    SettingsGroup,
    ISettingsProvider
)
from contour_editor.persistence.providers import AdditionalFormProvider
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
class TestDataForm(QWidget):
    """Simple test form for additional data"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.onSubmitCallBack = None
        self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        # Name field
        layout.addWidget(QLabel("Item Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter item name...")
        layout.addWidget(self.name_input)
        # Description field
        layout.addWidget(QLabel("Description:"))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Enter description...")
        layout.addWidget(self.description_input)
        # ID field
        layout.addWidget(QLabel("Item ID:"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter ID...")
        layout.addWidget(self.id_input)
        # Submit button
        self.submit_btn = QPushButton("Submit Test Data")
        self.submit_btn.clicked.connect(self.on_submit_clicked)
        layout.addWidget(self.submit_btn)
        layout.addStretch()
    def get_data(self):
        """Get form data as dictionary"""
        return {
            "name": self.name_input.text(),
            "description": self.description_input.text(),
            "id": self.id_input.text()
        }
    def on_submit_clicked(self):
        """Handle submit button click"""
        data = self.get_data()
        print(f"\n📋 Test Form Data Submitted:")
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
            return False, "Name is required"
        if not data["id"]:
            return False, "ID is required"
        return True, ""
    def clear(self):
        """Clear form fields"""
        self.name_input.clear()
        self.description_input.clear()
        self.id_input.clear()
        print("🧹 Form cleared")
    def prefill_form(self, data):
        """Prefill form with data"""
        if isinstance(data, dict):
            self.name_input.setText(data.get("name", ""))
            self.description_input.setText(data.get("description", ""))
            self.id_input.setText(data.get("id", ""))
            print(f"📥 Form prefilled with: {data}")
class TestFormFactory:
    """Factory for creating test forms"""
    def create_form(self, parent=None):
        print("🏭 Creating test form instance...")
        form = TestDataForm(parent)
        form.setFixedWidth(400)
        return form
def main():
    print("=" * 60)
    print("LAUNCHING DOMAIN-AGNOSTIC CONTOUR EDITOR WITH TEST FORM")
    print("=" * 60)
    print("This is the pure contour editor without workpiece functionality.")
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
    # Register test form
    print("📝 Registering test form...")
    form_factory = TestFormFactory()
    AdditionalFormProvider.get().set_factory(form_factory)
    print("✅ Test form registered successfully\n")
    # Build generic editor with form
    print("🔨 Building editor...")
    editor = (ContourEditorBuilder()
              .with_segment_manager(BezierSegmentManager)
              .with_settings(config, provider)
              .with_form(form_factory)
              .build())
    editor.show()
    editor.setWindowTitle("Contour Editor - Generic Mode (with Test Form)")
    print("\n✅ Generic Contour Editor launched successfully")
    print("   ✓ No workpiece concepts")
    print("   ✓ Pure contour editing")
    print("   ✓ Domain-agnostic data model")
    print("   ✓ Test form registered for additional data\n")
    print("💡 TIP: The test form allows you to add custom metadata")
    print("   to your contour data for testing purposes.")
    print("   Look for the form in the editor's additional data section.\n")
    sys.exit(app.exec())
if __name__ == '__main__':
    main()
