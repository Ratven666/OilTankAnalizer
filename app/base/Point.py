class Point:

    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"Point (x={self.x}, y={self.y}, z={self.z})"
