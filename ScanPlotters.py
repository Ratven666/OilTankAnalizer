import math
from abc import ABC, abstractmethod
from copy import deepcopy

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import TwoSlopeNorm


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
        ax.scatter(x, y, z, c=c, cmap='bwr', norm=norm)
        if self.plot_cylinder:
            ax.plot_surface(*self._data_for_cylinder_along_z(), alpha=0.5)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        plt.axis('equal')
        plt.show()