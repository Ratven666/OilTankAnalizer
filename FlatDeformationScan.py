import math

import ezdxf
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import Rbf

from Cylinder import Cylinder
from DeformationScan import DeformationScan
from Points import DeformationPoint


class FlatDeformationScan(DeformationScan):

    def __init__(self, scan_name, def_scale=1, rbf_function="linear"):
        super().__init__(scan_name)
        self.def_scale = def_scale
        self.function = rbf_function
        self.base_scan = None
        self.cylinder = None
        self.rbf = None

    def __str__(self):
        return (f"{self.__class__.__name__} (scan_name={self.name}, "
                f"num_of_point={len(self)}, borders={self.borders})")

    def get_rbf(self, function=None):
        def get_points_lists(scan):
            x, y, z = [], [], []
            for point in scan:
                x.append(point.x)
                y.append(point.y)
                z.append(point.z)
            return x, y, z

        if self.rbf is None and function is None:
            self.rbf = Rbf(*get_points_lists(self), function=self.function)
            return self.rbf
        elif self.rbf is not None and (function is None or function==self.function):
            return self.rbf
        else:
            return Rbf(*get_points_lists(self), function=function)

    def get_flat_contours(self, levels_step=0.01, function="linear", def_scale=1):
        levels_0 = self.borders["z_min"] - math.fmod(self.borders["z_min"], levels_step)
        levels = np.arange(levels_0, self.borders["z_max"], levels_step)
        rbf = self.get_rbf(function=function)
        x_grid, y_grid = np.meshgrid(np.linspace(0, self.borders["y_max"], 1000),
                                     np.linspace(self.borders["x_min"], self.borders["x_max"], 100))
        z_grid = rbf(y_grid, x_grid)
        z_grid *= def_scale
        contours = plt.contour(x_grid, y_grid, z_grid, levels=levels, colors='black')
        contours_dict = {}
        for idx, contour in enumerate(contours.collections):
            contours_dict[levels[idx]] = contour
        return contours_dict

    def get_circular_sections(self, levels_step=0.01, function="linear", def_scale=None):
        if def_scale is None:
            def_scale = self.def_scale
        flat_contours = self.get_flat_contours(levels_step=levels_step, function=function)
        contours = {}
        for level, collection in flat_contours.items():
            for path in collection.get_paths():
                segments = path.to_polygons()
                for idx, segment in enumerate(segments):
                    x_coords = segment[:-1, 0]
                    y_coords = segment[:-1, 1]
                    z_coords = np.full_like(x_coords, level)
                    for idx in range(len(x_coords)):
                        azimuth = x_coords[idx] / self.cylinder.r
                        r = self.cylinder.r + z_coords[idx] * def_scale
                        z_coords[idx] = y_coords[idx]
                        x_coords[idx] = self.cylinder.x0 + r * math.cos(azimuth)
                        y_coords[idx] = self.cylinder.y0 + r * math.sin(azimuth)
                    contours[f"{level}_{idx}"] = [x_coords, y_coords, z_coords]
        return contours

    def save_flat_contours_to_dxf(self, levels_step=0.01, file_path='contours.dxf', function="linear"):
        contours = self.get_flat_contours(levels_step=levels_step, function=function)
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        for level, collection in contours.items():
            for path in collection.get_paths():
                segments = path.to_polygons()
                for segment in segments:
                    x_coords = segment[:-1, 0]
                    y_coords = segment[:-1, 1]
                    z_coords = np.full_like(x_coords, level)
                    msp.add_lwpolyline(list(zip(x_coords, y_coords, z_coords)),
                                       dxfattribs={'elevation': z_coords[0]})
        doc.saveas(file_path)

    @staticmethod
    def save_sections_to_dxf(sections_dict, file_path='section.dxf'):
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        for level, section in sections_dict.items():
            msp.add_polyline3d(list(zip(section[0], section[1], section[2])))
        doc.saveas(file_path)

    def get_horizontal_section(self, z0, z_max, levels_step, count_of_segments=100, function="linear", def_scale=None):
        if def_scale is None:
            def_scale = self.def_scale
        rbf = self.get_rbf(function=function)
        contours = {}
        sec_elevations = np.arange(z0, z_max + 1e-5, levels_step)
        for sec_elev in sec_elevations:
            x_grid = np.linspace(self.borders["y_min"], self.borders["y_max"], count_of_segments+1)
            y_grid = np.full_like(x_grid, sec_elev)
            z_grid = rbf(y_grid, x_grid)
            for idx in range(count_of_segments+1):
                azimuth = x_grid[idx] / self.cylinder.r
                r = self.cylinder.r + z_grid[idx] * def_scale
                z_grid[idx] = y_grid[idx]
                x_grid[idx] = self.cylinder.x0 + r * math.cos(azimuth)
                y_grid[idx] = self.cylinder.y0 + r * math.sin(azimuth)
            contours[sec_elev] = [x_grid, y_grid, z_grid]
        return contours

    def get_vertical_section(self, start_azimuth=0, end_azimuth=360, count_of_section=8,
                             count_of_segments=100, function="linear", def_scale=None):
        if def_scale is None:
            def_scale = self.def_scale
        rbf = self.get_rbf(function=function)
        contours = {}
        sec_angels = np.linspace(start_azimuth, end_azimuth, count_of_section+1)[:-1]
        for sec_angle in sec_angels:
            y_grid = np.linspace(self.borders["x_min"], self.borders["x_max"], count_of_segments+1)
            l = self.cylinder.r * math.radians(sec_angle)
            x_grid = np.full_like(y_grid, l)
            z_grid = rbf(y_grid, x_grid)
            for idx in range(count_of_segments+1):
                azimuth = x_grid[idx] / self.cylinder.r
                r = self.cylinder.r + z_grid[idx] * def_scale
                z_grid[idx] = y_grid[idx]
                x_grid[idx] = self.cylinder.x0 + r * math.cos(azimuth)
                y_grid[idx] = self.cylinder.y0 + r * math.sin(azimuth)
            contours[sec_angle] = [x_grid, y_grid, z_grid]
        return contours

    @classmethod
    def create_flat_def_scan_from_cylinder_def_scan(cls, def_scan: DeformationScan,
                                                    cylinder: Cylinder):
        flat_def_scan = cls(scan_name=f"Flat_DS_{def_scan.name}")
        flat_def_scan.base_scan = def_scan
        flat_def_scan.cylinder = cylinder
        for point in def_scan:
            azimuth = math.atan2(point.y - cylinder.y0,
                                 point.x - cylinder.x0)
            if azimuth < 0:
                azimuth += 2 * math.pi
            x = point.z
            y = cylinder.circle.r * azimuth
            z = point.deformation
            new_point = DeformationPoint(x=float(x), y=float(y), z=float(z), color=point.color)
            new_point.deformation = point.deformation
            flat_def_scan.add_point(new_point)
        return flat_def_scan
