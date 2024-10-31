from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon, QClipboard
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QToolBar, QMessageBox
from markdown import markdown

from gui.guiutils import MD_IMPORT, MD_ADD, RESET_ICON


class DescriptionTextEdit(QWidget):
    """A widget that contains a QTextEdit and a QToolBar for text editing."""

    def __init__(self, text: str = ""):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
        layout.setSpacing(0)  # Remove space between widgets

        # Create a QTextEdit
        self.text_edit = QTextEdit(text)

        # Create a QToolBar and add an action to it
        self.toolbar = QToolBar("Text Actions")
        self.toolbar.setIconSize(QSize(20, 20))
        self.toolbar.setFixedHeight(24)
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        self.toolbar.setStyleSheet("""
            QToolBar { padding: 0px; margin: 0px; spacing: 0px; }
            QToolButton { padding: 0px; margin: 0px; }
        """)  # Adjust toolbar and button padding
        md_import_action = QAction(QIcon(MD_IMPORT), "Clipboard Markdown", self)
        md_import_action.triggered.connect(self.md_import_action_triggered)
        self.toolbar.addAction(md_import_action)
        md_add_action = QAction(QIcon(MD_ADD), "Add Clipboard Markdown", self)
        md_add_action.triggered.connect(self.md_add_action_triggered)
        self.toolbar.addAction(md_add_action)
        self.toolbar.addSeparator()
        reset_action = QAction(QIcon(RESET_ICON), "Reset", self)
        reset_action.triggered.connect(self.reset_action_triggered)
        self.toolbar.addAction(reset_action)

        # Add the toolbar and QTextEdit to the layout
        layout.addWidget(self.toolbar)
        layout.addWidget(self.text_edit)

        self.setLayout(layout)

    def md_import_action_triggered(self):
        """Import Markdown from Clipboard"""
        clipboard = QClipboard()
        clipboard_text = clipboard.text()
        if clipboard_text:
            html_text = markdown(clipboard.text())
            self.text_edit.setHtml(markdown(html_text))
        else:
            QMessageBox.warning(self, "Warning", "No text in Clipboard")

    def md_add_action_triggered(self):
        """Add Markdown from Clipboard"""
        clipboard = QClipboard()
        clipboard_text = clipboard.text()
        if clipboard_text:
            self.text_edit.append(markdown(clipboard.text()))
        else:
            QMessageBox.warning(self, "Warning", "No text in Clipboard")

    def reset_action_triggered(self):
        """Reset the QTextEdit"""
        self.text_edit.clear()

    # pylint: disable=invalid-name
    def toHtml(self):
        """Returns the HTML content of the QTextEdit"""
        return self.text_edit.toHtml()
