from app.scan.filters.ScanFilterABC import ScanFilterABC


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
