import math
import os

import ezdxf
import numpy as np
from matplotlib import pyplot as plt

from app.deformation.FlatDeformationScan import FlatDeformationScan
from app.scan.exporters.ScanExporterABC import ScanExporterABC


class FlatDefScanContoursExporterToDxf(ScanExporterABC):

    def __init__(self, file_path="", levels_step=0.01, def_scale=1, x_grid_size=1000, y_grid_size=100):
        super().__init__(file_path)
        self.levels_step = levels_step
        self.def_scale = def_scale
        self.x_grid_size = x_grid_size
        self.y_grid_size = y_grid_size

    def get_flat_contours(self, flat_def_scan: FlatDeformationScan):
        levels_0 = flat_def_scan.borders["z_min"] - math.fmod(flat_def_scan.borders["z_min"],
                                                              self.levels_step)
        levels = np.arange(levels_0, flat_def_scan.borders["z_max"], self.levels_step)
        rbf = flat_def_scan.rbf
        x_grid, y_grid = np.meshgrid(np.linspace(0, flat_def_scan.borders["y_max"],
                                                 self.x_grid_size),
                                     np.linspace(flat_def_scan.borders["x_min"], flat_def_scan.borders["x_max"],
                                                 self.y_grid_size))
        z_grid = rbf(y_grid, x_grid)
        z_grid *= self.def_scale
        levels *= self.def_scale
        contours = plt.contour(x_grid, y_grid, z_grid, levels=levels, colors='black')
        contours_dict = {}
        for idx, contour in enumerate(contours.collections):
            contours_dict[levels[idx]] = contour
        return contours_dict

    def get_file_name(self, flat_def_scan: FlatDeformationScan):
        return (f"Contours_of_{flat_def_scan.name},"
                f"_levels_step={self.levels_step},"
                f"_def_scale={self.def_scale}.dxf")

    def save_flat_contours_to_dxf(self, flat_def_scan: FlatDeformationScan):
        contours = self.get_flat_contours(flat_def_scan)
        if self.file_path == "":
            file_path = self.get_file_name(flat_def_scan=flat_def_scan)
        else:
            file_path = os.path.join(self.file_path, self.get_file_name(flat_def_scan=flat_def_scan))
        doc = ezdxf.new("R2010")
        msp = doc.modelspace()
        for level, collection in contours.items():
            for path in collection.get_paths():
                segments = path.to_polygons()
                for segment in segments:
                    x_coords = segment[:-1, 0]
                    y_coords = segment[:-1, 1]
                    z_coords = np.full_like(x_coords, level)
                    msp.add_lwpolyline(list(zip(x_coords, y_coords, z_coords)),
                                       dxfattribs={"elevation": z_coords[0]})
        doc.saveas(file_path)

    def export(self, scan):
        if isinstance(scan, FlatDeformationScan):
            self.save_flat_contours_to_dxf(flat_def_scan=scan)
        else:
            raise ValueError(f"Должен быть скан типа FlatDeformationScan, пеередан - {scan.__class__.__name__}")
