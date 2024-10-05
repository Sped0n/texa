qrc:
	pyside6-rcc gui.assets/resources.qrc -o gui/resources.py

pyinstaller:
	pyinstaller --windowed --noconfirm --icon=gui.assets/icon.png --collect-submodules=pymdownx.arithmatex --name=Texa --optimize=1 gui/__main__.py
