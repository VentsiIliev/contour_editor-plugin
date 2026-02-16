import numpy as np
from PyQt6.QtCore import QPointF
from shapely.geometry import Polygon, LineString

from ...platform.utils.utils import shrink_contour_points, generate_spray_pattern


class ContourProcessingService:
    def __init__(self, manager):
        self.manager = manager

    def get_workpiece_contour_points(self):
        external_segments = [
            seg for seg in self.manager.get_segments()
            if hasattr(seg, 'layer') and seg.layer and seg.layer.name == "Workpiece"
        ]

        if not external_segments:
            return None

        contour = external_segments[0]
        contour_points = np.array([(pt.x(), pt.y()) for pt in contour.points])

        if contour_points.size == 0 or contour_points.shape[0] < 3:
            return None

        return contour_points

    def shrink_contour(self, contour_points, shrink_amount):
        if contour_points is None or len(contour_points) < 3:
            return None

        new_contour_points = shrink_contour_points(contour_points, shrink_amount)

        if new_contour_points is None or len(new_contour_points) < 2:
            return None

        result = []
        for i in range(len(new_contour_points) - 1):
            p1 = new_contour_points[i]
            p2 = new_contour_points[i + 1]
            result.append([QPointF(float(p1[0]), float(p1[1])), QPointF(float(p2[0]), float(p2[1]))])

        return result

    def generate_spray_pattern(self, contour_points, spacing, shrink_offset=0):
        if contour_points is None or len(contour_points) < 3:
            print("[ContourProcessingService] Invalid contour_points")
            return []

        if shrink_offset > 0:
            new_contour_points = shrink_contour_points(contour_points, shrink_offset)
            if new_contour_points is None or len(new_contour_points) < 2:
                print("[ContourProcessingService] Shrink failed")
                return []
            contour_points = new_contour_points.astype(np.float32)
        else:
            contour_points = contour_points.astype(np.float32)

        zigzag_segments = generate_spray_pattern(contour_points, spacing)
        print(f"[ContourProcessingService] Generated {len(zigzag_segments)} zigzag segments")
        if len(zigzag_segments) > 0:
            print(f"[ContourProcessingService] First segment shape: {zigzag_segments[0].shape if hasattr(zigzag_segments[0], 'shape') else type(zigzag_segments[0])}")
        return zigzag_segments

    def create_segments_from_points(self, point_lists, layer_name):
        segments = []
        for points in point_lists:
            if points is None or len(points) < 2:
                continue

            # Convert numpy array or list of points to QPointF list
            qpoints = []
            for pt in points:
                if isinstance(pt, QPointF):
                    qpoints.append(pt)
                elif isinstance(pt, (list, tuple, np.ndarray)) and len(pt) >= 2:
                    qpoints.append(QPointF(float(pt[0]), float(pt[1])))

            if len(qpoints) >= 2:
                segment = self.manager.create_segment(qpoints, layer_name=layer_name)
                self.manager.segments.append(segment)
                segments.append(segment)
        return segments

    def create_fill_pattern(self, zigzag_segments, layer_name, contour_points):
        if zigzag_segments is None or len(zigzag_segments) == 0:
            return []

        contour_poly = Polygon(np.array(contour_points).squeeze())

        all_qpoints = []
        reverse = False
        prev_point = None

        for segment_coords in zigzag_segments:
            if segment_coords is None or len(segment_coords) < 2:
                continue

            # segment_coords is [[x1, y1], [x2, y2]] from numpy array
            pts = list(segment_coords)
            if reverse:
                pts = pts[::-1]

            if prev_point is not None:
                # Add connecting point
                all_qpoints.append(QPointF(float(pts[0][0]), float(pts[0][1])))

            # Add all points in the segment
            for pt in pts:
                all_qpoints.append(QPointF(float(pt[0]), float(pt[1])))

            prev_point = pts[-1]
            reverse = not reverse

        if all_qpoints and len(all_qpoints) >= 2:
            segment = self.manager.create_segment(all_qpoints, layer_name=layer_name)
            self.manager.segments.append(segment)
            return [segment]

        return []

    def create_contour_pattern(self, zigzag_segments, layer_name):
        if zigzag_segments is None or len(zigzag_segments) == 0:
            return []

        segments = []
        reverse = False

        for segment_coords in zigzag_segments:
            if segment_coords is None or len(segment_coords) < 2:
                continue

            # segment_coords is [[x1, y1], [x2, y2]] from numpy array
            pts = list(segment_coords)
            if reverse:
                pts = pts[::-1]

            qpoints = [QPointF(float(pt[0]), float(pt[1])) for pt in pts]

            if len(qpoints) >= 2:
                segment = self.manager.create_segment(qpoints, layer_name=layer_name)
                self.manager.segments.append(segment)
                segments.append(segment)

            reverse = not reverse

        return segments

