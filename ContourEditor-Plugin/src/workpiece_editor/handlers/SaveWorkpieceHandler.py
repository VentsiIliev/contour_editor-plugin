from typing import Dict, Any

from contour_editor.persistence.providers.dialog_provider import DialogProvider
from ..adapters.workpiece_adapter import WorkpieceAdapter
from contour_editor.persistence.data.editor_data_model import ContourEditorData
from ..models.workpiece_field_provider import WorkpieceFieldProvider


class SaveWorkpieceHandler:

    @classmethod
    def export_data(cls,
        workpiece_manager,
        form_data: Dict[str, Any],):
        editor_data = workpiece_manager.export_editor_data()

        workpiece_data = WorkpieceAdapter.to_workpiece_data(editor_data)

        complete_data = cls._merge_data(form_data, workpiece_data)
        return  complete_data

    @classmethod
    def save_workpiece(
        cls,
        workpiece_manager,
        form_data: Dict[str, Any],
        controller,
        endpoint: str = "SAVE_WORKPIECE"
    ) -> tuple[bool, str]:
        try:
            is_valid, errors = cls.validate_form_data(form_data)
            if not is_valid:
                error_message = f"Validation failed:\n{', '.join(errors)}"
                DialogProvider.get().show_error(
                    None,
                    "Validation Error",
                    error_message
                )
                return False, error_message

            editor_data = workpiece_manager.export_editor_data()

            workpiece_data = WorkpieceAdapter.to_workpiece_data(editor_data)

            complete_data = cls._merge_data(form_data, workpiece_data)

            cls.print_save_summary(editor_data, complete_data)

            success, message = controller.save_workpiece(complete_data)

            return success, message

        except Exception as e:
            error_msg = f"SaveWorkpieceHandler error: {str(e)}"
            import traceback
            traceback.print_exc()
            return False, error_msg

    @classmethod
    def prepare_workpiece_data(
        cls,
        workpiece_manager,
        form_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        editor_data = workpiece_manager.export_editor_data()
        workpiece_data = WorkpieceAdapter.to_workpiece_data(editor_data)
        return cls._merge_data(form_data, workpiece_data)

    @staticmethod
    def _merge_data(
        form_data: Dict[str, Any],
        workpiece_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        complete_data = form_data.copy()

        # Get Field enum from provider
        field_provider = WorkpieceFieldProvider.get_instance()
        Field = field_provider.get_field_enum()

        if workpiece_data.get("main_contour") is not None:
            contour_data = {
                "contour": workpiece_data["main_contour"],
                "settings": workpiece_data.get("main_settings", {})
            }
            complete_data[Field.CONTOUR.value if hasattr(Field, 'CONTOUR') else 'contour'] = contour_data

        if workpiece_data.get("spray_pattern"):
            complete_data[Field.SPRAY_PATTERN.value if hasattr(Field, 'SPRAY_PATTERN') else 'sprayPattern'] = workpiece_data["spray_pattern"]

        if Field.CONTOUR_AREA.value if hasattr(Field, 'CONTOUR_AREA') else 'contourArea' not in complete_data:
            complete_data[Field.CONTOUR_AREA.value if hasattr(Field, 'CONTOUR_AREA') else 'contourArea'] = "0"

        return complete_data

    @classmethod
    def extract_contours_only(
        cls,
        workpiece_manager
    ) -> Dict[str, Any]:
        editor_data = workpiece_manager.export_editor_data()
        return WorkpieceAdapter.to_workpiece_data(editor_data)

    @classmethod
    def print_save_summary(
        cls,
        editor_data: ContourEditorData,
        complete_data: Dict[str, Any]
    ):
        """Print summary of workpiece data being saved"""
        print("\n=== Save Workpiece Summary ===")

        # Get field enum from provider
        field_provider = WorkpieceFieldProvider.get_instance()
        Field = field_provider.get_field_enum()

        # Editor data stats
        stats = editor_data.get_statistics()
        print(f"Editor Data:")
        print(f"  - Total layers: {stats['total_layers']}")
        print(f"  - Total segments: {stats['total_segments']}")
        print(f"  - Total points: {stats['total_points']}")

        for layer_name, layer_stats in stats['layers'].items():
            print(f"  - {layer_name}: {layer_stats['segments']} segments, {layer_stats['points']} points")

        # Workpiece metadata
        print(f"\nWorkpiece Metadata:")

        # Print required fields
        for field_name in field_provider.get_required_fields():
            if hasattr(Field, field_name):
                field = getattr(Field, field_name)
                value = complete_data.get(field.value, "N/A")
                print(f"  - {field_name}: {value}")

        # Print spray pattern if present
        spray_pattern = complete_data.get(Field.SPRAY_PATTERN.value, {}) if hasattr(Field, 'SPRAY_PATTERN') else {}
        if spray_pattern:
            contour_count = len(spray_pattern.get("Contour", []))
            fill_count = len(spray_pattern.get("Fill", []))
            print(f"\nSpray Pattern:")
            print(f"  - Contour patterns: {contour_count}")
            print(f"  - Fill patterns: {fill_count}")

        print("==============================\n")

    @classmethod
    def validate_before_save(
        cls,
        editor_data: ContourEditorData,
        form_data: Dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Validate editor data and form data before saving"""
        errors = []

        # Validate editor data
        is_valid, editor_errors = editor_data.validate()
        if not is_valid:
            errors.extend([f"Editor: {err}" for err in editor_errors])

        # Get field configuration
        field_provider = WorkpieceFieldProvider.get_instance()
        Field = field_provider.get_field_enum()

        # Check required fields
        for field_name in field_provider.get_required_fields():
            if hasattr(Field, field_name):
                field = getattr(Field, field_name)
                if not form_data.get(field.value):
                    errors.append(f"Missing required field: {field_name}")

        # Check for workpiece contour data
        workpiece_layer = editor_data.get_layer("Workpiece")
        if not workpiece_layer or len(workpiece_layer.segments) == 0:
            errors.append("No workpiece contour data found")

        return (len(errors) == 0, errors)

    @classmethod
    def validate_form_data(cls, form_data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate form data against configured field requirements"""
        errors = []

        # Get field configuration
        field_provider = WorkpieceFieldProvider.get_instance()
        Field = field_provider.get_field_enum()

        # Validate required fields
        for field_name in field_provider.get_required_fields():
            if hasattr(Field, field_name):
                field = getattr(Field, field_name)
                value = form_data.get(field.value, "").strip() if isinstance(form_data.get(field.value), str) else form_data.get(field.value)

                if not value:
                    errors.append(f"{field_name.replace('_', ' ').title()} is mandatory and cannot be empty")

        # Special validation for HEIGHT field if it exists
        if hasattr(Field, 'HEIGHT'):
            height_value = form_data.get(Field.HEIGHT.value, "")
            if height_value:
                try:
                    height_float = float(str(height_value).strip())
                    if height_float <= 0:
                        errors.append("Height must be a positive number greater than 0")
                except (ValueError, TypeError):
                    errors.append("Height must be a valid number")

        return (len(errors) == 0, errors)

