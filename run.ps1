Write-Host "Building site into _site/..." -ForegroundColor Green
python scripts/build.py --out _site
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed, not starting server." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Starting Bearnoby Website Static Server..." -ForegroundColor Green
Write-Host "URL: http://localhost:8080" -ForegroundColor Yellow
Write-Host "Blog: http://localhost:8080/blog/" -ForegroundColor Yellow
Write-Host "Blog preview: http://localhost:8080/blog-preview/" -ForegroundColor Yellow

# Serve the built site
python -m http.server 8080 --directory _site
