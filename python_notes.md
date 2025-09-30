# Python Notes

## References

1. Pyside tutorial: https://www.youtube.com/watch?v=Z1N9JzNax2k
   - Tutorial's Github repo: https://github.com/rutura/Qt-For-Python-PySide6-GUI-For-Beginners-The-Fundamentals-
2. Qt for Python Reference: https://doc.qt.io/qtforpython-6/

## Install

- To install the project using pip and `pyproject.toml` file: `pip install .`
- To install the project using pip and `pyproject.toml` file in editable mode: `pip install -e .`
- To build the resource file for pyside6, use: `pyside6-rcc src/gui/icons.qrc -o src/gui/iconsrc.py`
- To build the project: 
  - First install build package if not already installed: `pip install build`
  - Then run: `python -m build`
- To install the project using the wheel file, use: `pip install dist/nextjob-0.0.1-py3-none-any.whl`
