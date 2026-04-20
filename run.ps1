# Smart Stadium AI - Windows Runner
Write-Host "Starting Smart Stadium AI..." -ForegroundColor Cyan

$baseDir = "$PSScriptRoot\.runtime"
$redisDir = "$baseDir\redis"

# Download Redis if not present
if (-not (Test-Path "$redisDir\redis-server.exe")) {
    Write-Host "Downloading Redis (one-time)..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $redisDir -Force | Out-Null
    $url = "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip"
    $zip = "$env:TEMP\redis.zip"
    Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
    Expand-Archive -Path $zip -DestinationPath $redisDir -Force
    Remove-Item $zip
}

# Check if Redis is running
try {
    $conn = New-Object System.Net.Sockets.TcpClient
    $conn.Connect("localhost", 6379)
    $conn.Close()
    $redisRunning = $true
} catch {
    $redisRunning = $false
}

# Start Redis if not running
if (-not $redisRunning) {
    Write-Host "Starting Redis..." -ForegroundColor Green
    Start-Process "$redisDir\redis-server.exe" -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

# Install deps
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -q -r backend/requirements.txt 2>$null
pip install -q -r frontend/requirements.txt 2>$null

# Launch services
Write-Host "Starting services..." -ForegroundColor Green

$projectPath = $PSScriptRoot

# Backend - run from project root with proper Python path
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; `$env:PYTHONPATH='$projectPath'; uvicorn backend.main:app --reload --port 8000" -WindowStyle Normal
Start-Sleep -Seconds 2

# Simulators
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; `$env:PYTHONPATH='$projectPath'; python backend/simulators/run_simulators.py" -WindowStyle Normal
Start-Sleep -Seconds 1

# Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath\frontend'; streamlit run app.py --server.port 8501" -WindowStyle Normal

Write-Host "All services started!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:8501" -ForegroundColor Cyan
Read-Host "Press Enter to stop all services"
