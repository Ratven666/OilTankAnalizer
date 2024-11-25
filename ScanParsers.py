from abc import ABC, abstractmethod

from Points import ScanPoint


class ScanParserABC(ABC):

    def __init__(self, file_path):
        self.file_path = file_path

    @abstractmethod
    def parse(self, scan):
        pass


class ScanParserFormTxt(ScanParserABC):
    def parse(self, scan):
        with open(self.file_path, "rt", encoding="UTF-8") as file:
            for line in file:
                line = line.strip().split()
                xyz = [float(xyz_) for xyz_ in line[:3]]
                rgb = list(map(int, line[3:6]))
                point = ScanPoint(x=xyz[0], y=xyz[1], z=xyz[2], color=rgb)
                scan.add_point(point)


class ScanParserFormLaz(ScanParserABC):
    def parse(self, scan):
        raise NotImplementedError
