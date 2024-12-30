import os

from app.base.Circle import Circle
from app.base.Cylinder import Cylinder
from app.scan.Scan import Scan
from app.scan.filters.ScanFilterFromCylinder import ScanFilterFromCylinder
from app.scan.filters.ScanFilterFromZminToZmax import ScanFilterFromZminToZmax


class CylinderUICreator:

    def __init__(self, cylinder_numbers_data: dict,
                 is_use_base_cylinder: bool,
                 is_fit_cylinder: bool,
                 is_use_points_in_z_limits: bool,
                 save_cylinder_log: bool,
                 scan_file_path: str):
        self.cylinder_numbers_data = cylinder_numbers_data
        self.is_use_base_cylinder = is_use_base_cylinder
        self.is_fit_cylinder = is_fit_cylinder
        self.is_use_points_in_z_limits = is_use_points_in_z_limits
        self.save_cylinder_log = save_cylinder_log
        self.scan_file_path = scan_file_path

    @staticmethod
    def __is_correct_data(data: dict):
        for value in data.values():
            if value is None:
                return False
        return True

    def _get_base_cylinder(self):
        data = {"x0": self.cylinder_numbers_data["X, м"],
                "y0": self.cylinder_numbers_data["Y, м"],
                "r": self.cylinder_numbers_data["R, м"],
                "z": self.cylinder_numbers_data["Z, м"],
                "h": self.cylinder_numbers_data["H, м"]
                }
        if self.__is_correct_data(data):
            circle = Circle(x0=data["x0"],
                            y0=data["y0"],
                            r=data["r"])
            z_min = data["z"]
            z_max = z_min + data["h"]
            cylinder = Cylinder(circle=circle,
                                z_min=z_min,
                                z_max=z_max)
            return cylinder
        return None, "BAD_BASE_CYLINDER_DATA"

    def _get_fit_cylinder(self):
        scan = Scan("Scan")
        try:
            scan.import_points_from_file(file_path=self.scan_file_path)
        except:
            return None, "BAD_SCAN"
        data = {"z_min": self.cylinder_numbers_data["Z_min, м"],
                "z_max": self.cylinder_numbers_data["Z_max, м"]}
        if self.is_use_points_in_z_limits:
            if self.__is_correct_data(data):
                scan.filter_scan(filter_cls=ScanFilterFromZminToZmax,
                                 z_min=data["z_min"],
                                 z_max=data["z_max"])
            else:
                return None, "BAD_Z_LIMITS_DATA"
        if self.save_cylinder_log:
            path = os.path.dirname(self.scan_file_path)
            path = os.path.join(path, Cylinder.cylinder_file_path_log)
            Cylinder.cylinder_file_path_log = path
        for tolerance in [0.5, 0.3, 0.2, 0.15, 0.10, 0.075, 0.05, 0.05]:
            rx = (scan.borders["x_max"] - scan.borders["x_min"]) / 2
            ry = (scan.borders["y_max"] - scan.borders["y_min"]) / 2
            r = (rx + ry) / 2
            x0 = scan.borders["x_min"] + rx
            y0 = scan.borders["y_min"] + ry
            cylinder = Cylinder.best_fit_cylinder_in_scan(x0=x0, y0=y0, r0=r, scan=scan,
                                                          print_log=self.save_cylinder_log)
            scan.filter_scan(filter_cls=ScanFilterFromCylinder, cylinder=cylinder, tolerance=tolerance)
        return cylinder, "OK"

    def get_cylinder(self):
        if self.is_use_base_cylinder:
            return self._get_base_cylinder()
        elif self.is_fit_cylinder:
            return self._get_fit_cylinder()
