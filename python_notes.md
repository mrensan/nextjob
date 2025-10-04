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
- To make a MacOS installer:
  - First install pyinstaller if not already installed: `pip install pyinstaller`
  - Then run: `pyinstaller --noconsole --windowed --name "Next Job" --icon=src/gui/images/nextjob.icns  src/gui/main.py`
  - This will create a "Next Job.app" file in the `dist` folder. Move this file to the Applications folder.
- How to convert `png` to `icns` for MacOS app icon:
  - Quick method: `sips -s format icns .../nextjob.png --out nextjob.icns`
  - Complete method:
    1. Create a folder named `nextjob.iconset`
    2. Inside this folder, create the following files by resizing the original `png` image:
       - `icon_16x16.png` (16x16 pixels)
       - `icon_32x32.png` (32x32 pixels)
       - `icon_128x128.png` (128x128 pixels)
       - `icon_256x256.png` (256x256 pixels)
       - `icon_512x512.png` (512x512 pixels)
    3. Run the command: `iconutil -c icns nextjob.iconset -o nextjob.icns`
