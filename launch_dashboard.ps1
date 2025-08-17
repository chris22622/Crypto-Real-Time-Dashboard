# Crypto Dashboard Launcher
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Crypto Real-Time Dashboard..." -ForegroundColor Green

# Set working directory
$projectPath = "C:\Users\Chris\Personal Finance Dashboard\crypto-realtime-dashboard"
Set-Location $projectPath

Write-Host "📂 Working directory: $(Get-Location)" -ForegroundColor Cyan

# Activate virtual environment
$venvPath = Join-Path $projectPath ".venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
    & $venvPath
} else {
    Write-Host "❌ Virtual environment not found at $venvPath" -ForegroundColor Red
    exit 1
}

# Check if app exists
$appPath = Join-Path $projectPath "app\main.py"
if (-not (Test-Path $appPath)) {
    Write-Host "❌ App file not found at $appPath" -ForegroundColor Red
    exit 1
}

Write-Host "📊 Starting Streamlit application..." -ForegroundColor Green
Write-Host "🌐 Dashboard will be available at: http://localhost:8501" -ForegroundColor Cyan
Write-Host "⏹️  Press Ctrl+C to stop the server" -ForegroundColor Yellow

# Run Streamlit
try {
    streamlit run app\main.py --server.port 8501
} catch {
    Write-Host "❌ Error running Streamlit: $_" -ForegroundColor Red
    exit 1
}
