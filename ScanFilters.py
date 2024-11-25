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
