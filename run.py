import sys

from PyQt6.QtWidgets import QApplication

from interface.interface import Ui_OilTankAnalizer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui_OilTankAnalizer()
    window.show()
    sys.exit(app.exec())
