# Smart Task Analyzer — Internship Assignment (Generated)

## Overview
This repository contains a complete minimal implementation of the Smart Task Analyzer assignment.
It includes a Django backend (with a simple scoring algorithm) and a small frontend (HTML/CSS/JS) that
communicates with the backend via REST endpoints.

## How to run (development)
1. Create a Python virtual environment and activate it.
   ```bash
   python -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```
2. Run migrations and start the server:
   ```bash
   cd backend
   python manage.py migrate
   python manage.py runserver
   ```
3. Open `frontend/index.html` in a browser (or serve it via a static server). For convenience, you can access the frontend by opening the file directly and making sure API calls are proxied to `http://localhost:8000/api/tasks/...` (if running locally) — or place frontend files under Django static files if preferred.

## API Endpoints
- `POST /api/tasks/analyze/` — Accepts JSON array of tasks, returns tasks sorted with `score` and `explanation`.
- `GET /api/tasks/suggest/` — Returns top 3 tasks from the most recent analysis (stored in-memory).

## Scoring algorithm (summary)
Implemented in `backend/tasks/scoring.py`. The score is computed from:
- Urgency (closeness of due date, overdue tasks boosted)
- Importance (1–10 normalized)
- Effort (favors low estimated_hours)
- Dependency (tasks that block others get a bump)

We combine weighted components and scale to `0-100`. Circular dependencies are detected and slightly penalized so the user is prompted to fix them.

## Design decisions & trade-offs
- Kept the backend stateless for task analysis; the `suggest` endpoint uses a small in-memory cache populated by `/analyze/` for demo convenience.
- The scoring function is intentionally simple and well-documented to show reasoning rather than opaque ML.
- For production, persistence (DB-stored tasks), authentication, and better handling of timezones/holidays would be required.

## Tests
Unit tests for the scoring algorithm are in `backend/tasks/tests.py` (run with `python manage.py test`).

## Future improvements
- Store tasks in DB, add CRUD endpoints.
- Make weights configurable per-user in a settings UI.
- Add circular-dependency visualization (D3/vis.js).
- Add holidays/weekends awareness for urgency calculation.

