#!/usr/bin/env python3
"""
Workpiece Editor Launcher
This script launches the workpiece editor with workpiece-specific functionality.
Includes forms, workpiece adapters, and domain-specific features.
"""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from PyQt6.QtWidgets import QApplication
from workpiece_editor.builder import build_workpiece_editor

def main():
    app = QApplication(sys.argv)
    print("🔨 Building workpiece editor...")
    editor = build_workpiece_editor()
    editor.show()
    editor.setWindowTitle("Workpiece Editor - with Test Form")
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
