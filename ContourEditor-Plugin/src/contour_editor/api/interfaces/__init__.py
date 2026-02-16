"""
Interfaces for ContourEditor

Abstract interfaces that allow dependency injection and decoupling.
"""

from .segment_types import ISegmentManager, Segment, Layer
from .settings_provider import ISettingsProvider

__all__ = ['ISegmentManager', 'ISettingsProvider', 'Segment', 'Layer']

