from abc import ABC, abstractmethod


class PointsABC(ABC):
    @abstractmethod
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z


class Point(PointsABC):

    def __init__(self, x, y, z):
        self.x = self.check_coordinates(x)
        self.y = self.check_coordinates(y)
        self.z = self.check_coordinates(z)

    def check_coordinates(self, coord):
        if type(coord) == int:
            return float(coord)
        elif type(coord) == float:
            return coord
        else:
            raise ValueError(f"Координата - {coord} - не число ({type(coord)})!")

    def __str__(self):
        return f"Point (x={self.x}, y={self.y}, z={self.z})"


class NamedPoint(PointsABC):
    _names = []

    def __init__(self, x, y, z, name=None):
        self.point = Point(x=x, y=y, z=z)
        self.name = self._check_name(name)

    def _check_name(self, name):
        if name is None:
            return name
        else:
            if name in self._names:
                raise ValueError("Точка с таким иенем уже есть!")
            else:
                self._names.append(name)
                return name

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    @property
    def z(self):
        return self.point.z

    def __str__(self):
        if self.name is None:
            return str(self.point)
        return f"NamedPoint (name={self.name}, x={self.x}, y={self.y}, z={self.z})"


class ScanPoint(PointsABC):

    def __init__(self, x, y, z, color=(0, 0, 0)):
        self.point = Point(x=x, y=y, z=z)
        self.color = color

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    @property
    def z(self):
        return self.point.z

    def __str__(self):
        return f"ScanPoint (x={self.x}, y={self.y}, z={self.z}, color={self.color})"


class DeformationPoint(ScanPoint):

    def __init__(self, x, y, z, color=(0, 0, 0)):
        super().__init__(x, y, z, color)
        self.deformation = None

    @classmethod
    def create_def_point_from_point(cls, point: PointsABC):
        if isinstance(point, ScanPoint):
            return cls(x=point.x, y=point.y, z=point.z, color=point.color)
        elif isinstance(point, PointsABC):
            return cls(x=point.x, y=point.y, z=point.z)
        else:
            raise ValueError(f"Должен быть объект класса Point, передан {point.__class__}")

    def __str__(self):
        return (f"DeformationPoint (x={self.x}, y={self.y}, z={self.z}, "
                f"deformation={self.deformation:.4f}, "
                f"color={self.color})")


if __name__ == "__main__":

    p1 = Point(12, 20, 30.6)
    np1 = NamedPoint(13, 45, 23, name="np1")
    np2 = NamedPoint(45, 23, 34)

    sp1 = ScanPoint(123, 435, 23, color=[255, 234, 111])

    print(p1, np1, np2, sp1, sep="\n")

    print("*" * 50)

    for point in [p1, np1, np2, sp1]:
        print(isinstance(point, PointsABC), point)
