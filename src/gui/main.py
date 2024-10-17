import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .mainwindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    image_absolute_path = Path(__file__).resolve().parent / "../../images/nextjob.png"
    app.setWindowIcon(QIcon(str(image_absolute_path)))
    widget = MainWindow(app)
    widget.show()
    sys.exit(app.exec())
