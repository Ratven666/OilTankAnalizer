from app.deformation.DeformationPoint import DeformationPoint
from app.scan.Scan import Scan


class DeformationScan(Scan):

    def __init__(self, scan_name):
        super().__init__(scan_name)
        self.min_deformation = None
        self.max_deformation = None
        self.mse = None

    def __str__(self):
        s_str = super().__str__()
        return (f"{s_str}\b\b def_limits=[({self.min_deformation:.3f})-({self.max_deformation:.3f})]_"
                f"def_mse={self.mse:.3f}")

    def add_point(self, point):
        if isinstance(point, DeformationPoint):
            self._points.append(point)
            self.borders = self._check_border(borders_dict=self.borders, point=point)
        else:
            d_point = DeformationPoint.create_def_point_from_point(point)
            self.add_point(d_point)

    def _calk_def_limits(self):
        def_lst = []
        for point in self:
            def_lst.append(point.deformation)
        self.min_deformation = min(def_lst)
        self.max_deformation = max(def_lst)

    def _calk_def_mse(self):
        vv = []
        for point in self:
            vv.append(point.deformation ** 2)
        sum_vv = sum(vv)
        mse = (sum_vv / len(vv)) ** 0.5
        self.mse = mse

    @classmethod
    def create_def_scan_from_scan(cls, scan: Scan):
        def_scan = cls(scan_name=scan.name)
        for point in scan:
            def_scan.add_point(point)
        return def_scan

    def calculate_deformation(self, deformation_calculator, *args, **kwargs):
        deformation_calculator = deformation_calculator(*args, **kwargs)
        deformation_calculator.calculate(def_scan=self)
        self._calk_def_limits()
        self._calk_def_mse()
