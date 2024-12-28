import math

import ezdxf
import numpy as np

from app.deformation.FlatDeformationScan import FlatDeformationScan
from app.deformation.exporters.FlatDefScanContoursExporterToDxf import FlatDefScanContoursExporterToDxf
from app.scan.exporters.ScanExporterABC import ScanExporterABC


class CircularSectionsDefScansExporterToDxf(ScanExporterABC):

    def __init__(self, file_path="", levels_step=0.01, def_scale=1, x_grid_size=1000, y_grid_size=100):
        super().__init__(file_path)
        self.levels_step = levels_step
        self.def_scale = def_scale
        self.x_grid_size = x_grid_size
        self.y_grid_size = y_grid_size
        self.base_scan = None

    def get_circular_sections(self, flat_def_scan: FlatDeformationScan):
        flat_counter_exporter = FlatDefScanContoursExporterToDxf(file_path=self.file_path,
                                                                 levels_step=self.levels_step,
                                                                 def_scale=self.def_scale,
                                                                 x_grid_size=self.x_grid_size,
                                                                 y_grid_size=self.y_grid_size)
        flat_contours = flat_counter_exporter.get_flat_contours(flat_def_scan=flat_def_scan)
        contours = {}
        for level, collection in flat_contours.items():
            for path in collection.get_paths():
                segments = path.to_polygons()
                for idx, segment in enumerate(segments):
                    x_coords = segment[:-1, 0]
                    y_coords = segment[:-1, 1]
                    z_coords = np.full_like(x_coords, level)
                    for idx in range(len(x_coords)):
                        azimuth = x_coords[idx] / flat_def_scan.cylinder.r
                        r = flat_def_scan.cylinder.r + z_coords[idx]
                        z_coords[idx] = y_coords[idx]
                        x_coords[idx] = flat_def_scan.cylinder.x0 + r * math.cos(azimuth)
                        y_coords[idx] = flat_def_scan.cylinder.y0 + r * math.sin(azimuth)
                    contours[f"{level}_{idx}"] = [x_coords, y_coords, z_coords]
        return contours

    def get_file_name(self, flat_def_scan: FlatDeformationScan):
        return (f"CircularSections_of_{flat_def_scan.name},"
                f"_levels_step={self.levels_step},"
                f"_def_scale={self.def_scale}.dxf")

    @staticmethod
    def save_sections_to_dxf(sections_dict, file_path='section.dxf'):
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        for level, section in sections_dict.items():
            msp.add_polyline3d(list(zip(section[0], section[1], section[2])))
        doc.saveas(file_path)

    def export(self, scan):
        if isinstance(scan, FlatDeformationScan):
            sections_dict = self.get_circular_sections(flat_def_scan=scan)
            if self.file_path == "":
                file_path = self.get_file_name(flat_def_scan=scan)
            else:
                file_path = self.file_path
            self.save_sections_to_dxf(sections_dict=sections_dict, file_path=file_path)
        else:
            raise ValueError(f"Должен быть скан типа FlatDeformationScan, пеередан - {scan.__class__.__name__}")
