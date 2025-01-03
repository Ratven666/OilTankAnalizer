import sys
import time
from pathlib import Path

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QWidget, QApplication, QFileDialog, QMessageBox

from app.deformation.DeformationScan import DeformationScan
from app.deformation.FlatDeformationScan import FlatDeformationScan
from app.deformation.calculators.CylinderDeformationCalculator import CylinderDeformationCalculator
from app.interface_utils.CylinderUICreator import CylinderUICreator
from app.interface_utils.ScanExporterUIManager import ScanExporterUIManager
from app.interface_utils.ScanUICreator import ScanUICreator


class Ui_OilTankAnalizer(QWidget):

    def __init__(self):
        super().__init__()
        self.setupUi()
        self.base_filepath = None
        self.cylinder_numbers_data = None
        self.filtering_numbers_data = None
        self.saving_info_numbers_data = None
        self.data_correct_flag = None

        self.file_path_button.clicked.connect(self.open_file_dialog_base_filepath)
        self.file_path_text.textChanged.connect(self.base_filepath_from_text_line)

        self.cb_use_base_cyl.stateChanged.connect(self.update_cb_of_base_cylinder)
        self.cb_fit_base_cyl.stateChanged.connect(self.update_cb_of_fit_cylinder)
        self.cb_filter_scan_by_z_limits.stateChanged.connect(self.update_cb_filter_scan_by_z_limits)

        self.cb_filter_scan_decim_n.stateChanged.connect(self.update_cb_filter_scan_decim_n)
        self.cb_filter_scan_radius.stateChanged.connect(self.update_cb_filter_scan_radius)
        self.cb_filter_scan_by_z_limits_2.stateChanged.connect(self.update_cb_filter_scan_by_z_limits_2)

        self.cb_cylinder_izol_def.stateChanged.connect(self.update_cb_cylinder_izol_def)
        self.cb_flat_izol_def.stateChanged.connect(self.update_cb_flat_izol_def)
        self.cb_vert_section_def.stateChanged.connect(self.update_cb_vert_section_def)
        self.cb_hor_section_def.stateChanged.connect(self.update_cb_hor_section_def)

        self.progressBar.setEnabled(True)
        self.progressBar.setProperty("value", 0)
        self.start_button.clicked.connect(self.start_calculation)

    def start_calculation(self):
        self.start_button.setEnabled(False)
        self.progressBar.setProperty("value", 0)
        self.init_number_data()
        if self.data_correct_flag is False or self.data_correct_flag is None:
            self.start_button.setEnabled(True)
            self.textEdit_operation_log.setText(f"Расчет прерван!")
            return
        print(f"Идет расчет базового цилиндра")
        self.textEdit_operation_log.setText(f"Идет расчет базового цилиндра")
        self.progressBar.setProperty("value", 5)
        cylinder, msg = CylinderUICreator(cylinder_numbers_data=self.cylinder_numbers_data,
                                          is_use_base_cylinder=self.cb_use_base_cyl.isChecked(),
                                          is_fit_cylinder=self.cb_fit_base_cyl.isChecked(),
                                          is_use_points_in_z_limits=self.cb_filter_scan_by_z_limits.isChecked(),
                                          save_cylinder_log=self.cb_save_cylinder_log.isChecked(),
                                          scan_file_path=self.base_filepath).get_cylinder()
        if cylinder is None:
            QMessageBox.critical(self, "Ошибка",
                                 f"Переданы некорректные данные для построения базового цилиндра - {msg}!")
            self.textEdit_operation_log.setText(f"Расчет прерван!")
            self.start_button.setEnabled(True)
            return
        self.progressBar.setProperty("value", 30)
        print(f"Идет расчет скана")
        self.textEdit_operation_log.setText(f"Идет расчет скана")
        time.sleep(0.5)
        scan, msg = ScanUICreator(filtering_numbers_data=self.filtering_numbers_data,
                                  cylinder=cylinder,
                                  is_scan_decimating=self.cb_filter_scan_decim_n.isChecked(),
                                  is_scan_filtering_by_radius=self.cb_filter_scan_radius.isChecked(),
                                  is_scan_filtering_by_z_limits=self.cb_filter_scan_by_z_limits_2.isChecked(),
                                  scan_file_path=self.base_filepath).init_scan()
        if scan is None:
            QMessageBox.critical(self, "Ошибка",
                                 f"Переданы некорректные данные для расчета скана - {msg}!")
            self.textEdit_operation_log.setText(f"Расчет прерван!")
            self.start_button.setEnabled(True)
            return
        self.progressBar.setProperty("value", 50)
        def_scan = DeformationScan.create_def_scan_from_scan(scan=scan)
        def_scan.calculate_deformation(deformation_calculator=CylinderDeformationCalculator,
                                       cylinder=cylinder)
        flat_def_scan = FlatDeformationScan.create_flat_def_scan_from_cylinder_def_scan(def_scan=def_scan,
                                                                                        cylinder=cylinder)
        def_scan.name = scan.name
        flat_def_scan.name = scan.name
        self.progressBar.setProperty("value", 70)
        msg_set = ScanExporterUIManager(saving_info_numbers_data=self.saving_info_numbers_data,
                                        is_cylinder_isoline_exp=self.cb_cylinder_izol_def.isChecked(),
                                        is_flat_isoline_exp=self.cb_flat_izol_def.isChecked(),
                                        is_vertical_sections_exp=self.cb_vert_section_def.isChecked(),
                                        is_horizontal_sections_exp=self.cb_hor_section_def.isChecked(),
                                        is_base_cylinder_scaled_point_cloud_exp=self.cb_save_def_pc.isChecked(),
                                        is_flat_scaled_point_cloud_exp=self.cb_save_flat_def_pc.isChecked(),
                                        scan_file_path=self.base_filepath,
                                        cylinder=cylinder,
                                        def_scan=def_scan,
                                        flat_def_scan=flat_def_scan).export_data()
        if len(msg_set) > 1:
            for msg in msg_set:
                if msg != "OK":
                    QMessageBox.critical(self, "Ошибка",
                                         f"Переданы некорректные данные для экспорта данных - {msg}!")
                    self.textEdit_operation_log.setText(f"Расчет прерван!")
                    self.start_button.setEnabled(True)
                    return
        self.progressBar.setProperty("value", 100)
        self.textEdit_operation_log.setText(f"Расчет закончен!")
        self.start_button.setEnabled(True)

    def init_number_data(self):
        self.cylinder_numbers_data = self.extract_numbers(text_browsers={"X, м": self.pt_bc_x,
                                                                         "Y, м": self.pt_bc_y,
                                                                         "Z, м": self.pt_bc_z,
                                                                         "R, м": self.pt_bc_r,
                                                                         "H, м": self.pt_bc_h,
                                                                         "Z_min, м": self.pt_bc_fit_cyl_z_min,
                                                                         "Z_max, м": self.pt_bc_fit_cyl_z_max,
                                                                         })
        if self.data_correct_flag is True:
            self.filtering_numbers_data = self.extract_numbers(text_browsers={"N, раз": self.pt_filter_decim_n,
                                                                              "dR, м": self.pt_filter_radius,
                                                                              "Z_min, м": self.pt_filter_cyl_z_min,
                                                                              "Z_max, м": self.pt_filter_cyl_z_max,
                                                                              })
        else:
            return
        if self.data_correct_flag is True:
            self.saving_info_numbers_data = self.extract_numbers(text_browsers={"Масштаб для вывода деформаций":
                                                                                self.pt_def_scale,
                                                                            "Шаг изолиний на цилиндре, м":
                                                                                self.pt_cyl_izol_step,
                                                                            "Шаг изолиний на плоскости, м":
                                                                                self.pt_flat_izol_step,
                                                                            "Азимут_min, deg":
                                                                                self.pt_vert_section_az_min,
                                                                            "Азимут_max, deg":
                                                                                self.pt_vert_section_az_max,
                                                                            "Количество сечений, шт":
                                                                                self.pt_vert_section_count,
                                                                            "Z_min, м": self.pt_hor_section_z_min,
                                                                            "Z_max, м": self.pt_hor_section_z_max,
                                                                            "Шаг горизонтальных сечений, м":
                                                                                self.pt_hor_section_step,
                                                                            })

    def extract_numbers(self, text_browsers: dict):
        for label, text_br in text_browsers.items():
            text = text_br.toPlainText()
            try:
                if text == "":
                    text_browsers[label] = None
                    continue
                text = text.replace(",", ".")
                number = float(text)
                text_browsers[label] = number
            except:
                self.data_correct_flag = False
                QMessageBox.critical(self, "Ошибка", f"В поле \"{label}\" не число, а \"{text}\"!")
                return None
        self.data_correct_flag = True
        return text_browsers

    def open_file_dialog_base_filepath(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            "Select a File",
            ".",
            "PointCloud (*.txt *.ascii *.las)"
        )
        if filename:
            path = Path(filename)
            self.file_path_text.setText(str(filename))
            self.base_filepath = str(path)

    def base_filepath_from_text_line(self):
        self.base_filepath = self.file_path_text.toPlainText()
        if self.base_filepath:
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)

    def update_cb_of_base_cylinder(self, state):
        filds = [self.label_bc_x, self.label_bc_y, self.label_bc_z,
                 self.label_bc_r, self.label_bc_h, self.pt_bc_x,
                 self.pt_bc_y, self.pt_bc_z, self.pt_bc_r, self.pt_bc_h]
        if state == 2:
            self.cb_fit_base_cyl.setChecked(False)
            for fild in filds:
                fild.setEnabled(True)
        else:
            self.cb_fit_base_cyl.setChecked(True)
            for fild in filds:
                fild.setEnabled(False)

    def update_cb_of_fit_cylinder(self, state):
        if state == 2:
            self.cb_use_base_cyl.setChecked(False)
            self.cb_filter_scan_by_z_limits.setEnabled(True)
            self.cb_save_cylinder_log.setEnabled(True)
            if self.cb_filter_scan_by_z_limits.isChecked():
                self.pt_bc_fit_cyl_z_min.setEnabled(True)
                self.pt_bc_fit_cyl_z_max.setEnabled(True)
                self.label_z_min.setEnabled(True)
                self.label_z_max.setEnabled(True)
        else:
            self.cb_use_base_cyl.setChecked(True)
            self.cb_filter_scan_by_z_limits.setEnabled(False)
            self.cb_save_cylinder_log.setEnabled(False)
            self.pt_bc_fit_cyl_z_min.setEnabled(False)
            self.pt_bc_fit_cyl_z_max.setEnabled(False)
            self.label_z_min.setEnabled(False)
            self.label_z_max.setEnabled(False)

    def update_cb_filter_scan_by_z_limits(self, state):
        if state == 2:
            self.label_z_min.setEnabled(True)
            self.label_z_max.setEnabled(True)
            self.pt_bc_fit_cyl_z_min.setEnabled(True)
            self.pt_bc_fit_cyl_z_max.setEnabled(True)
        else:
            self.label_z_min.setEnabled(False)
            self.label_z_max.setEnabled(False)
            self.pt_bc_fit_cyl_z_min.setEnabled(False)
            self.pt_bc_fit_cyl_z_max.setEnabled(False)

    def update_cb_filter_scan_decim_n(self, state):
        if state == 2:
            self.label_filter_decim_n.setEnabled(True)
            self.pt_filter_decim_n.setEnabled(True)
        else:
            self.label_filter_decim_n.setEnabled(False)
            self.pt_filter_decim_n.setEnabled(False)

    def update_cb_filter_scan_radius(self, state):
        if state == 2:
            self.label_filter_radius.setEnabled(True)
            self.pt_filter_radius.setEnabled(True)
        else:
            self.label_filter_radius.setEnabled(False)
            self.pt_filter_radius.setEnabled(False)

    def update_cb_filter_scan_by_z_limits_2(self, state):
        if state == 2:
            self.label_filter_cyl_z_min.setEnabled(True)
            self.label_filter_cyl_z_max.setEnabled(True)
            self.pt_filter_cyl_z_min.setEnabled(True)
            self.pt_filter_cyl_z_max.setEnabled(True)
        else:
            self.label_filter_cyl_z_min.setEnabled(False)
            self.label_filter_cyl_z_max.setEnabled(False)
            self.pt_filter_cyl_z_min.setEnabled(False)
            self.pt_filter_cyl_z_max.setEnabled(False)

    def update_cb_cylinder_izol_def(self, state):
        if state == 2:
            self.label_cyl_izol_step.setEnabled(True)
            self.pt_cyl_izol_step.setEnabled(True)
        else:
            self.label_cyl_izol_step.setEnabled(False)
            self.pt_cyl_izol_step.setEnabled(False)

    def update_cb_flat_izol_def(self, state):
        if state == 2:
            self.label_flat_izol_step.setEnabled(True)
            self.pt_flat_izol_step.setEnabled(True)
        else:
            self.label_flat_izol_step.setEnabled(False)
            self.pt_flat_izol_step.setEnabled(False)

    def update_cb_vert_section_def(self, state):
        if state == 2:
            self.label_vert_section_az_min.setEnabled(True)
            self.label_vert_section_az_max.setEnabled(True)
            self.label_vert_section_count.setEnabled(True)
            self.pt_vert_section_az_min.setEnabled(True)
            self.pt_vert_section_az_max.setEnabled(True)
            self.pt_vert_section_count.setEnabled(True)
        else:
            self.label_vert_section_az_min.setEnabled(False)
            self.label_vert_section_az_max.setEnabled(False)
            self.label_vert_section_count.setEnabled(False)
            self.pt_vert_section_az_min.setEnabled(False)
            self.pt_vert_section_az_max.setEnabled(False)
            self.pt_vert_section_count.setEnabled(False)

    def update_cb_hor_section_def(self, state):
        if state == 2:
            self.label_hor_section_z_min.setEnabled(True)
            self.label_hor_section_z_max.setEnabled(True)
            self.label_hor_section_step.setEnabled(True)
            self.pt_hor_section_z_min.setEnabled(True)
            self.pt_hor_section_z_max.setEnabled(True)
            self.pt_hor_section_step.setEnabled(True)
        else:
            self.label_hor_section_z_min.setEnabled(False)
            self.label_hor_section_z_max.setEnabled(False)
            self.label_hor_section_step.setEnabled(False)
            self.pt_hor_section_z_min.setEnabled(False)
            self.pt_hor_section_z_max.setEnabled(False)
            self.pt_hor_section_step.setEnabled(False)

    def setupUi(self):
        self.setObjectName("OilTankAnalizer")
        self.resize(781, 818)
        self.setMinimumSize(QtCore.QSize(781, 818))
        self.setMaximumSize(QtCore.QSize(781, 818))
        self.verticalLayoutWidget_12 = QtWidgets.QWidget(parent=self)
        self.verticalLayoutWidget_12.setGeometry(QtCore.QRect(10, 10, 764, 798))
        self.verticalLayoutWidget_12.setObjectName("verticalLayoutWidget_12")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_12)
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.file_path_text = QtWidgets.QTextEdit(parent=self.verticalLayoutWidget_12)
        self.file_path_text.setMinimumSize(QtCore.QSize(0, 20))
        self.file_path_text.setMaximumSize(QtCore.QSize(16777215, 25))
        self.file_path_text.setObjectName("file_path_text")
        self.gridLayout.addWidget(self.file_path_text, 0, 1, 1, 1)
        self.Label_scan_name = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.Label_scan_name.setMaximumSize(QtCore.QSize(16777215, 100))
        self.Label_scan_name.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.Label_scan_name.setObjectName("Label_scan_name")
        self.gridLayout.addWidget(self.Label_scan_name, 0, 0, 1, 1)
        self.file_path_button = QtWidgets.QToolButton(parent=self.verticalLayoutWidget_12)
        self.file_path_button.setObjectName("file_path_button")
        self.gridLayout.addWidget(self.file_path_button, 0, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.line_7 = QtWidgets.QFrame(parent=self.verticalLayoutWidget_12)
        self.line_7.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_7.setObjectName("line_7")
        self.verticalLayout.addWidget(self.line_7)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_bc_h = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_bc_h.setEnabled(False)
        self.label_bc_h.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_bc_h.setObjectName("label_bc_h")
        self.gridLayout_4.addWidget(self.label_bc_h, 1, 2, 1, 1)
        self.label_bc_z = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_bc_z.setEnabled(False)
        self.label_bc_z.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_bc_z.setObjectName("label_bc_z")
        self.gridLayout_4.addWidget(self.label_bc_z, 2, 0, 1, 1)
        self.label_bc_y = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_bc_y.setEnabled(False)
        self.label_bc_y.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_bc_y.setObjectName("label_bc_y")
        self.gridLayout_4.addWidget(self.label_bc_y, 1, 0, 1, 1)
        self.label_bc_r = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_bc_r.setEnabled(False)
        self.label_bc_r.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_bc_r.setObjectName("label_bc_r")
        self.gridLayout_4.addWidget(self.label_bc_r, 0, 2, 1, 1)
        self.label_bc_x = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_bc_x.setEnabled(False)
        self.label_bc_x.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_bc_x.setObjectName("label_bc_x")
        self.gridLayout_4.addWidget(self.label_bc_x, 0, 0, 1, 1)
        self.pt_bc_x = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_bc_x.setEnabled(False)
        self.pt_bc_x.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_bc_x.setObjectName("pt_bc_x")
        self.gridLayout_4.addWidget(self.pt_bc_x, 0, 1, 1, 1)
        self.pt_bc_y = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_bc_y.setEnabled(False)
        self.pt_bc_y.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_bc_y.setObjectName("pt_bc_y")
        self.gridLayout_4.addWidget(self.pt_bc_y, 1, 1, 1, 1)
        self.pt_bc_z = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_bc_z.setEnabled(False)
        self.pt_bc_z.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_bc_z.setObjectName("pt_bc_z")
        self.gridLayout_4.addWidget(self.pt_bc_z, 2, 1, 1, 1)
        self.pt_bc_r = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_bc_r.setEnabled(False)
        self.pt_bc_r.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_bc_r.setObjectName("pt_bc_r")
        self.gridLayout_4.addWidget(self.pt_bc_r, 0, 3, 1, 1)
        self.pt_bc_h = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_bc_h.setEnabled(False)
        self.pt_bc_h.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_bc_h.setObjectName("pt_bc_h")
        self.gridLayout_4.addWidget(self.pt_bc_h, 1, 3, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_4, 1, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.cb_use_base_cyl = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_use_base_cyl.setEnabled(True)
        self.cb_use_base_cyl.setChecked(False)
        self.cb_use_base_cyl.setObjectName("cb_use_base_cyl")
        self.horizontalLayout_5.addWidget(self.cb_use_base_cyl)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.gridLayout_3.addLayout(self.horizontalLayout_5, 0, 0, 1, 1)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem2)
        self.cb_fit_base_cyl = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_fit_base_cyl.setEnabled(True)
        self.cb_fit_base_cyl.setChecked(True)
        self.cb_fit_base_cyl.setObjectName("cb_fit_base_cyl")
        self.horizontalLayout_6.addWidget(self.cb_fit_base_cyl)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem3)
        self.gridLayout_3.addLayout(self.horizontalLayout_6, 0, 2, 1, 1)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout_4.addLayout(self.horizontalLayout_8)
        self.cb_filter_scan_by_z_limits = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_filter_scan_by_z_limits.setEnabled(True)
        self.cb_filter_scan_by_z_limits.setObjectName("cb_filter_scan_by_z_limits")
        self.verticalLayout_4.addWidget(self.cb_filter_scan_by_z_limits)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_z_min = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_z_min.setEnabled(True)
        self.label_z_min.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_z_min.setObjectName("label_z_min")
        self.horizontalLayout_9.addWidget(self.label_z_min)
        self.pt_bc_fit_cyl_z_min = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_bc_fit_cyl_z_min.setEnabled(False)
        self.pt_bc_fit_cyl_z_min.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_bc_fit_cyl_z_min.setObjectName("pt_bc_fit_cyl_z_min")
        self.horizontalLayout_9.addWidget(self.pt_bc_fit_cyl_z_min)
        self.label_z_max = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_z_max.setEnabled(True)
        self.label_z_max.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_z_max.setObjectName("label_z_max")
        self.horizontalLayout_9.addWidget(self.label_z_max)
        self.pt_bc_fit_cyl_z_max = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_bc_fit_cyl_z_max.setEnabled(False)
        self.pt_bc_fit_cyl_z_max.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_bc_fit_cyl_z_max.setObjectName("pt_bc_fit_cyl_z_max")
        self.horizontalLayout_9.addWidget(self.pt_bc_fit_cyl_z_max)
        self.verticalLayout_4.addLayout(self.horizontalLayout_9)
        self.cb_save_cylinder_log = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_save_cylinder_log.setEnabled(True)
        self.cb_save_cylinder_log.setChecked(True)
        self.cb_save_cylinder_log.setObjectName("cb_save_cylinder_log")
        self.verticalLayout_4.addWidget(self.cb_save_cylinder_log)
        self.gridLayout_3.addLayout(self.verticalLayout_4, 1, 2, 1, 1)
        self.line_2 = QtWidgets.QFrame(parent=self.verticalLayoutWidget_12)
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_3.addWidget(self.line_2, 1, 1, 1, 1)
        self.line_3 = QtWidgets.QFrame(parent=self.verticalLayoutWidget_12)
        self.line_3.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout_3.addWidget(self.line_3, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)
        self.verticalLayout_12.addLayout(self.verticalLayout)
        self.line_5 = QtWidgets.QFrame(parent=self.verticalLayoutWidget_12)
        self.line_5.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_5.setObjectName("line_5")
        self.verticalLayout_12.addWidget(self.line_5)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.label_filter_major = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_filter_major.setObjectName("label_filter_major")
        self.horizontalLayout.addWidget(self.label_filter_major)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.cb_filter_scan_decim_n = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_filter_scan_decim_n.setEnabled(True)
        self.cb_filter_scan_decim_n.setObjectName("cb_filter_scan_decim_n")
        self.verticalLayout_3.addWidget(self.cb_filter_scan_decim_n)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_filter_decim_n = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_filter_decim_n.setEnabled(False)
        self.label_filter_decim_n.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_filter_decim_n.setObjectName("label_filter_decim_n")
        self.horizontalLayout_2.addWidget(self.label_filter_decim_n)
        self.pt_filter_decim_n = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_filter_decim_n.setEnabled(False)
        self.pt_filter_decim_n.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_filter_decim_n.setObjectName("pt_filter_decim_n")
        self.horizontalLayout_2.addWidget(self.pt_filter_decim_n)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.line = QtWidgets.QFrame(parent=self.verticalLayoutWidget_12)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_4.addWidget(self.line)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.cb_filter_scan_radius = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_filter_scan_radius.setEnabled(True)
        self.cb_filter_scan_radius.setObjectName("cb_filter_scan_radius")
        self.verticalLayout_5.addWidget(self.cb_filter_scan_radius)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_filter_radius = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_filter_radius.setEnabled(False)
        self.label_filter_radius.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_filter_radius.setObjectName("label_filter_radius")
        self.horizontalLayout_3.addWidget(self.label_filter_radius)
        self.pt_filter_radius = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_filter_radius.setEnabled(False)
        self.pt_filter_radius.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_filter_radius.setObjectName("pt_filter_radius")
        self.horizontalLayout_3.addWidget(self.pt_filter_radius)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4.addLayout(self.verticalLayout_5)
        self.line_4 = QtWidgets.QFrame(parent=self.verticalLayoutWidget_12)
        self.line_4.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_4.setObjectName("line_4")
        self.horizontalLayout_4.addWidget(self.line_4)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.cb_filter_scan_by_z_limits_2 = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_filter_scan_by_z_limits_2.setEnabled(True)
        self.cb_filter_scan_by_z_limits_2.setObjectName("cb_filter_scan_by_z_limits_2")
        self.verticalLayout_6.addWidget(self.cb_filter_scan_by_z_limits_2)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pt_filter_cyl_z_min = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_filter_cyl_z_min.setEnabled(False)
        self.pt_filter_cyl_z_min.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_filter_cyl_z_min.setObjectName("pt_filter_cyl_z_min")
        self.gridLayout_2.addWidget(self.pt_filter_cyl_z_min, 0, 1, 1, 1)
        self.label_filter_cyl_z_min = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_filter_cyl_z_min.setEnabled(False)
        self.label_filter_cyl_z_min.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_filter_cyl_z_min.setObjectName("label_filter_cyl_z_min")
        self.gridLayout_2.addWidget(self.label_filter_cyl_z_min, 0, 0, 1, 1)
        self.label_filter_cyl_z_max = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_filter_cyl_z_max.setEnabled(False)
        self.label_filter_cyl_z_max.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_filter_cyl_z_max.setObjectName("label_filter_cyl_z_max")
        self.gridLayout_2.addWidget(self.label_filter_cyl_z_max, 1, 0, 1, 1)
        self.pt_filter_cyl_z_max = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_filter_cyl_z_max.setEnabled(False)
        self.pt_filter_cyl_z_max.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_filter_cyl_z_max.setObjectName("pt_filter_cyl_z_max")
        self.gridLayout_2.addWidget(self.pt_filter_cyl_z_max, 1, 1, 1, 1)
        self.verticalLayout_6.addLayout(self.gridLayout_2)
        self.horizontalLayout_4.addLayout(self.verticalLayout_6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.verticalLayout_12.addLayout(self.verticalLayout_2)
        self.line_6 = QtWidgets.QFrame(parent=self.verticalLayoutWidget_12)
        self.line_6.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_6.setObjectName("line_6")
        self.verticalLayout_12.addWidget(self.line_6)
        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem6)
        self.label_saving_information = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_saving_information.setObjectName("label_saving_information")
        self.horizontalLayout_10.addWidget(self.label_saving_information)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem7)
        self.verticalLayout_11.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_def_scale = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_def_scale.setEnabled(True)
        self.label_def_scale.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_def_scale.setObjectName("label_def_scale")
        self.horizontalLayout_11.addWidget(self.label_def_scale)
        self.pt_def_scale = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_def_scale.setEnabled(True)
        self.pt_def_scale.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_def_scale.setObjectName("pt_def_scale")
        self.horizontalLayout_11.addWidget(self.pt_def_scale)
        self.verticalLayout_11.addLayout(self.horizontalLayout_11)
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.cb_vert_section_def = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_vert_section_def.setEnabled(True)
        self.cb_vert_section_def.setObjectName("cb_vert_section_def")
        self.verticalLayout_10.addWidget(self.cb_vert_section_def)
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_vert_section_az_max = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_vert_section_az_max.setEnabled(False)
        self.label_vert_section_az_max.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_vert_section_az_max.setObjectName("label_vert_section_az_max")
        self.gridLayout_6.addWidget(self.label_vert_section_az_max, 1, 0, 1, 1)
        self.pt_vert_section_az_max = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_vert_section_az_max.setEnabled(False)
        self.pt_vert_section_az_max.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_vert_section_az_max.setObjectName("pt_vert_section_az_max")
        self.gridLayout_6.addWidget(self.pt_vert_section_az_max, 1, 1, 1, 1)
        self.label_vert_section_az_min = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_vert_section_az_min.setEnabled(False)
        self.label_vert_section_az_min.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_vert_section_az_min.setObjectName("label_vert_section_az_min")
        self.gridLayout_6.addWidget(self.label_vert_section_az_min, 0, 0, 1, 1)
        self.pt_vert_section_az_min = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_vert_section_az_min.setEnabled(False)
        self.pt_vert_section_az_min.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_vert_section_az_min.setObjectName("pt_vert_section_az_min")
        self.gridLayout_6.addWidget(self.pt_vert_section_az_min, 0, 1, 1, 1)
        self.label_vert_section_count = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_vert_section_count.setEnabled(False)
        self.label_vert_section_count.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_vert_section_count.setObjectName("label_vert_section_count")
        self.gridLayout_6.addWidget(self.label_vert_section_count, 2, 0, 1, 1)
        self.pt_vert_section_count = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_vert_section_count.setEnabled(False)
        self.pt_vert_section_count.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_vert_section_count.setObjectName("pt_vert_section_count")
        self.gridLayout_6.addWidget(self.pt_vert_section_count, 2, 1, 1, 1)
        self.verticalLayout_10.addLayout(self.gridLayout_6)
        self.gridLayout_7.addLayout(self.verticalLayout_10, 1, 0, 1, 1)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.cb_cylinder_izol_def = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_cylinder_izol_def.setEnabled(True)
        self.cb_cylinder_izol_def.setObjectName("cb_cylinder_izol_def")
        self.verticalLayout_7.addWidget(self.cb_cylinder_izol_def)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_cyl_izol_step = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_cyl_izol_step.setEnabled(False)
        self.label_cyl_izol_step.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_cyl_izol_step.setObjectName("label_cyl_izol_step")
        self.horizontalLayout_12.addWidget(self.label_cyl_izol_step)
        self.pt_cyl_izol_step = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_cyl_izol_step.setEnabled(False)
        self.pt_cyl_izol_step.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_cyl_izol_step.setObjectName("pt_cyl_izol_step")
        self.horizontalLayout_12.addWidget(self.pt_cyl_izol_step)
        self.verticalLayout_7.addLayout(self.horizontalLayout_12)
        self.gridLayout_7.addLayout(self.verticalLayout_7, 0, 0, 1, 1)
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.cb_hor_section_def = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_hor_section_def.setEnabled(True)
        self.cb_hor_section_def.setObjectName("cb_hor_section_def")
        self.verticalLayout_9.addWidget(self.cb_hor_section_def)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_hor_section_z_max = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_hor_section_z_max.setEnabled(False)
        self.label_hor_section_z_max.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_hor_section_z_max.setObjectName("label_hor_section_z_max")
        self.gridLayout_5.addWidget(self.label_hor_section_z_max, 1, 0, 1, 1)
        self.pt_hor_section_z_max = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_hor_section_z_max.setEnabled(False)
        self.pt_hor_section_z_max.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_hor_section_z_max.setObjectName("pt_hor_section_z_max")
        self.gridLayout_5.addWidget(self.pt_hor_section_z_max, 1, 1, 1, 1)
        self.label_hor_section_z_min = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_hor_section_z_min.setEnabled(False)
        self.label_hor_section_z_min.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_hor_section_z_min.setObjectName("label_hor_section_z_min")
        self.gridLayout_5.addWidget(self.label_hor_section_z_min, 0, 0, 1, 1)
        self.pt_hor_section_z_min = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_hor_section_z_min.setEnabled(False)
        self.pt_hor_section_z_min.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_hor_section_z_min.setObjectName("pt_hor_section_z_min")
        self.gridLayout_5.addWidget(self.pt_hor_section_z_min, 0, 1, 1, 1)
        self.label_hor_section_step = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_hor_section_step.setEnabled(False)
        self.label_hor_section_step.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_hor_section_step.setObjectName("label_hor_section_step")
        self.gridLayout_5.addWidget(self.label_hor_section_step, 2, 0, 1, 1)
        self.pt_hor_section_step = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_hor_section_step.setEnabled(False)
        self.pt_hor_section_step.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_hor_section_step.setObjectName("pt_hor_section_step")
        self.gridLayout_5.addWidget(self.pt_hor_section_step, 2, 1, 1, 1)
        self.verticalLayout_9.addLayout(self.gridLayout_5)
        self.gridLayout_7.addLayout(self.verticalLayout_9, 1, 1, 1, 1)
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.cb_flat_izol_def = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_flat_izol_def.setEnabled(True)
        self.cb_flat_izol_def.setObjectName("cb_flat_izol_def")
        self.verticalLayout_8.addWidget(self.cb_flat_izol_def)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_flat_izol_step = QtWidgets.QLabel(parent=self.verticalLayoutWidget_12)
        self.label_flat_izol_step.setEnabled(False)
        self.label_flat_izol_step.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label_flat_izol_step.setObjectName("label_flat_izol_step")
        self.horizontalLayout_13.addWidget(self.label_flat_izol_step)
        self.pt_flat_izol_step = QtWidgets.QPlainTextEdit(parent=self.verticalLayoutWidget_12)
        self.pt_flat_izol_step.setEnabled(False)
        self.pt_flat_izol_step.setMaximumSize(QtCore.QSize(79, 21))
        self.pt_flat_izol_step.setObjectName("pt_flat_izol_step")
        self.horizontalLayout_13.addWidget(self.pt_flat_izol_step)
        self.verticalLayout_8.addLayout(self.horizontalLayout_13)
        self.gridLayout_7.addLayout(self.verticalLayout_8, 0, 1, 1, 1)
        self.cb_save_flat_def_pc = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_save_flat_def_pc.setEnabled(True)
        self.cb_save_flat_def_pc.setObjectName("cb_save_flat_def_pc")
        self.gridLayout_7.addWidget(self.cb_save_flat_def_pc, 2, 1, 1, 1)
        self.cb_save_def_pc = QtWidgets.QCheckBox(parent=self.verticalLayoutWidget_12)
        self.cb_save_def_pc.setEnabled(True)
        self.cb_save_def_pc.setObjectName("cb_save_def_pc")
        self.gridLayout_7.addWidget(self.cb_save_def_pc, 2, 0, 1, 1)
        self.verticalLayout_11.addLayout(self.gridLayout_7)
        self.verticalLayout_12.addLayout(self.verticalLayout_11)
        self.textEdit_operation_log = QtWidgets.QTextEdit(parent=self.verticalLayoutWidget_12)
        self.textEdit_operation_log.setMaximumSize(QtCore.QSize(16777215, 31))
        self.textEdit_operation_log.setObjectName("textEdit_operation_log")
        self.verticalLayout_12.addWidget(self.textEdit_operation_log)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.progressBar = QtWidgets.QProgressBar(parent=self.verticalLayoutWidget_12)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout_7.addWidget(self.progressBar)
        self.start_button = QtWidgets.QPushButton(parent=self.verticalLayoutWidget_12)
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet("background-color: rgb(170, 255, 127);")
        self.start_button.setFlat(False)
        self.start_button.setObjectName("start_button")
        self.horizontalLayout_7.addWidget(self.start_button)
        self.verticalLayout_12.addLayout(self.horizontalLayout_7)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("OilTankAnalizer", "Form"))
        self.Label_scan_name.setText(_translate("OilTankAnalizer", "Исходный\n"
                                                                   "скан:"))
        self.file_path_button.setText(_translate("OilTankAnalizer", "..."))
        self.label_bc_h.setText(_translate("OilTankAnalizer", "H, м:"))
        self.label_bc_z.setText(_translate("OilTankAnalizer", "Z, м:"))
        self.label_bc_y.setText(_translate("OilTankAnalizer", "Y, м:"))
        self.label_bc_r.setText(_translate("OilTankAnalizer", "R, м:"))
        self.label_bc_x.setText(_translate("OilTankAnalizer", "X, м:"))
        self.cb_use_base_cyl.setText(_translate("OilTankAnalizer", "Использовать цилиндр по\n"
                                                                   "заданным параметрам"))
        self.cb_fit_base_cyl.setText(_translate("OilTankAnalizer", "Вписать цилиндр в скан"))
        self.cb_filter_scan_by_z_limits.setText(_translate("OilTankAnalizer", "Использовать только точки\n"
                                                                              "в пределах:"))
        self.label_z_min.setText(_translate("OilTankAnalizer", "Z_min, м:"))
        self.label_z_max.setText(_translate("OilTankAnalizer", "Z_max, м:"))
        self.cb_save_cylinder_log.setText(_translate("OilTankAnalizer", "Сохранить параметры\n"
                                                                        "цилиндра в файл"))
        self.label_filter_major.setText(_translate("OilTankAnalizer", "Фильтрация исходного скана"))
        self.cb_filter_scan_decim_n.setText(_translate("OilTankAnalizer", "Разредить скан в N раз:"))
        self.label_filter_decim_n.setText(_translate("OilTankAnalizer", "N, раз:"))
        self.cb_filter_scan_radius.setText(_translate("OilTankAnalizer", "Удалить точки отстоящие от\n"
                                                                         "базового цилиндра:"))
        self.label_filter_radius.setText(_translate("OilTankAnalizer", "dR, м:"))
        self.cb_filter_scan_by_z_limits_2.setText(_translate("OilTankAnalizer", "Удалить точки не попадающие\n"
                                                                                "в пределы:"))
        self.label_filter_cyl_z_min.setText(_translate("OilTankAnalizer", "Z_min, м:"))
        self.label_filter_cyl_z_max.setText(_translate("OilTankAnalizer", "Z_max, м:"))
        self.label_saving_information.setText(_translate("OilTankAnalizer", "Сохраняемая информация"))
        self.label_def_scale.setText(_translate("OilTankAnalizer", "Масштаб для вывода деформаций:"))
        self.pt_def_scale.setPlainText(_translate("OilTankAnalizer", "1"))
        self.cb_vert_section_def.setText(_translate("OilTankAnalizer", "Построить вертикальные сечения:"))
        self.label_vert_section_az_max.setText(_translate("OilTankAnalizer", "Азимут_max, deg:"))
        self.pt_vert_section_az_max.setPlainText(_translate("OilTankAnalizer", "360"))
        self.label_vert_section_az_min.setText(_translate("OilTankAnalizer", "Азимут_min, deg:"))
        self.pt_vert_section_az_min.setPlainText(_translate("OilTankAnalizer", "0"))
        self.label_vert_section_count.setText(_translate("OilTankAnalizer", "Количество\n"
                                                                            "сечений, шт:"))
        self.pt_vert_section_count.setPlainText(_translate("OilTankAnalizer", "8"))
        self.cb_cylinder_izol_def.setText(_translate("OilTankAnalizer", "Изолинии деформаций\n"
                                                                        "на цилиндре:"))
        self.label_cyl_izol_step.setText(_translate("OilTankAnalizer", "Шаг изолиний, м:"))
        self.pt_cyl_izol_step.setPlainText(_translate("OilTankAnalizer", "0.01"))
        self.cb_hor_section_def.setText(_translate("OilTankAnalizer", "Построить горизонтальные сечения:"))
        self.label_hor_section_z_max.setText(_translate("OilTankAnalizer", "Z_max, м:"))
        self.label_hor_section_z_min.setText(_translate("OilTankAnalizer", "Z_min, м:"))
        self.label_hor_section_step.setText(_translate("OilTankAnalizer", "Шаг сечений, м:"))
        self.pt_hor_section_step.setPlainText(_translate("OilTankAnalizer", "0.05"))
        self.cb_flat_izol_def.setText(_translate("OilTankAnalizer", "Изолинии деформаций\n"
                                                                    "на плоскости:"))
        self.label_flat_izol_step.setText(_translate("OilTankAnalizer", "Шаг изолиний, м:"))
        self.pt_flat_izol_step.setPlainText(_translate("OilTankAnalizer", "0.01"))
        self.cb_save_flat_def_pc.setText(_translate("OilTankAnalizer", "Сохранить \"деформированное\"\n"
                                                                       "плоское облако точек"))
        self.cb_save_def_pc.setText(_translate("OilTankAnalizer", "Сохранить \"деформированное\"\n"
                                                                  "облако точек"))
        self.start_button.setText(_translate("OilTankAnalizer", "Запуск расчета"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui_OilTankAnalizer()
    window.show()
    sys.exit(app.exec())
