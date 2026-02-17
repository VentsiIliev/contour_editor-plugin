from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSizePolicy, QLabel
)
from PyQt6.QtGui import QIcon, QFont
from ....persistence.providers.icon_provider import IconProvider


class IndentedWidget(QWidget):
    """Widget with configurable left indentation"""

    def __init__(self, content_widget, indent_level=0, indent_size=20):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(indent_level * indent_size, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(content_widget)
        layout.addStretch()


class ExpandableLayerWidget(QWidget):
    """Layer widget with expand/collapse functionality"""

    def __init__(self, layer_name, layer_buttons_widget, on_expand_toggle):
        super().__init__()

        self.layer_name = layer_name
        self.on_expand_toggle = on_expand_toggle
        self.is_expanded = True

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Center vertically

        # Expand/collapse button with text fallback (folder icons don't exist)
        self.expand_btn = QPushButton("▼")  # Use text instead of missing folder icons
        self.expand_btn.setFixedSize(80, 80)
        self.expand_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-size: 20px;
            }
        """)
        self.expand_btn.setContentsMargins(0, 0, 0, 0)
        self.expand_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.expand_btn.clicked.connect(self._toggle_expansion)
        layout.addWidget(self.expand_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Layer buttons widget
        layout.addWidget(layer_buttons_widget, alignment=Qt.AlignmentFlag.AlignVCenter)

    def _toggle_expansion(self):
        self.is_expanded = not self.is_expanded
        self.expand_btn.setText("▼" if self.is_expanded else "▶")
        if self.on_expand_toggle:
            self.on_expand_toggle(self.layer_name, self.is_expanded)

    def set_expanded(self, expanded):
        self.is_expanded = expanded
        self.expand_btn.setText("▼" if expanded else "▶")


class ExpandableSegmentWidget(QWidget):
    """Segment widget with expand/collapse functionality"""

    def __init__(self, seg_index, segment_buttons_widget, on_expand_toggle):
        super().__init__()

        self.seg_index = seg_index
        self.on_expand_toggle = on_expand_toggle
        self.is_expanded = True

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Center vertically

        # Expand/collapse button
        self.expand_btn = QPushButton("▼")
        self.expand_btn.setFixedSize(80, 80)
        self.expand_btn.setStyleSheet("QPushButton { background-color: transparent; border: none;; font-weight: bold; }")
        self.expand_btn.clicked.connect(self._toggle_expansion)
        layout.addWidget(self.expand_btn)

        # Segment buttons widget
        layout.addWidget(segment_buttons_widget)

    def _toggle_expansion(self):
        self.is_expanded = not self.is_expanded
        self.expand_btn.setText("▼" if self.is_expanded else "▶")
        if self.on_expand_toggle:
            self.on_expand_toggle(self.seg_index, self.is_expanded)

    def set_expanded(self, expanded):
        self.is_expanded = expanded
        self.expand_btn.setText("▼" if expanded else "▶")


class PointWidget(QWidget):
    """Widget for displaying point information"""

    def __init__(self, point_label, coordinates):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Point label
        label = QLabel(point_label)
        label.setFont(QFont("Arial", 12))
        if point_label.startswith("P"):
            label.setStyleSheet("color: #0066cc;")  # Blue for anchor points
        else:
            label.setStyleSheet("color: #cc6600;")  # Orange for control points
        label.setFixedWidth(40)
        layout.addWidget(label)

        # Coordinates
        coords_label = QLabel(coordinates)
        coords_label.setFont(QFont("Arial", 12))
        layout.addWidget(coords_label)

        layout.addStretch()
