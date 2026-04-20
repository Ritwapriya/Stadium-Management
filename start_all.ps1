# Smart Stadium AI - Startup Script

Write-Host "🚀 Starting Smart Stadium AI Infrastructure..." -ForegroundColor Cyan

# 1. Start Docker Containers
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    docker-compose up -d
} else {
    Write-Error "docker-compose not found. Please install Docker Desktop."
    exit 1
}

# 2. Install Backend Dependencies
Write-Host "📦 Installing Backend Dependencies..." -ForegroundColor Yellow
cd backend
pip install -r requirements.txt
cd ..

# 3. Install Frontend Dependencies
Write-Host "📦 Installing Frontend Dependencies..." -ForegroundColor Yellow
cd frontend
pip install -r requirements.txt
cd ..

# 4. Launch Services
Write-Host "🏃 Launching Services..." -ForegroundColor Green

# Start Backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn main:app --reload --port 8000" -WindowStyle Normal

# Start Simulators in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python backend/simulators/run_simulators.py" -WindowStyle Normal

# Start Frontend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; streamlit run app.py --server.port 8501" -WindowStyle Normal

Write-Host "✅ All services are starting in separate windows." -ForegroundColor Green
Write-Host "Please wait a few seconds for initialization, then tell me 'Services are running'." -ForegroundColor Cyan
