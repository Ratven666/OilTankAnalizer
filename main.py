from app.base.Cylinder import Cylinder
from app.deformation.FlatDeformationScan import FlatDeformationScan
from app.deformation.calculators.CylinderDeformationCalculator import CylinderDeformationCalculator
from app.deformation.DeformationScan import DeformationScan
from app.deformation.exporters.DeformationScaledColoredScanExporter import DeformationScaledColoredScanExporter
from app.scan.Scan import Scan
from app.scan.filters.ScanDelimiter import ScanDelimiter
from app.scan.filters.ScanFilterFromCylinder import ScanFilterFromCylinder
from app.scan.filters.ScanFilterFromZminToZmax import ScanFilterFromZminToZmax
from app.scan.parsers.ScanParserFactory import ScanParserFactory

scan = Scan(scan_name="OilTank")
scan.import_points_from_file(file_path="src/OilTank1.txt", parser=ScanParserFactory)
print(scan)

scan.filter_scan(filter_cls=ScanFilterFromZminToZmax, z_min=2, z_max=8.5)
print(scan)
scan = scan.filter_scan(filter_cls=ScanDelimiter, replace_points_in_scan=True, delimiter=20)
print(scan)

rx = (scan.borders["x_max"] - scan.borders["x_min"]) / 2
ry = (scan.borders["y_max"] - scan.borders["y_min"]) / 2
r = (rx + ry) / 2

x0 = scan.borders["x_min"] + rx
y0 = scan.borders["y_min"] + ry

for tolerance in [0.5, 0.3, 0.2, 0.15, 0.10, 0.075, 0.05]:
    cylinder = Cylinder.best_fit_cylinder_in_scan(x0=x0, y0=y0, r0=r, scan=scan)
    scan.filter_scan(filter_cls=ScanFilterFromCylinder, cylinder=cylinder, tolerance=tolerance)

def_scan = DeformationScan.create_def_scan_from_scan(scan)

def_scan.calculate_deformation(deformation_calculator=CylinderDeformationCalculator,
                               cylinder=cylinder)
print(def_scan)

# def_scan.plot(plotter=DeformationScanPlotterMPL, cylinder=cylinder, def_scale=50, plot_cylinder=True)

flat_def_scan = FlatDeformationScan.create_flat_def_scan_from_cylinder_def_scan(def_scan=def_scan, cylinder=cylinder)
print(flat_def_scan)
flat_def_scan.export_data_to_file(exporter=DeformationScaledColoredScanExporter, file_path="ftest.txt", def_scale=50,
                             base_obj=cylinder)
# flat_def_scan.plot(plotter=FlatDeformationScanPlotterMPL)
# flat_def_scan.export_data_to_file(file_path="", exporter=FlatDefScanContoursExporterToDxf, levels_step=0.005,
#                                   def_scale=50)
# flat_def_scan.export_data_to_file(file_path="", exporter=FlatDefScanContoursExporterToDxf, levels_step=0.005,
#                                   def_scale=1)
# flat_def_scan.export_data_to_file(file_path="", exporter=FlatDefScanContoursExporterToDxf, levels_step=0.01,
#                                   def_scale=50)
# flat_def_scan.export_data_to_file(file_path="", exporter=CircularSectionsDefScansExporterToDxf,
#                                   levels_step=0.005,
#                                   def_scale=50)
# flat_def_scan.export_data_to_file(file_path="", exporter=CircularSectionsDefScansExporterToDxf,
#                                   levels_step=0.005,
#                                   def_scale=1)
# flat_def_scan.export_data_to_file(file_path="", exporter=CircularSectionsDefScansExporterToDxf,
#                                   levels_step=0.01,
#                                   def_scale=50)
# flat_def_scan.export_data_to_file(file_path="", z0=4, z_max=5,
#                                   levels_step=0.1, exporter=HorizontalSectionFlatScanExporterToDxf, def_scale=1)
# flat_def_scan.export_data_to_file(file_path="",
#                                   levels_step=0.1, exporter=HorizontalSectionFlatScanExporterToDxf, def_scale=50)
# flat_def_scan.export_data_to_file(file_path="", z0=4, z_max=5,
#                                   levels_step=0.01, exporter=HorizontalSectionFlatScanExporterToDxf, def_scale=50)

# flat_def_scan.export_data_to_file(file_path="", start_azimuth=45,
#                                   end_azimuth=120, count_of_section=10,
#                                   exporter=VerticalSectionsFlatScanExporterToDxf, def_scale=50)
# def_scan.export_data_to_file(file_path="", exporter=FlatDefScanContoursExporterToDxf)
