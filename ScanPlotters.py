from abc import ABC, abstractmethod

from matplotlib import pyplot as plt


class ScanPlotterABC(ABC):

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def plot(self, scan):
        pass


class ScanPlotterMPL(ScanPlotterABC):

    def __init__(self, *args, **kwargs):
        pass

    def plot(self, scan):
        ax = plt.figure().add_subplot(projection="3d")
        x, y, z, c = [], [], [], []
        for point in scan:
            x.append(point.x)
            y.append(point.y)
            z.append(point.z)
            rgb = [rgb / 255 for rgb in point.color]
            c.append(rgb)
        ax.scatter(x, y, z, c=c)
        plt.axis('equal')
        plt.show()
