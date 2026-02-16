"""
Settings Provider Interface

Allows applications to inject their own settings definitions into the ContourEditor.
This makes the editor completely agnostic about what settings exist.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class ISettingsProvider(ABC):
    """
    Interface for providing settings definitions to the ContourEditor.

    Applications implement this to define their own settings structure.
    """

    @abstractmethod
    def get_all_setting_keys(self) -> List[str]:
        """
        Get all available setting keys.

        Returns:
            List of setting key strings (e.g., ["Spray Width", "Fan Speed", ...])
        """
        pass

    @abstractmethod
    def get_default_values(self) -> Dict[str, Any]:
        """
        Get default values for all settings.

        Returns:
            Dictionary mapping setting keys to default values
        """
        pass

    @abstractmethod
    def get_material_type_key(self) -> str:
        """
        Get the key name for material type setting (e.g., "Glue Type", "Paint Type").

        Returns:
            String key for material type
        """
        pass

    @abstractmethod
    def get_available_material_types(self) -> List[str]:
        """
        Get list of available material types.

        Returns:
            List of material type names
        """
        pass

    @abstractmethod
    def get_default_material_type(self) -> str:
        """
        Get the default material type.

        Returns:
            Default material type name
        """
        pass

    @abstractmethod
    def get_setting_label(self, key: str) -> str:
        """
        Get display label for a setting key.

        Args:
            key: Setting key

        Returns:
            Human-readable label (e.g., "Spray Width:" for "Spray Width")
        """
        pass

    @abstractmethod
    def get_settings_tabs_config(self) -> List[tuple[str, List[str]]]:
        """
        Get tab configuration for settings dialog.

        Returns:
            List of (tab_name, [setting_keys]) tuples
            Example: [("General", ["Spray Width", "Fan Speed"]), ...]
        """
        pass

    def validate_setting_value(self, key: str, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a setting value (optional).

        Args:
            key: Setting key
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        return (True, None)  # Default: accept all values

