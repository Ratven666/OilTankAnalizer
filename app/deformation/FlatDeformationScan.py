import math

from scipy.interpolate import Rbf

from app.base.Cylinder import Cylinder
from app.deformation.DeformationPoint import DeformationPoint
from app.deformation.calculators.DeformationScan import DeformationScan


class FlatDeformationScan(DeformationScan):

    def __init__(self, scan_name):
        super().__init__(scan_name)
        self.base_scan = None
        self.cylinder = None
        self._rbf = None

    def __str__(self):
        return (f"{self.__class__.__name__} (scan_name={self.name}, "
                f"num_of_point={len(self)}, borders={self.borders})")

    @property
    def rbf(self):
        def get_points_lists(scan):
            x, y, z = [], [], []
            for point in scan:
                x.append(point.x)
                y.append(point.y)
                z.append(point.z)
            return x, y, z

        if self._rbf is None:
            self._rbf = Rbf(*get_points_lists(self), function="linear")
            return self._rbf
        else:
            return self._rbf

    @rbf.setter
    def rbf(self, value):
        self._rbf = value

    @classmethod
    def create_flat_def_scan_from_cylinder_def_scan(cls, def_scan: DeformationScan,
                                                    cylinder: Cylinder):
        flat_def_scan = cls(scan_name=f"Flat_{def_scan.name}")
        flat_def_scan.base_scan = def_scan
        flat_def_scan.cylinder = cylinder
        for point in def_scan:
            azimuth = math.atan2(point.y - cylinder.y0,
                                 point.x - cylinder.x0)
            if azimuth < 0:
                azimuth += 2 * math.pi
            x = point.z
            y = cylinder.circle.r * azimuth
            z = point.deformation
            new_point = DeformationPoint(x=float(x), y=float(y), z=float(z), color=point.color)
            new_point.deformation = point.deformation
            flat_def_scan.add_point(new_point)
        return flat_def_scan
