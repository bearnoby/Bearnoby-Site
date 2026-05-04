# Bearnoby Website

I'm the bear, it's my site c:

## Getting Started

### Local Development
To run the website locally on Windows, use the provided PowerShell script:
```powershell
.\run.ps1
```
This script will automatically:
1. Create a Python virtual environment (`venv`).
2. Install necessary dependencies from `requirements.txt`.
3. Start the Flask server on `http://localhost:8080`.

### Tech Stack
- **Backend**: Flask (Python 3.11+)
- **Frontend**: Vanilla HTML/CSS (Modern "Carrd-style" centered layout)
- **Deployment**: Optimized for Google Cloud Run

## Deployment

This project is configured for **Google Cloud Run** with GitHub-based Continuous Integration:
1. Push this repository to GitHub.
2. Create a new Cloud Run service in the Google Cloud Console.
3. Enable "Continuous Deployment from a Repository".
4. The included `Dockerfile` and `requirements.txt` will handle the build and deployment automatically.

## Project Structure
- `app.py`: Flask application entry point.
- `static/`: Contains CSS styling and images.
- `templates/`: HTML templates.
- `Dockerfile`: Container configuration for production.
- `run.ps1`: Automated local setup script.
