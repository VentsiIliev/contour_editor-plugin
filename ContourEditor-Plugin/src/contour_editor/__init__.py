"""
Contour Editor Package

A standalone, backend-agnostic contour editing widget for PyQt6.
Can be used standalone or integrated via dependency injection.
"""

# Core data models
from .persistence.data.editor_data_model import ContourEditorData
from .api.interfaces import Segment, Layer, ISegmentManager, ISettingsProvider

# Providers for dependency injection
from .api.providers import (
    DialogProvider,
    WidgetProvider,
    IconProvider,
    WorkpieceFormProvider
)
from .persistence.data.segment_provider import SegmentManagerProvider
from .persistence.data.settings_provider_registry import SettingsProviderRegistry

# Main widget
from .core.main_frame import MainApplicationFrame

# Adapters
from .api.adapters.WorkpieceAdapter import WorkpieceAdapter

# Model
from .persistence.model import BaseWorkpiece, GenericWorkpiece, WorkpieceFactory, WorkpieceField

__all__ = [
    'ContourEditorData',
    'Segment',
    'Layer',
    'ISegmentManager',
    'ISettingsProvider',
    'DialogProvider',
    'WidgetProvider',
    'IconProvider',
    'WorkpieceFormProvider',
    'SegmentManagerProvider',
    'SettingsProviderRegistry',
    'MainApplicationFrame',
    'WorkpieceAdapter',
    'BaseWorkpiece',
    'GenericWorkpiece',
    'WorkpieceFactory',
    'WorkpieceField',
]

