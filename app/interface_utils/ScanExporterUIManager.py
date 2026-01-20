import os

from app.base.Cylinder import Cylinder
from app.deformation.FlatDeformationScan import FlatDeformationScan
from app.deformation.DeformationScan import DeformationScan
from app.deformation.exporters.CircularSectionsDefScansExporterToDxf import CircularSectionsDefScansExporterToDxf
from app.deformation.exporters.DeformationScaledColoredScanExporter import DeformationScaledColoredScanExporter
from app.deformation.exporters.FlatDefScanContoursExporterToDxf import FlatDefScanContoursExporterToDxf
from app.deformation.exporters.HorizontalSectionFlatScanExporterToDxf import HorizontalSectionFlatScanExporterToDxf
from app.deformation.exporters.VerticalSectionsFlatScanExporterToDxf import VerticalSectionsFlatScanExporterToDxf


class ScanExporterUIManager:

    def __init__(self, saving_info_numbers_data: dict,
                 is_cylinder_isoline_exp: bool,
                 is_flat_isoline_exp: bool,
                 is_vertical_sections_exp: bool,
                 is_horizontal_sections_exp: bool,
                 is_base_cylinder_scaled_point_cloud_exp: bool,
                 is_flat_scaled_point_cloud_exp: bool,
                 scan_file_path: str,
                 cylinder: Cylinder,
                 def_scan: DeformationScan,
                 flat_def_scan: FlatDeformationScan):
        self.saving_info_numbers_data = saving_info_numbers_data
        self.is_cylinder_isoline_exp = is_cylinder_isoline_exp
        self.is_flat_isoline_exp = is_flat_isoline_exp
        self.is_vertical_sections_exp = is_vertical_sections_exp
        self.is_horizontal_sections_exp = is_horizontal_sections_exp
        self.is_base_cylinder_scaled_point_cloud_exp = is_base_cylinder_scaled_point_cloud_exp
        self.is_flat_scaled_point_cloud_exp = is_flat_scaled_point_cloud_exp
        self.scan_file_path = scan_file_path
        self.cylinder = cylinder
        self.def_scan = def_scan
        self.flat_def_scan = flat_def_scan
        self.base_file_path = os.path.dirname(self.scan_file_path)

    @staticmethod
    def __is_correct_data(data: dict):
        for value in data.values():
            if value is None:
                return False
        return True

    def _export_cylinder_isoline_dxf(self):
        data = {"d_cyl_isol": self.saving_info_numbers_data["Шаг изолиний на цилиндре, м"],
                "def_scale": self.saving_info_numbers_data["Масштаб для вывода деформаций"]}
        if self.__is_correct_data(data):
            self.flat_def_scan.export_data_to_file(exporter=CircularSectionsDefScansExporterToDxf,
                                                   file_path=self.base_file_path,
                                                   levels_step=data["d_cyl_isol"],
                                                   def_scale=data["def_scale"])
        else:
            return "BAD_CIRCULAR_ISOLINE_EXPORT_DATA"
        return "OK"

    def _export_flat_isoline_dxf(self):
        data = {"d_flat_isol": self.saving_info_numbers_data["Шаг изолиний на плоскости, м"],
                "def_scale": self.saving_info_numbers_data["Масштаб для вывода деформаций"]}
        if self.__is_correct_data(data):
            self.flat_def_scan.export_data_to_file(exporter=FlatDefScanContoursExporterToDxf,
                                                   file_path=self.base_file_path,
                                                   levels_step=data["d_flat_isol"],
                                                   def_scale=data["def_scale"])
        else:
            return "BAD_FLAT_ISOLINE_EXPORT_DATA"
        return "OK"

    def _export_horizontal_sections_dxf(self):
        data = {"level_step": self.saving_info_numbers_data["Шаг горизонтальных сечений, м"],
                "def_scale": self.saving_info_numbers_data["Масштаб для вывода деформаций"],
                }
        if self.__is_correct_data(data):
            data["z_min"] = self.saving_info_numbers_data["Z_min, м"]
            data["z_max"] = self.saving_info_numbers_data["Z_max, м"]
            self.flat_def_scan.export_data_to_file(exporter=HorizontalSectionFlatScanExporterToDxf,
                                                   file_path=self.base_file_path,
                                                   z0=data["z_min"],
                                                   z_max=data["z_max"],
                                                   levels_step=data["level_step"],
                                                   def_scale=data["def_scale"])
        else:
            return "BAD_HORIZONTAL_SECTIONS_EXPORT_DATA"
        return "OK"

    def _export_vertical_sections_dxf(self):
        data = {"start_azimuth": self.saving_info_numbers_data["Азимут_min, deg"],
                "end_azimuth": self.saving_info_numbers_data["Азимут_max, deg"],
                "count_of_section": self.saving_info_numbers_data["Количество сечений, шт"],
                "def_scale": self.saving_info_numbers_data["Масштаб для вывода деформаций"],
                }
        if self.__is_correct_data(data):
            self.flat_def_scan.export_data_to_file(exporter=VerticalSectionsFlatScanExporterToDxf,
                                                   file_path=self.base_file_path,
                                                   start_azimuth=data["start_azimuth"],
                                                   end_azimuth=data["end_azimuth"],
                                                   count_of_section=int(data["count_of_section"]),
                                                   def_scale=data["def_scale"])
        else:
            return "BAD_VERTICAL_SECTIONS_EXPORT_DATA"
        return "OK"

    def _export_base_cylinder_scaled_point_cloud(self):
        data = {"def_scale": self.saving_info_numbers_data["Масштаб для вывода деформаций"]}
        if self.__is_correct_data(data):
            self.def_scan.export_data_to_file(exporter=DeformationScaledColoredScanExporter,
                                              file_path=self.base_file_path,
                                              def_scale=data["def_scale"],
                                              base_obj=self.cylinder,
                                              )
        else:
            return "BAD_DEF_SCALE_EXPORT_DATA"
        return "OK"

    def _export_flat_scaled_point_cloud(self):
        data = {"def_scale": self.saving_info_numbers_data["Масштаб для вывода деформаций"]}
        if self.__is_correct_data(data):
            self.flat_def_scan.export_data_to_file(exporter=DeformationScaledColoredScanExporter,
                                                   file_path=self.base_file_path,
                                                   def_scale=data["def_scale"],
                                                   )
        else:
            return "BAD_DEF_SCALE_EXPORT_DATA"
        return "OK"

    def export_data(self):
        msg_set = set()
        if self.is_cylinder_isoline_exp:
            msg = self._export_cylinder_isoline_dxf()
            msg_set.add(msg)
        if self.is_flat_isoline_exp:
            msg = self._export_flat_isoline_dxf()
            msg_set.add(msg)
        if self.is_horizontal_sections_exp:
            msg = self._export_horizontal_sections_dxf()
            msg_set.add(msg)
        if self.is_vertical_sections_exp:
            msg = self._export_vertical_sections_dxf()
            msg_set.add(msg)
        if self.is_base_cylinder_scaled_point_cloud_exp:
            msg = self._export_base_cylinder_scaled_point_cloud()
            msg_set.add(msg)
        if self.is_flat_scaled_point_cloud_exp:
            msg = self._export_flat_scaled_point_cloud()
            msg_set.add(msg)
        return msg_set
