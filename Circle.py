import numpy as np


class Circle:

    def __init__(self, x0, y0, r):
        self.x0 = x0
        self.y0 = y0
        self.r = r

    def __str__(self):
        return f"Circle (center=({self.x0:.4f}, {self.y0:.4f}), R={self.r:.4f})"

    def _get_a_matrix(self, scan):
        a_lst = []
        for point in scan:
            r = ((point.x - self.x0) ** 2 + (point.y - self.y0) ** 2) ** 0.5
            a = -(point.x - self.x0) / r
            b = -(point.y - self.y0) / r
            c = -1
            a_lst.append([a, b, c])
        return np.array(a_lst)

    def _get_l_vector(self, scan):
        l_vct = []
        for point in scan:
            r = ((point.x - self.x0) ** 2 + (point.y - self.y0) ** 2) ** 0.5
            l = r - self.r
            l_vct.append([l])
        return np.array(l_vct)

    def _get_dt(self, scan):
        a = self._get_a_matrix(scan)
        l = self._get_l_vector(scan)
        n = a.T @ a
        q = np.linalg.inv(n)
        t = -q @ a.T @ l
        return t

    def best_fit_circle_in_scan(self, scan, max_iteration=50, max_tolerance=1e-4, print_log=True):
        for i in range(max_iteration):
            t = self._get_dt(scan)
            self.x0 += t[0][0]
            self.y0 += t[1][0]
            self.r += t[2][0]
            if print_log:
                print("*" * 25, f"iteration - {i}","*" * 25)
                print(t.T)
                print(self)
            if abs(max(t)[0]) < max_tolerance:
                break


