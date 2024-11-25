from Scan import Scan
from ScanFilters import ScanDelimiter, ScanFilterFromZminToZmax

scan = Scan("Heap")

scan.load_points_from_file(file_path="src/SKLD.txt")
print(scan)

f_scan = scan.filter_scan(filter_cls=ScanDelimiter, replace_points_in_scan=False, delimiter=10)
print(scan)
print(f_scan)

f_scan.filter_scan(filter_cls=ScanFilterFromZminToZmax, z_min=60, z_max=62)
print(f_scan)
f_scan.plot()