# Aequitas-MVP — Local Run Instructions

This short guide explains how to run the backend (Flask) and frontend (Vite/React) locally.

Prerequisites
- Python 3.10+ and pip
- Node.js & npm (install via Homebrew: `brew install node` or from https://nodejs.org)

Backend
1. Install Python deps:
   ```bash
   cd backend
   python3 -m pip install -r requirements.txt
   ```
2. Start the backend (development):
   ```bash
   # dev server (foreground)
   PORT=5001 python3 run.py
   # or in background (use gunicorn for production-like runs)
   gunicorn -b 0.0.0.0:5001 "app:create_app()" --workers 2 --log-file -
   ```

Frontend
1. Install Node deps and start Vite dev server:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. The frontend dev server runs on http://127.0.0.1:5173 by default.
   The dev Vite config proxies requests starting with `/api` to
   `http://localhost:5001` so frontend code can call `/api/v1/...` directly.

Notes
- If port 5000 is in use by macOS services, the backend will fail to bind — use `PORT=5001` or another free port.
- If you run the Flask dev server in background (nohup) the reloader can crash due to TTY/termios; run without the reloader or use gunicorn for background runs.

If you want, I can add a small script (Makefile / start script) to encapsulate these commands.
