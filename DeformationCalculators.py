from abc import ABC, abstractmethod

from Cylinder import Cylinder
from DeformationScan import DeformationScan


class DeformationCalculatorABC(ABC):

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def calculate(self, def_scan: DeformationScan):
        pass


class CylinderDeformationCalculator(DeformationCalculatorABC):

    def __init__(self, cylinder: Cylinder):
        self.cylinder = cylinder

    def calculate(self, def_scan):
        for point in def_scan:
            self.calculate_deformation(point)

    def calculate_deformation(self, point):
        point_r = ((point.x - self.cylinder.x0) ** 2 + (point.y - self.cylinder.y0) ** 2) ** 0.5
        deformation = point_r - self.cylinder.circle.r
        point.deformation = deformation
