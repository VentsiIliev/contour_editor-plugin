from typing import Dict, Any, Optional
import numpy as np

from contour_editor.persistence.data.editor_data_model import ContourEditorData
from contour_editor.models.segment import Segment


class WorkpieceAdapter:
    LAYER_WORKPIECE = "Workpiece"
    LAYER_CONTOUR = "Contour"
    LAYER_FILL = "Fill"

    @classmethod
    def from_workpiece(cls, workpiece) -> ContourEditorData:
        main_contour = workpiece.get_main_contour()
        main_settings = workpiece.get_main_contour_settings()

        spray_contours = workpiece.get_spray_pattern_contours()
        spray_fills = workpiece.get_spray_pattern_fills()

        layer_data = {
            cls.LAYER_WORKPIECE: [{"contour": main_contour, "settings": main_settings}],
            cls.LAYER_CONTOUR: spray_contours,
            cls.LAYER_FILL: spray_fills,
        }

        normalized_data = cls._normalize_layer_data(layer_data)
        return ContourEditorData.from_legacy_format(normalized_data)

    @classmethod
    def to_workpiece_data(cls, editor_data: ContourEditorData) -> Dict[str, Any]:
        result = {
            "main_contour": None,
            "main_settings": {},
            "spray_pattern": {
                "Contour": [],
                "Fill": []
            }
        }

        workpiece_layer = editor_data.get_layer(cls.LAYER_WORKPIECE)
        if workpiece_layer and len(workpiece_layer.segments) > 0:
            main_segment = workpiece_layer.segments[0]
            result["main_contour"] = cls._segment_to_contour_array(main_segment)
            result["main_settings"] = main_segment.settings.copy()
        else:
            result["main_contour"] = np.zeros((0, 1, 2), dtype=np.float32)
            result["main_settings"] = {}

        contour_layer = editor_data.get_layer(cls.LAYER_CONTOUR)
        if contour_layer:
            for segment in contour_layer.segments:
                contour_array = cls._segment_to_contour_array(segment)
                if contour_array is not None and len(contour_array) > 0:
                    result["spray_pattern"]["Contour"].append({
                        "contour": contour_array,
                        "settings": segment.settings.copy()
                    })

        fill_layer = editor_data.get_layer(cls.LAYER_FILL)
        if fill_layer:
            for segment in fill_layer.segments:
                contour_array = cls._segment_to_contour_array(segment)
                if contour_array is not None and len(contour_array) > 0:
                    result["spray_pattern"]["Fill"].append({
                        "contour": contour_array,
                        "settings": segment.settings.copy()
                    })

        return result

    @staticmethod
    def _normalize_layer_data(layer_data: Dict[str, Any]) -> Dict[str, Dict[str, list]]:
        normalized = {}

        for layer_name, entries in layer_data.items():
            contours = []
            settings_list = []

            if not isinstance(entries, list):
                entries = [entries]

            for item in entries:
                if not isinstance(item, dict):
                    continue

                contour = np.array(item.get("contour", []), dtype=np.float32)

                if contour.ndim == 2 and contour.shape[1] == 2:
                    contour = contour.reshape(-1, 1, 2)
                elif contour.ndim == 3 and contour.shape[1] == 1:
                    pass
                else:
                    contour = contour.reshape(-1, 1, 2)

                contours.append(contour)
                settings_list.append(item.get("settings", {}))

            normalized[layer_name] = {
                "contours": contours,
                "settings": settings_list
            }

        return normalized

    @staticmethod
    def _segment_to_contour_array(segment: Segment) -> Optional[np.ndarray]:
        if len(segment.points) == 0:
            return None

        points = np.array(
            [[pt.x(), pt.y()] for pt in segment.points],
            dtype=np.float32
        ).reshape(-1, 1, 2)

        return points

    @classmethod
    def print_summary(cls, editor_data: ContourEditorData):
        print("\n=== WorkpieceAdapter Summary ===")

        workpiece_layer = editor_data.get_layer(cls.LAYER_WORKPIECE)
        if workpiece_layer:
            print(f"Main workpiece contour: {len(workpiece_layer.segments)} segment(s)")
        else:
            print("Main workpiece contour: N/A")

        contour_layer = editor_data.get_layer(cls.LAYER_CONTOUR)
        if contour_layer:
            print(f"Spray pattern contours: {len(contour_layer.segments)} segment(s)")
        else:
            print("Spray pattern contours: N/A")

        fill_layer = editor_data.get_layer(cls.LAYER_FILL)
        if fill_layer:
            print(f"Spray pattern fills: {len(fill_layer.segments)} segment(s)")
        else:
            print("Spray pattern fills: N/A")

        stats = editor_data.get_statistics()
        print(f"Total segments: {stats['total_segments']}")
        print(f"Total points: {stats['total_points']}")
        print("================================\n")

