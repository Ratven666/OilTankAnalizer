from FlatDeformationScan import FlatDeformationScan
from ScanFilters import ScanDelimiter
from ScanParsers import ScanParserFormTxtWithoutColor
from ScanPlotters import FlatDeformationScanPlotterMPL, DeformationInterpolation, DeformationInterpolationHeatMap

scan = FlatDeformationScan("Flat_DS_OilTank_filtered")

scan.load_points_from_file(file_path="flat_def_scan.txt", parser=ScanParserFormTxtWithoutColor)
print(scan)
scan.filter_scan(filter_cls=ScanDelimiter, delimiter=10)
print(scan)

# scan.plot()


functions = ['multiquadric', 'inverse', 'gaussian', 'linear', 'cubic', 'quintic', 'thin_plate']
scan.plot(plotter=DeformationInterpolationHeatMap, function_type="linear", show_points=False)

# scan.get_contours()

scan.get_horizontal_section(sec_elevation=5)