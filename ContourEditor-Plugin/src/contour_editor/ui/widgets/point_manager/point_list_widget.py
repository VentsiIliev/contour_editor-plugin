from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QLabel

from .models import ListItemData
from .list_item_widgets import IndentedWidget


class PointListWidget(QListWidget):
    point_clicked = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.point_items = []

        self.setAlternatingRowColors(True)
        self.itemClicked.connect(self._on_item_clicked)

    def add_anchor_point(self, seg_index, point_index, point):
        """Add an anchor point item to the list"""
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 40))

        item_data = ListItemData(
            'point',
            seg_index=seg_index,
            point_index=point_index,
            point_type='anchor'
        )
        item.setData(Qt.ItemDataRole.UserRole, item_data)

        label = QLabel(f"  📍 Anchor {point_index}: ({point.x():.1f}, {point.y():.1f})")
        label.setStyleSheet("font-size: 16px; padding: 5px;")

        indented_widget = IndentedWidget(label, indent_level=2)

        self.addItem(item)
        self.setItemWidget(item, indented_widget)

        self.point_items.append(item)

    def add_control_point(self, seg_index, point_index, point):
        """Add a control point item to the list"""
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 40))

        item_data = ListItemData(
            'point',
            seg_index=seg_index,
            point_index=point_index,
            point_type='control'
        )
        item.setData(Qt.ItemDataRole.UserRole, item_data)

        label = QLabel(f"  🎯 Control {point_index}: ({point.x():.1f}, {point.y():.1f})")
        label.setStyleSheet("font-size: 16px; padding: 5px; color: #666;")

        indented_widget = IndentedWidget(label, indent_level=2)

        self.addItem(item)
        self.setItemWidget(item, indented_widget)

        self.point_items.append(item)

    def _on_item_clicked(self, item):
        """Handle point selection"""
        item_data = item.data(Qt.ItemDataRole.UserRole)
        if item_data and item_data.item_type == 'point':
            self.point_clicked.emit({
                'role': item_data.point_type,
                'seg_index': item_data.seg_index,
                'point_index': item_data.point_index
            })

