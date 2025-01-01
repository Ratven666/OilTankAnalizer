import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import TwoSlopeNorm

from app.deformation.DeformationPoint import DeformationPoint


class FlatDeformationScanPlotterMPL:

    def __init__(self, def_scale=1, plot_flat=True):
        self.def_scale = def_scale
        self.plot_flat = plot_flat

    def _calc_scaled_point(self, point):
        z = point.deformation * self.def_scale
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
