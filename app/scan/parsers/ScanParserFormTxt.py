from app.scan.ScanPoint import ScanPoint
from app.scan.parsers.ScanParserABC import ScanParserABC


class ScanParserFormTxt(ScanParserABC):
    def parse(self, scan):
        with open(self.file_path, "rt", encoding="UTF-8") as file:
            for line in file:
                line = line.strip().split()
                xyz = [float(xyz_) for xyz_ in line[:3]]
                try:
                    rgb = list(map(int, line[3:6]))
                except ValueError:
                    rgb = (0, 0, 0)
                point = ScanPoint(x=xyz[0], y=xyz[1], z=xyz[2], color=rgb)
                scan.add_point(point)
