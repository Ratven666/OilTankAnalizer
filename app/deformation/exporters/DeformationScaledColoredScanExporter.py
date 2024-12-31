import math
from copy import deepcopy

from matplotlib import pyplot as plt
from matplotlib.colors import TwoSlopeNorm

from app.base.Cylinder import Cylinder
from app.deformation.FlatDeformationScan import FlatDeformationScan
from app.deformation.calculators.DeformationScan import DeformationScan
from app.scan.exporters.ScanExporterABC import ScanExporterABC
from app.scan.exporters.ScanExporterToTxt import ScanExporterToTxt


class DeformationScaledColoredScanExporter(ScanExporterABC):

    def __init__(self, file_path, def_scale=1, base_obj=None):
        super().__init__(file_path)
        self.def_scale = def_scale
        self.base_obj = base_obj
        self.def_scan = None

    def _init_point_colors_by_deformation(self):
        deformation = [point.deformation for point in self.def_scan]
        norm = TwoSlopeNorm(vcenter=0, vmin=min(deformation), vmax=max(deformation))
        colors = plt.cm.seismic(norm(deformation))
        for idx, point in enumerate(self.def_scan):
            color = [int(rgb * 255) for rgb in colors[idx][:3]]
            point.color = color

    def _calc_cylinder_scaled_point(self, point):
        azimuth = math.atan2(point.y - self.base_obj.y0,
                             point.x - self.base_obj.x0)
        dx = point.deformation * math.cos(azimuth) * self.def_scale
        dy = point.deformation * math.sin(azimuth) * self.def_scale
        point.x = point.x + dx
        point.y = point.y + dy

    def _calk_flat_scaled_point(self, point):
        point.z = point.deformation * self.def_scale

    def _calk_scaled_scan(self):
        if isinstance(self.def_scan, FlatDeformationScan):
            scaler_func = self._calk_flat_scaled_point
        elif isinstance(self.base_obj, Cylinder):
            scaler_func = self._calc_cylinder_scaled_point
        else:
            return
        for point in self.def_scan:
            scaler_func(point)

    def export(self, scan: DeformationScan):
        self.def_scan = deepcopy(scan)
        self._init_point_colors_by_deformation()
        self._calk_scaled_scan()
        self.def_scan.export_data_to_file(exporter=ScanExporterToTxt, file_path=self.file_path)
