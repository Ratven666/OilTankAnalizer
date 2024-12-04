

class ScanExportersToTxt:

    def __init__(self, file_path):
        self.file_path = file_path

    def export(self, scan):
        with open(self.file_path, "w", encoding="UTF-8") as file:
            for point in scan:
                if point.color is None:
                    point_str = f"{point.x} {point.y} {point.z}\n"
                else:
                    point_str = f"{point.x} {point.y} {point.z} {point.color[0]} {point.color[1]} {point.color[2]}\n"
                file.write(point_str)