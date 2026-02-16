"""
Segment Types Interfaces

Abstract interfaces for segment, layer, and manager classes.
Allows ContourEditor to work with any implementation via dependency injection.
"""

from abc import ABC, abstractmethod
from typing import Protocol, List, Optional, Dict, Any
from PyQt6.QtCore import QPointF


class Layer:
    def __init__(self, name: str, locked: bool = False, visible: bool = True):
        self.name = name
        self.locked = locked
        self.visible = visible
        self.segments: list['Segment'] = []

    def add_segment(self, segment: 'Segment'):
        self.segments.append(segment)

    def remove_segment(self, index: int):
        if 0 <= index < len(self.segments):
            del self.segments[index]

    def __str__(self):
        return f"Layer(name={self.name}, locked={self.locked}, visible={self.visible}, segments={len(self.segments)})"


class Segment:
    def __init__(self, layer: Optional[Layer] = None, settings: Optional[dict] = None):
        self.points: list[QPointF] = []
        self.controls: list[QPointF | None] = []
        self.visible = True
        self.layer = layer
        self.settings = settings or {}

    def set_settings(self, settings: dict):
        self.settings = settings

    def add_point(self, point: QPointF):
        self.points.append(point)
        if len(self.points) > 1:
            self.controls.append(None)

    def remove_point(self, index: int):
        if 0 <= index < len(self.points):
            del self.points[index]
            if index < len(self.controls):
                del self.controls[index]

    def add_control_point(self, index: int, point: QPointF):
        if 0 <= index < len(self.controls):
            self.controls[index] = point
        else:
            self.controls.append(point)

    def set_layer(self, layer: Layer):
        self.layer = layer

    def __str__(self):
        return f"Segment(points={len(self.points)}, controls={len(self.controls)}, visible={self.visible}, layer={self.layer.name if self.layer else None})"


class ISegment(ABC):
    """Abstract interface for segment objects"""

    @abstractmethod
    def add_point(self, point: QPointF) -> None:
        """Add a point to the segment"""
        pass

    @abstractmethod
    def remove_point(self, index: int) -> None:
        """Remove a point at index"""
        pass

    @abstractmethod
    def add_control_point(self, index: int, point: QPointF) -> None:
        """Add a control point for bezier curves"""
        pass

    @abstractmethod
    def set_layer(self, layer: 'ILayer') -> None:
        """Assign segment to a layer"""
        pass

    @abstractmethod
    def set_settings(self, settings: Dict[str, Any]) -> None:
        """Set segment settings"""
        pass

    @property
    @abstractmethod
    def points(self) -> List[QPointF]:
        """Get segment points"""
        pass

    @property
    @abstractmethod
    def controls(self) -> List[Optional[QPointF]]:
        """Get control points"""
        pass

    @property
    @abstractmethod
    def visible(self) -> bool:
        """Get visibility status"""
        pass

    @property
    @abstractmethod
    def layer(self) -> Optional['ILayer']:
        """Get assigned layer"""
        pass

    @property
    @abstractmethod
    def settings(self) -> Dict[str, Any]:
        """Get segment settings"""
        pass


class ILayer(ABC):
    """Abstract interface for layer objects"""

    @abstractmethod
    def add_segment(self, segment: ISegment) -> None:
        """Add a segment to this layer"""
        pass

    @abstractmethod
    def remove_segment(self, index: int) -> None:
        """Remove a segment at index"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get layer name"""
        pass

    @property
    @abstractmethod
    def locked(self) -> bool:
        """Get locked status"""
        pass

    @locked.setter
    @abstractmethod
    def locked(self, value: bool) -> None:
        """Set locked status"""
        pass

    @property
    @abstractmethod
    def visible(self) -> bool:
        """Get visibility status"""
        pass

    @visible.setter
    @abstractmethod
    def visible(self, value: bool) -> None:
        """Set visibility status"""
        pass

    @property
    @abstractmethod
    def segments(self) -> List[ISegment]:
        """Get all segments in this layer"""
        pass


class ISegmentManager(ABC):
    """Abstract interface for segment manager"""

    @abstractmethod
    def create_segment(self, points: List[QPointF], layer_name: str = "Contour") -> ISegment:
        """Create a new segment"""
        pass

    @abstractmethod
    def get_segments(self) -> List[ISegment]:
        """Get all segments"""
        pass

    @abstractmethod
    def get_layer(self, name: str) -> Optional[ILayer]:
        """Get layer by name"""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Undo last action"""
        pass

    @abstractmethod
    def redo(self) -> None:
        """Redo last undone action"""
        pass

    @property
    @abstractmethod
    def segments(self) -> List[ISegment]:
        """Direct access to segments list"""
        pass

