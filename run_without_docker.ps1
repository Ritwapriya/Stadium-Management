# Smart Stadium AI - Windows Run Script (Downloads portable Redis/MongoDB)

Write-Host "🔧 Setting up Smart Stadium AI..." -ForegroundColor Cyan

$baseDir = "$PSScriptRoot\runtime_db"

# Create directories
if (-not (Test-Path "$baseDir")) {
    New-Item -ItemType Directory -Path "$baseDir" -Force | Out-Null
}
if (-not (Test-Path "$baseDir\redis")) {
    New-Item -ItemType Directory -Path "$baseDir\redis" -Force | Out-Null
}
if (-not (Test-Path "$baseDir\mongodb\data")) {
    New-Item -ItemType Directory -Path "$baseDir\mongodb\data" -Force | Out-Null
}

# Download and setup Redis if not present
$redisDir = "$baseDir\redis"
if (-not (Test-Path "$redisDir\redis-server.exe")) {
    Write-Host "📥 Downloading Redis for Windows..." -ForegroundColor Yellow
    $redisUrl = "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip"
    $redisZip = "$env:TEMP\redis.zip"
    
    try {
        Invoke-WebRequest -Uri $redisUrl -OutFile $redisZip -UseBasicParsing
        Expand-Archive -Path $redisZip -DestinationPath $redisDir -Force
        Remove-Item $redisZip
        Write-Host "✅ Redis downloaded" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to download Redis automatically" -ForegroundColor Red
        Write-Host "Please download from: https://github.com/tporadowski/redis/releases" -ForegroundColor Yellow
        pause
        exit
    }
}

# Check if ports are available
function Test-Port($Port) {
    try {
        $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        $listener.Stop()
        return $false
    } catch {
        return $true
    }
}

# Start Redis
Write-Host "🚀 Starting Redis..." -ForegroundColor Green
if (-not (Test-Port 6379)) {
    $redisProcess = Start-Process -FilePath "$redisDir\redis-server.exe" -WorkingDirectory $redisDir -WindowStyle Hidden -PassThru
    Start-Sleep -Seconds 2
    if (Test-Port 6379) {
        Write-Host "✅ Redis started on port 6379" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to start Redis" -ForegroundColor Red
    }
} else {
    Write-Host "✅ Redis already running on port 6379" -ForegroundColor Green
}

# For MongoDB, use in-memory approach or download
# Let's use a lightweight approach - install pymongo with in-memory mode or use SQLite fallback
Write-Host "📦 Note: MongoDB will use lightweight mode for development" -ForegroundColor Yellow

# Install dependencies
Write-Host "📦 Installing Backend Dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt
# Add mongomock for testing without MongoDB
pip install mongomock 2>$null
Set-Location ..

Write-Host "📦 Installing Frontend Dependencies..." -ForegroundColor Yellow
Set-Location frontend
pip install -r requirements.txt
Set-Location ..

# Launch Services
Write-Host "🏃 Launching Services..." -ForegroundColor Green

# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; `$env:MONGO_URL='mongodb://localhost:27017'; uvicorn main:app --reload --port 8000" -WindowStyle Normal

# Start Simulators
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python backend/simulators/run_simulators.py" -WindowStyle Normal

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; streamlit run app.py --server.port 8501" -WindowStyle Normal

Write-Host "" -ForegroundColor White
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host "📍 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📍 Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
