from PySide6.QtWidgets import QWidget

def test_widget_creation(qtbot):
    """Test if the QWidget is created and shown correctly."""
    widget = QWidget()
    qtbot.addWidget(widget)  # Registers the widget with qtbot to handle Qt-related events
    widget.show()

    assert widget.isVisible()  # Check if the widget is visible
