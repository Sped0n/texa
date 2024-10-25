#!/bin/bash

# Check if version parameter is provided
if [ $# -ne 1 ]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 1.0.3"
  exit 1
fi

VERSION=$1

# Build frontend
cd frontend && pnpm run build && cd ..

# Build with Nuitka
python -m nuitka texa.py \
  --include-package-data=webview \
  --include-data-dir=./artifacts=artifacts \
  --macos-create-app-bundle \
  --macos-app-version="$VERSION" \
  --macos-app-icon=./assets/icon.png \
  --output-filename=texa \
  --standalone \
  --deployment \
  --product-name=Texa \
  --file-version="$VERSION" \
  --product-version="$VERSION" \
  --file-description="Easy LaTeX and markdown OCR" \
  --show-progress

# Check if build was successful
if [ $? -eq 0 ]; then
  echo "Build completed successfully!"
else
  echo "Build failed!"
  exit 1
fi
