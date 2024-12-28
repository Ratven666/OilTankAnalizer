import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from scipy.interpolate import Rbf

from app.scan.plotters.ScanPlotterABC import ScanPlotterABC


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
