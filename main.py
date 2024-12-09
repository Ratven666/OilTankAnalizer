import numpy as np
from matplotlib import pyplot as plt

from Circle import Circle
from Cylinder import Cylinder
from DeformationCalculators import CylinderDeformationCalculator
from DeformationScan import DeformationScan
from FlatDeformationScan import FlatDeformationScan
from Scan import Scan
from ScanFilters import ScanDelimiter, ScanFilterFromZminToZmax, ScanFilterFromCylinder
from ScanParsers import ScanParserFormTxtWithoutColor
from ScanPlotters import FlatDeformationScanPlotterMPL, DeformationInterpolation, DeformationScanPlotterMPL

scan = Scan("OilTank")

scan.load_points_from_file(file_path="src/OilTank1.txt", parser=ScanParserFormTxtWithoutColor)
print(scan)

# f_scan = scan.filter_scan(filter_cls=ScanDelimiter, replace_points_in_scan=False, delimiter=100)
# scan.filter_scan(filter_cls=ScanFilterFromZminToZmax, z_min=5, z_max=5.25)
scan.filter_scan(filter_cls=ScanFilterFromZminToZmax, z_min=2, z_max=8.5)
# scan.filter_scan(filter_cls=ScanFilterFromZminToZmax, z_min=5, z_max=5.5)
# scan = scan.filter_scan(filter_cls=ScanDelimiter, replace_points_in_scan=True, delimiter=10)

print(scan)
# scan.plot()

rx = (scan.borders["x_max"] - scan.borders["x_min"]) / 2
ry = (scan.borders["y_max"] - scan.borders["y_min"]) / 2
r = (rx + ry) / 2

x0 = scan.borders["x_min"] + rx
y0 = scan.borders["y_min"] + ry
#
#
# cylinder = Cylinder.best_fit_cylinder_in_scan(x0=x0, y0=y0, r0=r, scan=scan)
#
# print(cylinder)
#

for tolerance in [0.5, 0.3, 0.2, 0.15, 0.10, 0.075, 0.05]:
    cylinder = Cylinder.best_fit_cylinder_in_scan(x0=x0, y0=y0, r0=r, scan=scan)
    scan.filter_scan(filter_cls=ScanFilterFromCylinder, cylinder=cylinder, tolerance=tolerance)


cylinder = Cylinder.best_fit_cylinder_in_scan(x0=x0, y0=y0, r0=r, scan=scan)
#
def_scan = DeformationScan.create_def_scan_from_scan(scan)
#
def_scan.calculate_deformation(deformation_calculator=CylinderDeformationCalculator,
                               cylinder=cylinder)
#
print(def_scan)
def_scan = def_scan.filter_scan(filter_cls=ScanDelimiter, replace_points_in_scan=False, delimiter=10)
print(def_scan)

# def_scan.plot(plotter=DeformationScanPlotterMPL, cylinder=cylinder, def_scale=50, plot_cylinder=True)
# def_scan.plot(plotter=DeformationScanPlotterFlatMPL, cylinder=cylinder, def_scale=200)



flat_def_scan = FlatDeformationScan.create_flat_def_scan_from_cylinder_def_scan(def_scan=def_scan, cylinder=cylinder)


# contours = flat_def_scan.get_horizontal_section(z0=def_scan.borders["z_min"],
#                                                 z_max=def_scan.borders["z_max"], levels_step=2,
#                                                 count_of_segments=360, def_scale=50)




from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()

ax = fig.add_subplot(111, projection='3d')

contours = flat_def_scan.get_circular_sections(def_scale=50)

for c in contours.values():
    ax.plot(*c, linewidth=1)

# contours = flat_def_scan.get_vertical_section(count_of_section=64, def_scale=50)
#
# for c in contours.values():
#     ax.plot(*c, linewidth=1)
#
# contours = flat_def_scan.get_horizontal_section(z0=def_scan.borders["z_min"],
#                                                 z_max=def_scan.borders["z_max"], levels_step=0.5,
#                                                 count_of_segments=360, def_scale=50)
# for c in contours.values():
#     ax.plot(*c)


# def data_for_cylinder_along_z(cylinder):
#     z = np.linspace(cylinder.z_min, cylinder.z_max, 50)
#     theta = np.linspace(0, 2 * np.pi, 50)
#     theta_grid, z_grid = np.meshgrid(theta, z)
#     x_grid = cylinder.circle.r * np.cos(theta_grid) + cylinder.x0
#     y_grid = cylinder.circle.r * np.sin(theta_grid) + cylinder.y0
#     return x_grid, y_grid, z_grid
#
#
# ax.plot_surface(*data_for_cylinder_along_z(cylinder), alpha=0.5)

plt.axis('equal')
plt.show()
