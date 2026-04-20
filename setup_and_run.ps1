# Smart Stadium AI - Windows Setup (No Docker)

Write-Host "🔧 Setting up Smart Stadium AI for Windows (No Docker)..." -ForegroundColor Cyan

# Function to check if a command exists
function Test-Command($Command) {
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

# Function to check if a port is in use
function Test-Port($Port) {
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
    return $connection.TcpTestSucceeded
}

# 1. Check/Install Redis
Write-Host "📦 Checking Redis..." -ForegroundColor Yellow
if (-not (Test-Command "redis-server")) {
    Write-Host "⚠️ Redis not found. Installing via Chocolatey..." -ForegroundColor Yellow
    if (-not (Test-Command "choco")) {
        Write-Host "Installing Chocolatey first..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    }
    choco install redis-64 -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

# 2. Check/Install MongoDB
Write-Host "📦 Checking MongoDB..." -ForegroundColor Yellow
if (-not (Test-Command "mongod")) {
    Write-Host "⚠️ MongoDB not found. Installing via Chocolatey..." -ForegroundColor Yellow
    if (-not (Test-Command "choco")) {
        Write-Host "Installing Chocolatey first..." -ForegroundColor Yellow
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    }
    choco install mongodb -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

# 3. Create data directories
if (-not (Test-Path "C:\data\db")) {
    New-Item -ItemType Directory -Path "C:\data\db" -Force | Out-Null
}

# 4. Start Redis
Write-Host "🚀 Starting Redis..." -ForegroundColor Green
if (-not (Test-Port 6379)) {
    Start-Process redis-server -WindowStyle Hidden
    Start-Sleep -Seconds 2
    Write-Host "✅ Redis started on port 6379" -ForegroundColor Green
} else {
    Write-Host "✅ Redis already running on port 6379" -ForegroundColor Green
}

# 5. Start MongoDB
Write-Host "🚀 Starting MongoDB..." -ForegroundColor Green
if (-not (Test-Port 27017)) {
    Start-Process mongod -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "✅ MongoDB started on port 27017" -ForegroundColor Green
} else {
    Write-Host "✅ MongoDB already running on port 27017" -ForegroundColor Green
}

# 6. Install Backend Dependencies
Write-Host "📦 Installing Backend Dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt
Set-Location ..

# 7. Install Frontend Dependencies
Write-Host "📦 Installing Frontend Dependencies..." -ForegroundColor Yellow
Set-Location frontend
pip install -r requirements.txt
Set-Location ..

# 8. Launch Services in separate windows
Write-Host "🏃 Launching Services..." -ForegroundColor Green

# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; uvicorn main:app --reload --port 8000" -WindowStyle Normal

# Start Simulators
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python backend/simulators/run_simulators.py" -WindowStyle Normal

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; streamlit run app.py --server.port 8501" -WindowStyle Normal

Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host "📍 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📍 Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "Press Enter to stop all services..." -ForegroundColor Yellow
$null = Read-Host

# Cleanup - stop services
Write-Host "🛑 Stopping services..." -ForegroundColor Red
Stop-Process -Name "redis-server" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "mongod" -Force -ErrorAction SilentlyContinue
Write-Host "✅ Services stopped" -ForegroundColor Green
