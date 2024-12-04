import math
from abc import ABC, abstractmethod

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from scipy.interpolate import Rbf


class ScanPlotterABC(ABC):

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def plot(self, scan):
        pass


class ScanPlotterMPL(ScanPlotterABC):

    def __init__(self, *args, **kwargs):
        pass

    def plot(self, scan):
        ax = plt.figure().add_subplot(projection="3d")
        x, y, z, c = [], [], [], []
        for point in scan:
            x.append(point.x)
            y.append(point.y)
            z.append(point.z)
            rgb = [rgb / 255 for rgb in point.color]
            c.append(rgb)
        ax.scatter(x, y, z, c=c)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        plt.axis('equal')
        plt.show()


class DeformationScanPlotterMPL(ScanPlotterABC):

    def __init__(self, cylinder, def_scale, plot_cylinder=True):
        self.cylinder = cylinder
        self.def_scale = def_scale
        self.plot_cylinder = plot_cylinder

    def _data_for_cylinder_along_z(self):
        z = np.linspace(self.cylinder.z_min, self.cylinder.z_max, 50)
        theta = np.linspace(0, 2 * np.pi, 50)
        theta_grid, z_grid = np.meshgrid(theta, z)
        x_grid = self.cylinder.circle.r * np.cos(theta_grid) + self.cylinder.x0
        y_grid = self.cylinder.circle.r * np.sin(theta_grid) + self.cylinder.y0
        return x_grid, y_grid, z_grid

    def _calc_scaled_point(self, point):
        azimuth = math.atan2(point.y - self.cylinder.y0,
                             point.x - self.cylinder.x0)
        dx = point.deformation * math.cos(azimuth) * self.def_scale
        dy = point.deformation * math.sin(azimuth) * self.def_scale
        x = point.x + dx
        y = point.y + dy
        from Points import DeformationPoint
        s_point = DeformationPoint(x=float(x), y=float(y), z=point.z, color=point.color)
        s_point.deformation = point.deformation
        return s_point

    def plot(self, scan):
        ax = plt.figure().add_subplot(projection="3d")
        x, y, z, c = [], [], [], []
        norm = TwoSlopeNorm(vcenter=0)
        for point in scan:
            point = self._calc_scaled_point(point)
            x.append(point.x)
            y.append(point.y)
            z.append(point.z)
            c.append(point.deformation)
        ax.scatter(x, y, z, c=c, cmap='seismic', norm=norm)
        if self.plot_cylinder:
            ax.plot_surface(*self._data_for_cylinder_along_z(), alpha=0.5)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        plt.axis('equal')
        plt.show()


class FlatDeformationScanPlotterMPL:

    def __init__(self, def_scale=1, plot_flat=True):
        self.def_scale = def_scale
        self.plot_flat = plot_flat

    def _calc_scaled_point(self, point):
        z = point.deformation * self.def_scale
        from Points import DeformationPoint
        s_point = DeformationPoint(x=float(point.x), y=float(point.y), z=float(z), color=point.color)
        s_point.deformation = point.deformation
        return s_point

    def _get_flat_data(self, scan):
        x = np.linspace(scan.borders["x_min"], scan.borders["x_max"], 50)
        y = np.linspace(scan.borders["y_min"], scan.borders["y_max"], 50)
        x_grid, y_grid = np.meshgrid(x, y)
        z = np.zeros_like(x_grid)
        return x_grid, y_grid, z


    def plot(self, scan):
        ax = plt.figure().add_subplot(projection="3d")
        x, y, z, c = [], [], [], []
        norm = TwoSlopeNorm(vcenter=0)
        for point in scan:
            point = self._calc_scaled_point(point)
            x.append(point.x)
            y.append(point.y)
            z.append(point.z)
            c.append(point.deformation)
        ax.scatter(x, y, z, c=c, cmap='seismic', norm=norm)
        if self.plot_flat:
            ax.plot_surface(*self._get_flat_data(scan), alpha=0.5)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        plt.axis('equal')
        plt.show()

class DeformationInterpolation(ScanPlotterABC):

    functions = ['multiquadric', 'inverse', 'gaussian', 'linear', 'cubic', 'quintic', 'thin_plate']

    def __init__(self, function_type="multiquadric", def_scale=1, show_points=False):
        self.function_type = function_type
        self.def_scale = def_scale
        self.show_points = show_points

    def plot(self, scan):
        ax = plt.figure().add_subplot(projection="3d")
        norm = TwoSlopeNorm(vcenter=0)
        x, y, z, c = [], [], [], []
        for point in scan:
            x.append(point.x)
            y.append(point.y)
            z.append(point.z * self.def_scale)
            c.append(point.color)
        x_grid, y_grid = np.meshgrid(np.linspace(scan.borders["x_min"], scan.borders["x_max"], 100),
                                     np.linspace(scan.borders["y_min"], scan.borders["y_max"], 100))
        rbf = Rbf(x, y, z, function=self.function_type)
        z_grid = rbf(x_grid, y_grid)
        if self.show_points:
            ax.scatter(x, y, z, c=c, marker='o')
        ax.plot_surface(x_grid, y_grid, z_grid, cmap='seismic', alpha=0.5, norm=norm)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        plt.axis('equal')
        plt.show()

class DeformationInterpolationHeatMap(ScanPlotterABC):

    functions = ['multiquadric', 'inverse', 'gaussian', 'linear', 'cubic', 'quintic', 'thin_plate']

    def __init__(self, function_type="linear", show_points=False):
        self.function_type = function_type
        self.show_points = show_points

    def plot(self, scan):
        norm = TwoSlopeNorm(vcenter=0)
        x, y, z, c = [], [], [], []
        for point in scan:
            x.append(point.x)
            y.append(point.y)
            z.append(point.z)
            c.append(point.color)
        x_grid, y_grid = np.meshgrid(np.linspace(scan.borders["x_min"], scan.borders["x_max"], 100),
                                     np.linspace(scan.borders["y_min"], scan.borders["y_max"], 1000))
        rbf = Rbf(x, y, z, function=self.function_type)
        z_grid = rbf(x_grid, y_grid)
        # z_grid_rotated = np.rot90(z_grid)
        z_grid_rotated = z_grid.T

        plt.figure(figsize=(8, 6))
        if self.show_points:
            plt.scatter(x, y, z, c=c, marker='o')
        plt.imshow(z_grid_rotated, extent=[scan.borders["y_min"], scan.borders["y_max"],
                                           scan.borders["x_min"], scan.borders["x_max"]],
                   # origin='lower', cmap='seismic', norm=norm)
                   origin='lower', cmap='bwr', norm=norm)

        # Добавляем заполненные горизонтали
        # contours = plt.contourf(y_grid, x_grid, z_grid, alpha=.75, cmap='seismic', norm=norm)
        # plt.colorbar(contours, label='Z values')

        # Добавляем горизонтали
        contours = plt.contour(y_grid, x_grid, z_grid, colors='black')
        plt.clabel(contours, inline=True, fontsize=8)

        # Получаем координаты контуров
        for collection in contours.collections:
            for path in collection.get_paths():
                vertices = path.vertices
                x_coords = vertices[:, 0]
                y_coords = vertices[:, 1]
                print(f"X coordinates: {x_coords}")
                print(f"Y coordinates: {y_coords}")

        # plt.colorbar(label='Z values')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.axis('equal')
        # plt.savefig('high_resolution_heatmap.svg', dpi=300, bbox_inches='tight', format="svg")
        plt.savefig('high_resolution_heatmap.png', dpi=300, bbox_inches='tight', format="png")
        plt.show()


