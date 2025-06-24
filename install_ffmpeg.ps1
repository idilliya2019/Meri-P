# Скрипт для установки FFmpeg
Write-Host "🎬 Установка FFmpeg..." -ForegroundColor Green

# Создаем папку для FFmpeg
$ffmpegPath = "C:\ffmpeg"
if (!(Test-Path $ffmpegPath)) {
    New-Item -ItemType Directory -Path $ffmpegPath -Force
    Write-Host "✅ Создана папка $ffmpegPath" -ForegroundColor Green
}

# Скачиваем FFmpeg
$ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$ffmpegZip = "$ffmpegPath\ffmpeg.zip"

Write-Host "📥 Скачивание FFmpeg..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip -UseBasicParsing
    Write-Host "✅ FFmpeg скачан" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка при скачивании: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Распаковываем архив
Write-Host "📦 Распаковка архива..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $ffmpegZip -DestinationPath $ffmpegPath -Force
    Write-Host "✅ Архив распакован" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка при распаковке: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Находим папку с исполняемыми файлами
$binPath = Get-ChildItem -Path $ffmpegPath -Directory | Where-Object { $_.Name -like "*bin*" } | Select-Object -First 1
if ($binPath) {
    $binPath = $binPath.FullName
    Write-Host "✅ Найдена папка bin: $binPath" -ForegroundColor Green
} else {
    Write-Host "❌ Папка bin не найдена" -ForegroundColor Red
    exit 1
}

# Копируем файлы в основную папку
Write-Host "📋 Копирование файлов..." -ForegroundColor Yellow
try {
    Copy-Item -Path "$binPath\*" -Destination "$ffmpegPath\bin\" -Force
    Write-Host "✅ Файлы скопированы" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка при копировании: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Добавляем в PATH
Write-Host "🔧 Добавление в PATH..." -ForegroundColor Yellow
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$ffmpegBinPath = "$ffmpegPath\bin"

if ($currentPath -notlike "*$ffmpegBinPath*") {
    $newPath = "$currentPath;$ffmpegBinPath"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-Host "✅ FFmpeg добавлен в PATH" -ForegroundColor Green
} else {
    Write-Host "✅ FFmpeg уже в PATH" -ForegroundColor Green
}

# Очищаем временные файлы
try {
    Remove-Item $ffmpegZip -Force
    Write-Host "✅ Временные файлы удалены" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Не удалось удалить временные файлы" -ForegroundColor Yellow
}

Write-Host "🎉 Установка FFmpeg завершена!" -ForegroundColor Green
Write-Host "💡 Перезапустите командную строку и выполните: ffmpeg -version" -ForegroundColor Cyan 