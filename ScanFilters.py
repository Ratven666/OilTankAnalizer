from abc import ABC, abstractmethod


class ScanFilterABC(ABC):

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def filter(self, scan):
        pass


class ScanDelimiter(ScanFilterABC):

    def __init__(self, delimiter):
        self.delimiter = delimiter
        self.counter = 0

    def filter(self, scan):
        point_lst = []
        for point in scan:
            if self.counter % self.delimiter == 0:
                point_lst.append(point)
            self.counter += 1
        return point_lst


class ScanFilterFromZminToZmax(ScanFilterABC):

    def __init__(self, z_min, z_max):
        self.z_min = z_min
        self.z_max = z_max

    def filter(self, scan):
        point_lst = []
        for point in scan:
            if self.z_min < point.z < self.z_max:
                point_lst.append(point)
        return point_lst


class ScanFilterFromCylinder(ScanFilterABC):

    def __init__(self, cylinder, tolerance=0.1, only_outside=False):
        self.cylinder = cylinder
        self.tolerance = tolerance
        self.only_outside = only_outside

    def filtered_function(self, point):
        point_r = ((point.x - self.cylinder.x0) ** 2 + (point.y - self.cylinder.y0) ** 2) ** 0.5
        dr = point_r - self.cylinder.circle.r
        if self.only_outside:
            return dr < self.tolerance
        return abs(dr) < self.tolerance

    def filter(self, scan):
        point_lst = []
        for point in scan:
            if self.filtered_function((point)):
                point_lst.append(point)
        return point_lst


