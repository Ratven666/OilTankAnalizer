from Circle import Circle
from Scan import Scan


class Cylinder:

    def __init__(self, circle: Circle, z_min, z_max):
        self.circle = circle
        self.z_min = z_min
        self.z_max = z_max

    @property
    def x0(self):
        return self.circle.x0

    @property
    def y0(self):
        return self.circle.y0

    @property
    def r(self):
        return self.circle.r

    def __str__(self):
        return f"Cylinder (circle={self.circle}, z_min={self.z_min}, z_max={self.z_max})"

    @classmethod
    def best_fit_cylinder_in_scan(cls, x0, y0, r0, scan: Scan, max_iteration=50, max_tolerance=1e-4, print_log=True):
        circle_0 = Circle(x0=x0, y0=y0, r=r0)
        circle_0.best_fit_circle_in_scan(scan=scan,
                                         max_iteration=max_iteration,
                                         max_tolerance=max_tolerance,
                                         print_log=print_log)
        return cls(circle=circle_0,
                   z_min=scan.borders["z_min"],
                   z_max=scan.borders["z_max"],
                   )