#!/usr/bin/env python3
"""
Standalone ContourEditor Application Entry Point
This is the main entry point for running the ContourEditor as a standalone application.
It sets up the necessary providers and launches the main application frame.
"""
import sys
import os
# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from contour_editor.core.main_frame import MainApplicationFrame
from contour_editor.backend.default.BezierSegmentManager import BezierSegmentManager
from contour_editor.persistence.data.segment_provider import SegmentManagerProvider
def register_default_providers():
    """Register default providers for standalone execution"""
    print("[Standalone Mode] Registering default providers...")
    # Register BezierSegmentManager as the default segment manager
    try:
        class DefaultSegmentManagerAdapter:
            """Simple pass-through adapter for standalone mode"""
            def __init__(self):
                self._manager = BezierSegmentManager()
            def __getattr__(self, name):
                return getattr(self._manager, name)
        SegmentManagerProvider.get_instance().set_manager_class(DefaultSegmentManagerAdapter)
        print("[Standalone Mode] ✓ Registered BezierSegmentManager")
    except Exception as e:
        print(f"[Standalone Mode] ⚠ Failed to register segment manager: {e}")
        import traceback
        traceback.print_exc()
        print("[Standalone Mode] Editor may not work correctly without segment manager")
def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)
    # Register providers
    register_default_providers()
    # Optional: Load stylesheet
    # stylesheetPath = "styles.qss"
    # if os.path.exists(stylesheetPath):
    #     with open(stylesheetPath, 'r') as f:
    #         app.setStyleSheet(f.read())
    # Create main window
    main_window = QWidget()
    layout = QVBoxLayout(main_window)
    # Create and add application frame
    app_frame = MainApplicationFrame()
    layout.addWidget(app_frame)
    # Configure window
    main_window.setGeometry(100, 100, 1600, 800)
    main_window.setWindowTitle("ContourEditor - Standalone Application")
    main_window.show()
    # Start event loop
    sys.exit(app.exec())
if __name__ == "__main__":
    main()
