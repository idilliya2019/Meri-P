# FFmpeg Installation Script
Write-Host "Installing FFmpeg..." -ForegroundColor Green

# Create FFmpeg directory
$ffmpegPath = "C:\ffmpeg"
if (!(Test-Path $ffmpegPath)) {
    New-Item -ItemType Directory -Path $ffmpegPath -Force
    Write-Host "Created directory $ffmpegPath" -ForegroundColor Green
}

# Download FFmpeg
$ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$ffmpegZip = "$ffmpegPath\ffmpeg.zip"

Write-Host "Downloading FFmpeg..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip -UseBasicParsing
    Write-Host "FFmpeg downloaded" -ForegroundColor Green
} catch {
    Write-Host "Download error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Extract archive
Write-Host "Extracting archive..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $ffmpegZip -DestinationPath $ffmpegPath -Force
    Write-Host "Archive extracted" -ForegroundColor Green
} catch {
    Write-Host "Extraction error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Find bin directory
$binPath = Get-ChildItem -Path $ffmpegPath -Directory | Where-Object { $_.Name -like "*bin*" } | Select-Object -First 1
if ($binPath) {
    $binPath = $binPath.FullName
    Write-Host "Found bin directory: $binPath" -ForegroundColor Green
} else {
    Write-Host "Bin directory not found" -ForegroundColor Red
    exit 1
}

# Copy files
Write-Host "Copying files..." -ForegroundColor Yellow
try {
    Copy-Item -Path "$binPath\*" -Destination "$ffmpegPath\bin\" -Force
    Write-Host "Files copied" -ForegroundColor Green
} catch {
    Write-Host "Copy error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Add to PATH
Write-Host "Adding to PATH..." -ForegroundColor Yellow
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$ffmpegBinPath = "$ffmpegPath\bin"

if ($currentPath -notlike "*$ffmpegBinPath*") {
    $newPath = "$currentPath;$ffmpegBinPath"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-Host "FFmpeg added to PATH" -ForegroundColor Green
} else {
    Write-Host "FFmpeg already in PATH" -ForegroundColor Green
}

# Clean up
try {
    Remove-Item $ffmpegZip -Force
    Write-Host "Temporary files removed" -ForegroundColor Green
} catch {
    Write-Host "Could not remove temporary files" -ForegroundColor Yellow
}

Write-Host "FFmpeg installation completed!" -ForegroundColor Green
Write-Host "Restart your terminal and run: ffmpeg -version" -ForegroundColor Cyan 