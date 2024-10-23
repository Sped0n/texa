qrc:
	pyside6-rcc gui.assets/resources.qrc -o gui/resources.py

pyinstaller:
	pyinstaller --windowed --noconfirm --icon=gui.assets/icon.png --collect-submodules=pymdownx.arithmatex --name=Texa --optimize=1 gui/__main__.py

nuitka:
	python -m nuitka gui \
		--plugin-enable=pyside6 \
		--include-module=pymdownx.arithmatex \
		--macos-create-app-bundle \
		--macos-app-version=1.0.3 \
		--macos-app-icon=./gui.assets/icon.png \
		--output-filename=texa \
		--lto=yes \
		--standalone \
		--deployment \
		--product-name=Texa \
		--file-version=1.0.3 \
		--product-version=1.0.3 \
		--file-description="Easy LaTeX and markdown OCR" \
		--show-progress \
