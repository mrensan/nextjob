from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QAbstractItemView,
    QPushButton,
    QMessageBox,
    QApplication,
    QErrorMessage,
)
from pydantic import ValidationError

ADD_ICON = ":/images/add.png"
EDIT_ICON = ":/images/edit.png"
DELETE_ICON = ":/images/delete.png"
SEARCH_ICON = ":/images/search.png"
RESET_ICON = ":/images/reset.png"
MD_IMPORT = ":/images/md_import.png"
MD_ADD = ":/images/md_add.png"


def get_line_layout(
    left: QWidget,
    right: QWidget,
    first_stretch: int = 1,
    second_stretch: int = 2,
    space_stretch: int = 7,
) -> QHBoxLayout:
    """Creates a line layout with left and right widgets."""
    line = QHBoxLayout()
    line.addWidget(left, first_stretch)
    line.addWidget(right, second_stretch)
    line.addWidget(QLabel(), space_stretch)
    return line


def config_view_as_line_selectable(abstract_item_view: QAbstractItemView):
    """Configures an abstract item view as line selectable."""
    abstract_item_view.setSelectionBehavior(
        QAbstractItemView.SelectionBehavior.SelectRows
    )
    abstract_item_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    abstract_item_view.setAlternatingRowColors(True)
    abstract_item_view.setHorizontalScrollMode(
        QAbstractItemView.ScrollMode.ScrollPerPixel
    )


def create_save_cancel_layout(
    cancel_method: callable,
    save_method: callable,
    first_stretch: int = 1,
    second_stretch: int = 1,
    space_stretch: int = 7,
) -> QHBoxLayout:
    """Creates a layout with save and cancel buttons."""
    cancel_btn = QPushButton("Cancel")
    cancel_btn.clicked.connect(cancel_method)
    save_btn = QPushButton("Save")
    save_btn.clicked.connect(save_method)
    return get_line_layout(
        cancel_btn, save_btn, first_stretch, second_stretch, space_stretch
    )


def get_attr(obj, attr, default=""):
    """Returns an attribute from an object when it exists, otherwise returns the default value."""
    return getattr(obj, attr, default) if obj else default


def verify_delete_row(message: str, parent: QWidget) -> bool:
    """Asks the user if they want to delete a row."""
    buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    return (
        QMessageBox.critical(parent, "Delete", message, buttons)
        == QMessageBox.StandardButton.Yes
    )


def translate_validation_error(error: ValidationError) -> str:
    """Translates a validation error to a string."""
    msg_parts = []
    for err in error.errors():
        msg_parts.append(f"'{err['loc'][0]}': {err['msg']}\n")
    return ", ".join(msg_parts)


def translate_date_format_error(error: ValueError) -> str:
    """Translates a date format error to a string."""
    if "Invalid isoformat string" in error.args[0]:
        return "Invalid date format. Use YYYY-MM-DD"
    return error.args[0]


def show_error_dialog(parent: QWidget, title: str, message: str):
    """Shows an error dialog."""
    error_dialog = QErrorMessage(parent)
    error_dialog.setWindowTitle(title)
    error_dialog.showMessage(message)
    error_dialog.exec()


def is_dark_theme():
    """Checks if the current theme is dark."""
    # Get the application's palette
    palette = QApplication.palette()
    window_color = palette.color(QPalette.ColorRole.Window)

    # Calculate the brightness of the background color
    # Brightness formula (weighted sum) is standard for luminance calculation
    brightness = (
        0.299 * window_color.red()
        + 0.587 * window_color.green()
        + 0.114 * window_color.blue()
    )
    return brightness < 128  # A threshold value; < 128 indicates a dark color
