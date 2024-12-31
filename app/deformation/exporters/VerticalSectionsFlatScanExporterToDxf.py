import math
import os

import ezdxf
import numpy as np

from app.deformation.FlatDeformationScan import FlatDeformationScan
from app.scan.exporters.ScanExporterABC import ScanExporterABC


class VerticalSectionsFlatScanExporterToDxf(ScanExporterABC):

    def __init__(self, file_path="", start_azimuth=0, end_azimuth=360,
                 count_of_section = 8,
                 count_of_segments=100,
                 def_scale=1):
        super().__init__(file_path)
        self.def_scale = def_scale
        self.start_azimuth = start_azimuth
        self.end_azimuth= end_azimuth
        self.count_of_section = count_of_section
        self.count_of_segments = count_of_segments

    def get_vertical_sections(self, flat_def_scan: FlatDeformationScan):
        rbf = flat_def_scan.rbf
        contours = {}
        sec_angels = np.linspace(self.start_azimuth, self.end_azimuth, self.count_of_section + 1)[:-1]
        for sec_angle in sec_angels:
            y_grid = np.linspace(flat_def_scan.borders["x_min"],
                                 flat_def_scan.borders["x_max"],
                                 self.count_of_segments + 1)
            l = flat_def_scan.cylinder.r * math.radians(sec_angle)
            x_grid = np.full_like(y_grid, l)
            z_grid = rbf(y_grid, x_grid)
            for idx in range(self.count_of_segments + 1):
                azimuth = x_grid[idx] / flat_def_scan.cylinder.r
                r = flat_def_scan.cylinder.r + z_grid[idx] * self.def_scale
                z_grid[idx] = y_grid[idx]
                x_grid[idx] = flat_def_scan.cylinder.x0 + r * math.cos(azimuth)
                y_grid[idx] = flat_def_scan.cylinder.y0 + r * math.sin(azimuth)
            contours[sec_angle] = [x_grid, y_grid, z_grid]
        return contours

    @staticmethod
    def save_sections_to_dxf(sections_dict, file_path='section.dxf'):
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        for level, section in sections_dict.items():
            msp.add_polyline3d(list(zip(section[0], section[1], section[2])))
        doc.saveas(file_path)

    def get_file_name(self, flat_def_scan: FlatDeformationScan):
        return (f"VerticalSections_of_{flat_def_scan.name},"
                f"_start_azimuth={self.start_azimuth},"
                f"_end_azimuth={self.end_azimuth},"
                f"_count_of_section={self.count_of_section},"
                f"_def_scale={self.def_scale}.dxf")

    def export(self, scan):
        if isinstance(scan, FlatDeformationScan):
            vertical_sections = self.get_vertical_sections(flat_def_scan=scan)
            if self.file_path == "":
                file_path = self.get_file_name(flat_def_scan=scan)
            else:
                file_path = os.path.join(self.file_path, self.get_file_name(flat_def_scan=scan))
            self.save_sections_to_dxf(sections_dict=vertical_sections, file_path=file_path)
        else:
            raise ValueError(f"Должен быть скан типа FlatDeformationScan, пеередан - {scan.__class__.__name__}")
