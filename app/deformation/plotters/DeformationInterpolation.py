import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from scipy.interpolate import Rbf

from app.scan.plotters.ScanPlotterABC import ScanPlotterABC


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
