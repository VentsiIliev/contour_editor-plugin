from contour_editor import ISettingsProvider


class SegmentSettingsProvider(ISettingsProvider):
    """Settings provider for workpiece editing"""

    def __init__(self, material_types=None):
        self._default_settings = {
            "speed": "100",
            "power": "50",
            "passes": "1",
            "glue_type": "Type A"
        }
        self._material_types = material_types if material_types else ["Type A", "Type B", "Type C"]

    def get_all_setting_keys(self):
        return list(self._default_settings.keys())

    def get_default_values(self):
        return self._default_settings.copy()

    def get_material_type_key(self):
        return "glue_type"

    def get_available_material_types(self):
        return self._material_types

    def get_default_material_type(self):
        return self._material_types[0] if self._material_types else "Type A"

    def get_setting_label(self, key: str):
        return key.replace('_', ' ').title()

    def get_setting_value(self, key: str):
        """Get default value for a setting"""
        return self._default_settings.get(key)

    def validate_setting(self, key: str, value: str) -> bool:
        """Validate a setting value"""
        if key not in self._default_settings:
            return False
        if not value or value.strip() == "":
            return False
        # Validate numeric settings
        if key in ["speed", "power", "passes"]:
            try:
                num_value = float(value)
                if num_value < 0:
                    return False
            except (ValueError, TypeError):
                return False
        return True

    def validate_setting_value(self, key: str, value: str) -> bool:
        """Alias for validate_setting for backward compatibility"""
        return self.validate_setting(key, value)

    def get_settings_tabs_config(self):
        return [("Settings", list(self._default_settings.keys()))]
