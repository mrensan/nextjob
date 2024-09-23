import sys

from PySide6.QtWidgets import QApplication, QWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QWidget()
    widget.show()
    sys.exit(app.exec())
