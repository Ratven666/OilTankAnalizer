from app.deformation.__FlatDeformationScan import FlatDeformationScan
from app.scan.filters.ScanFilters import ScanDelimiter
from app.scan.parsers.ScanParsers import ScanParserFormTxtWithoutColor
from app.scan.plotters.ScanPlotters import DeformationInterpolationHeatMap

scan = FlatDeformationScan("Flat_DS_OilTank_filtered")

scan.import_points_from_file(file_path="flat_def_scan.txt", parser=ScanParserFormTxtWithoutColor)
print(scan)
scan.filter_scan(filter_cls=ScanDelimiter, delimiter=10)
print(scan)

# scan.plot()


functions = ['multiquadric', 'inverse', 'gaussian', 'linear', 'cubic', 'quintic', 'thin_plate']
scan.plot(plotter=DeformationInterpolationHeatMap, function_type="linear", show_points=False)

# scan.get_contours()

scan.get_horizontal_section(sec_elevation=5)