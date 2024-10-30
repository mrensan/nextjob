from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QAbstractItemView, QPushButton, QMessageBox

ADD_ICON = ":/images/newdirectory-32.png"
EDIT_ICON = ":/images/desktop-32.png"
DELETE_ICON = ":/images/critical-32.png"
SEARCH_ICON = ":/images/filecontents-32.png"
RESET_ICON = ":/images/cleartext-32.png"


def get_line_layout(
        left: QWidget,
        right: QWidget,
        first_stretch: int = 1,
        second_stretch: int = 2,
        space_stretch: int = 7
) -> QHBoxLayout:
    """Creates a line layout with left and right widgets."""
    line = QHBoxLayout()
    line.addWidget(left, first_stretch)
    line.addWidget(right, second_stretch)
    line.addWidget(QLabel(), space_stretch)
    return line


def config_view_as_line_selectable(abstract_item_view: QAbstractItemView):
    """Configures an abstract item view as line selectable."""
    abstract_item_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    abstract_item_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    abstract_item_view.setAlternatingRowColors(True)
    abstract_item_view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)


def create_save_cancel_layout(cancel_method: callable, save_method: callable, first_stretch: int = 1,
                              second_stretch: int = 1, space_stretch: int = 7) -> QHBoxLayout:
    """Creates a layout with save and cancel buttons."""
    cancel_btn = QPushButton("Cancel")
    cancel_btn.clicked.connect(cancel_method)
    save_btn = QPushButton("Save")
    save_btn.clicked.connect(save_method)
    return get_line_layout(cancel_btn, save_btn, first_stretch, second_stretch, space_stretch)


def get_attr(obj, attr, default=''):
    """Returns an attribute from an object when it exists, otherwise returns the default value."""
    return getattr(obj, attr, default) if obj else default


def verify_delete_row(message: str, parent: QWidget) -> bool:
    """Asks the user if they want to delete a row."""
    buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    return QMessageBox.critical(parent, "Delete", message, buttons) == QMessageBox.StandardButton.Yes
