nuitka: texa.py
	cd frontend && pnpm run build && cd .. && \
	python -m nuitka texa.py \
    --include-package-data=webview \
		--include-data-dir=./artifacts=artifacts \
		--macos-create-app-bundle \
		--macos-app-version=1.0.3 \
		--macos-app-icon=./assets/icon.png \
		--output-filename=texa \
		--standalone \
		--deployment \
		--product-name=Texa \
		--file-version=1.0.3 \
		--product-version=1.0.3 \
		--file-description="Easy LaTeX and markdown OCR" \
		--show-progress \

pyinstaller:
	pyinstaller --windowed --noconfirm --icon=assets/icon.png --name=Texa --add-data=artifacts:artifacts --optimize=1 texa.py
