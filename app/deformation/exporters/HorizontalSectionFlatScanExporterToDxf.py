import math

import ezdxf
import numpy as np

from app.deformation.FlatDeformationScan import FlatDeformationScan
from app.scan.exporters.ScanExporterABC import ScanExporterABC


class HorizontalSectionFlatScanExporterToDxf(ScanExporterABC):

    def __init__(self, file_path="", z0=None, z_max=None, count_of_segments=360,
                 levels_step=0.01, def_scale=1):
        super().__init__(file_path)
        self.levels_step = levels_step
        self.def_scale = def_scale
        self.z0 = z0
        self.z_max= z_max
        self.count_of_segments = count_of_segments

    def _init_z_limits(self, scan):
        if self.z0 is None:
            self.z0 = scan.borders["x_min"]
        if self.z_max is None:
            self.z_max = scan.borders["x_max"]

    def get_horizontal_sections(self, flat_def_scan: FlatDeformationScan):
        rbf = flat_def_scan.rbf
        contours = {}
        sec_elevations = np.arange(self.z0, self.z_max + 1e-5, self.levels_step)
        for sec_elev in sec_elevations:
            x_grid = np.linspace(flat_def_scan.borders["y_min"],
                                 flat_def_scan.borders["y_max"],
                                 self.count_of_segments+1)
            y_grid = np.full_like(x_grid, sec_elev)
            z_grid = rbf(y_grid, x_grid)
            for idx in range(self.count_of_segments+1):
                azimuth = x_grid[idx] / flat_def_scan.cylinder.r
                r = flat_def_scan.cylinder.r + z_grid[idx] * self.def_scale
                z_grid[idx] = y_grid[idx]
                x_grid[idx] = flat_def_scan.cylinder.x0 + r * math.cos(azimuth)
                y_grid[idx] = flat_def_scan.cylinder.y0 + r * math.sin(azimuth)
            contours[sec_elev] = [x_grid, y_grid, z_grid]
        return contours

    @staticmethod
    def save_sections_to_dxf(sections_dict, file_path='section.dxf'):
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        for level, section in sections_dict.items():
            msp.add_polyline3d(list(zip(section[0], section[1], section[2])))
        doc.saveas(file_path)

    def get_file_name(self, flat_def_scan: FlatDeformationScan):
        return (f"HorizontalSections_of_{flat_def_scan.name},"
                f"_levels_step={self.levels_step},"
                f"_z0={self.z0},_z_max={self.z_max}"
                f"_def_scale={self.def_scale}.dxf")

    def export(self, scan):
        if isinstance(scan, FlatDeformationScan):
            self._init_z_limits(scan)
            horizontal_sections = self.get_horizontal_sections(flat_def_scan=scan)
            if self.file_path == "":
                file_path = self.get_file_name(flat_def_scan=scan)
            else:
                file_path = self.file_path
            self.save_sections_to_dxf(sections_dict=horizontal_sections, file_path=file_path)
        else:
            raise ValueError(f"Должен быть скан типа FlatDeformationScan, пеередан - {scan.__class__.__name__}")
