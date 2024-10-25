#!/bin/bash

# Build frontend
cd frontend && pnpm run build && cd ..

# Build with Nuitka
pyinstaller \
  --windowed \
  --noconfirm \
  --icon=assets/icon.png \
  --name=Texa \
  --add-data=artifacts:artifacts \
  --optimize=1 \
  texa.py

# Check if build was successful
if [ $? -eq 0 ]; then
  echo "Build completed successfully!"
else
  echo "Build failed!"
  exit 1
fi
