Write-Host "Starting Bearnoby Website Static Server..." -ForegroundColor Green
Write-Host "URL: http://localhost:8080" -ForegroundColor Yellow

# Start a simple Python HTTP server to preview the static site
python -m http.server 8080
