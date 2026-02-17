#!/usr/bin/env python3
"""
Example Additional Data Form - Simple implementation
This form implements the IAdditionalDataForm protocol.
Python's Protocol provides type checking without requiring explicit inheritance.
"""
import sys
import os
# Add src to path for standalone testing
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTextEdit, QLabel
from PyQt6.QtCore import pyqtSignal
from typing import Dict, Any, Tuple, Optional
class SimpleWorkpieceForm(QWidget):
    """
    Simple form for collecting additional data.
    Implements IAdditionalDataForm protocol which requires:
    - get_data() -> Dict[str, Any] - REQUIRED
    - onSubmit() -> bool - REQUIRED
    - validate() -> Tuple[bool, str] - REQUIRED
    - clear() -> None - REQUIRED
    - prefill_form(data: Any) -> None - OPTIONAL
    This form collects:
    - Name (required)
    - Description (optional)
    - Notes (optional)
    Note: We use Protocol (duck typing) instead of ABC inheritance
    to avoid metaclass conflicts with QWidget.
    """
    submitted = pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    def setup_ui(self):
        """Setup the form UI"""
        layout = QVBoxLayout(self)
        title = QLabel("<h2>Create Workpiece</h2>")
        layout.addWidget(title)
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter workpiece name...")
        form_layout.addRow("Name *:", self.name_input)
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Brief description...")
        form_layout.addRow("Description:", self.description_input)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Additional notes (optional)...")
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes_input)
        layout.addLayout(form_layout)
        button_layout = QVBoxLayout()
        self.submit_btn = QPushButton("Create Workpiece")
        self.submit_btn.clicked.connect(self.onSubmit)
        button_layout.addWidget(self.submit_btn)
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        layout.addStretch()
    def get_data(self) -> Dict[str, Any]:
        """
        Get form data as a dictionary.
        Implements IAdditionalDataForm.get_data() (REQUIRED)
        Returns:
            dict: Form data with keys: name, description, notes
        """
        return {
            "name": self.name_input.text().strip(),
            "description": self.description_input.text().strip(),
            "notes": self.notes_input.toPlainText().strip()
        }
    def validate(self) -> Tuple[bool, str]:
        """
        Validate form data.
        Implements IAdditionalDataForm.validate() (REQUIRED)
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        data = self.get_data()
        if not data["name"]:
            return False, "Workpiece name is required"
        if len(data["name"]) < 3:
            return False, "Workpiece name must be at least 3 characters"
        return True, ""
    def onSubmit(self) -> bool:
        """
        Handle form submission.
        Implements IAdditionalDataForm.onSubmit() (REQUIRED)
        Returns:
            bool: True if submission succeeded, False otherwise
        """
        is_valid, error_msg = self.validate()
        if not is_valid:
            print(f"Validation error: {error_msg}")
            return False
        data = self.get_data()
        print(f"Data submitted -> {data}")
        if hasattr(self, 'onSubmitCallBack') and callable(self.onSubmitCallBack):
            success, message = self.onSubmitCallBack(data)
            if not success:
                print(f"Callback returned failure: {message}")
                return False
        self.submitted.emit(data)
        return True
    def clear(self) -> None:
        """
        Clear all form fields.
        Implements IAdditionalDataForm.clear() (REQUIRED)
        """
        self.name_input.clear()
        self.description_input.clear()
        self.notes_input.clear()
    def prefill_form(self, workpiece: Any) -> None:
        """
        Prefill form with data from an existing workpiece.
        Implements IAdditionalDataForm.prefill_form() (OPTIONAL)
        Args:
            workpiece: Workpiece object or dictionary with data
        """
        if hasattr(workpiece, 'name'):
            self.name_input.setText(str(workpiece.name or ""))
        elif isinstance(workpiece, dict):
            self.name_input.setText(str(workpiece.get('name', "")))
        if hasattr(workpiece, 'description'):
            self.description_input.setText(str(workpiece.description or ""))
        elif isinstance(workpiece, dict):
            self.description_input.setText(str(workpiece.get('description', "")))
        if hasattr(workpiece, 'notes'):
            self.notes_input.setPlainText(str(workpiece.notes or ""))
        elif isinstance(workpiece, dict):
            self.notes_input.setPlainText(str(workpiece.get('notes', "")))
class SimpleWorkpieceFormFactory:
    """Factory for creating SimpleWorkpieceForm instances"""
    def create_form(self, parent=None):
        """Create a new form instance"""
        return SimpleWorkpieceForm(parent)
if __name__ == "__main__":
    """Test the form standalone"""
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    form = SimpleWorkpieceForm()
    form.submitted.connect(lambda data: print(f"Form submitted: {data}"))
    form.show()
    sys.exit(app.exec())
