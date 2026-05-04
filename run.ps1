# Check if venv exists, if not create it
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate venv and install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
.\venv\Scripts\pip install -r requirements.txt

# Run the app
Write-Host "Starting Bearnoby Website locally..." -ForegroundColor Green
Write-Host "URL: http://localhost:8080" -ForegroundColor Yellow
$env:PORT = "8080"
.\venv\Scripts\python app.py
