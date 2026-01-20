from app.scan.filters.ScanFilterABC import ScanFilterABC


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
