import os

from app.base.Cylinder import Cylinder
from app.scan.Scan import Scan
from app.scan.filters.ScanDelimiter import ScanDelimiter
from app.scan.filters.ScanFilterFromCylinder import ScanFilterFromCylinder
from app.scan.filters.ScanFilterFromZminToZmax import ScanFilterFromZminToZmax


class ScanUICreator:

    def __init__(self, filtering_numbers_data: dict,
                 cylinder: Cylinder,
                 is_scan_decimating: bool,
                 is_scan_filtering_by_radius: bool,
                 is_scan_filtering_by_z_limits: bool,
                 scan_file_path: str):
        self.filtering_numbers_data = filtering_numbers_data
        self.cylinder = cylinder
        self.is_scan_decimating = is_scan_decimating
        self.is_scan_filtering_by_radius = is_scan_filtering_by_radius
        self.is_scan_filtering_by_z_limits = is_scan_filtering_by_z_limits
        self.scan_file_path = scan_file_path

    @staticmethod
    def __is_correct_data(data: dict):
        for value in data.values():
            if value is None:
                return False
        return True

    def _decimate_scan(self, scan: Scan):
        data = {"n": self.filtering_numbers_data["N, раз"]}
        if self.__is_correct_data(data):
            scan.filter_scan(filter_cls=ScanDelimiter, delimiter=data["n"])
        else:
            return None, "BAD_DECIMATION_FILTER_DATA"
        return scan, "OK"

    def _filter_scan_by_radius(self, scan: Scan):
        data = {"dR": self.filtering_numbers_data["dR, м"]}
        if self.__is_correct_data(data):
            scan.filter_scan(filter_cls=ScanFilterFromCylinder,
                             cylinder=self.cylinder,
                             tolerance=data["dR"])
        else:
            return None, "BAD_RADIUS_FILTER_DATA"
        return scan, "OK"

    def _filter_scan_by_z_limits(self, scan: Scan):
        data = {"z_min": self.filtering_numbers_data["Z_min, м"],
                "z_max": self.filtering_numbers_data["Z_max, м"],}
        if self.__is_correct_data(data):
            scan.filter_scan(filter_cls=ScanFilterFromZminToZmax,
                             z_min=data["z_min"],
                             z_max=data["z_max"])
        else:
            return scan, "BAD_Z_LIMITS_FILTER_DATA"
        return scan, "OK"

    def init_scan(self):
        scan_name = os.path.basename(self.scan_file_path).split(".")[0]
        scan = Scan(scan_name)
        try:
            scan.import_points_from_file(file_path=self.scan_file_path)
        except:
            return None, "BAD_SCAN"
        msg = "OK"
        if self.is_scan_decimating and scan is not None:
            scan, msg = self._decimate_scan(scan)
        if self.is_scan_filtering_by_z_limits and scan is not None:
            scan, msg = self._filter_scan_by_z_limits(scan)
        if self.is_scan_filtering_by_radius and scan is not None:
            scan, msg = self._filter_scan_by_radius(scan)
        return scan, msg
