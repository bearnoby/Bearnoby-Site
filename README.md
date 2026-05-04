# Bearnoby Website

I'm the bear, it's my site c:

## Getting Started

### Local Development
To preview the website locally on Windows, use the provided PowerShell script:
```powershell
.\run.ps1
```
This script will start a lightweight Python HTTP server on `http://localhost:8080`.

### Tech Stack
- **Frontend**: Vanilla HTML/CSS (Modern "Carrd-style" centered layout)
- **Deployment**: GitHub Pages (Static Hosting)

## Deployment

The project is hosted on **GitHub Pages**. To update the live site:

1. Push your changes to the `main` branch.
2. GitHub Actions/Pages will automatically detect the `index.html` in the root and deploy it.

## Project Structure
- `index.html`: The main static landing page.
- `static/`: Contains CSS styling and images.
- `run.ps1`: Simple local preview script.
- `templates/` & `app.py`: Legacy Flask files (not used by GitHub Pages).
