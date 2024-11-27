from Circle import Circle
from Cylinder import Cylinder
from DeformationCalculators import CylinderDeformationCalculator
from DeformationScan import DeformationScan
from Scan import Scan
from ScanFilters import ScanDelimiter, ScanFilterFromZminToZmax, ScanFilterFromCylinder
from ScanParsers import ScanParserFormTxtWithoutColor
from ScanPlotters import DeformationScanPlotterMPL, DeformationScanPlotterFlatMPL

scan = Scan("OilTank")

scan.load_points_from_file(file_path="src/OilTank1.txt", parser=ScanParserFormTxtWithoutColor)
print(scan)

# f_scan = scan.filter_scan(filter_cls=ScanDelimiter, replace_points_in_scan=False, delimiter=100)

# f_scan.plot()
# scan.filter_scan(filter_cls=ScanFilterFromZminToZmax, z_min=5, z_max=5.25)
scan.filter_scan(filter_cls=ScanFilterFromZminToZmax, z_min=1, z_max=10)
scan.filter_scan(filter_cls=ScanFilterFromZminToZmax, z_min=5, z_max=5.5)
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
for _ in range(5):
    cylinder = Cylinder.best_fit_cylinder_in_scan(x0=x0, y0=y0, r0=r, scan=scan)
    scan.filter_scan(filter_cls=ScanFilterFromCylinder, cylinder=cylinder, tolerance=0.1)
for _ in range(5):
    cylinder = Cylinder.best_fit_cylinder_in_scan(x0=x0, y0=y0, r0=r, scan=scan)
    scan.filter_scan(filter_cls=ScanFilterFromCylinder, cylinder=cylinder, tolerance=0.04, only_outside=True)
#
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

# def_scan.plot(plotter=DeformationScanPlotterMPL, cylinder=cylinder, def_scale=50, plot_cylinder=False)
# def_scan.plot(plotter=DeformationScanPlotterFlatMPL, cylinder=cylinder, def_scale=200)