import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from gui.mainwindow import MainWindow


def main():
    """Main function."""
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
    app.setWindowIcon(QIcon(":/images/nextjob.png"))
    widget = MainWindow(app)
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
