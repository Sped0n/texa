# Build frontend
Set-Location frontend
pnpm run build
Set-Location ..

# Build with Nuitka
$buildProcess = Start-Process -FilePath "pyinstaller" -ArgumentList @(
    "--windowed",
    "--noconfirm", 
    "--icon=assets/icon.png",
    "--name=Texa",
    "--add-data=artifacts;artifacts",
    "--optimize=1",
    "texa.py"
) -Wait -PassThru -NoNewWindow

# Check if build was successful
if ($buildProcess.ExitCode -eq 0) {
    Write-Host "Build completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
