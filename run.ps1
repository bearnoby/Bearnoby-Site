param(
    [int]$Port = 8080
)

Write-Host "Building site into _site/..." -ForegroundColor Green
python scripts/build.py --out _site
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed, not starting server." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Starting Bearnoby Website Static Server..." -ForegroundColor Green
Write-Host "URL: http://localhost:$Port" -ForegroundColor Yellow
Write-Host "Blog: http://localhost:$Port/blog/" -ForegroundColor Yellow
Write-Host "Blog preview: http://localhost:$Port/blog-preview/" -ForegroundColor Yellow

# Serve the built site
python -m http.server $Port --directory _site
