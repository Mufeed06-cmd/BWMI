# NTA Exam Tracker

Mobile-first React + FastAPI app for tracking JEE Main, NEET, and CUET exam journeys with AI-assisted date predictions and readiness actions.

The backend uses NTA pattern data and calls Groq when `GROQ_API_KEY` is configured. If no API key is present, the API returns a deterministic pattern-based response so local development still works.

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The React dev server proxies `/api` to `http://localhost:8000`.

## Environment

Create a backend `.env` file for local development or set Railway variables for deployment:

```bash
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

## Railway Deployment

This repo includes a root `Dockerfile` and `railway.json`. Railway can deploy it as one web service.

The Dockerfile builds `frontend/dist`, copies it to `/app/frontend/dist`, installs the FastAPI backend, and starts:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

FastAPI serves `/api/*` from the backend and serves the compiled React app from `frontend/dist`, so no separate frontend service is required.

Railway uses the Dockerfile `CMD` as the start command for Dockerfile deployments, so `railway.json` does not need a custom `startCommand`.

Exact steps:

1. Push this repository to GitHub.
2. In Railway, create a new project and choose **Deploy from GitHub repo**.
3. Select this repository.
4. Confirm Railway detects the root `Dockerfile`.
5. Open the service **Variables** tab.
6. Add `GROQ_API_KEY` with your Groq key.
7. Optionally add `GROQ_MODEL` if you want to override the default model.
8. Deploy the service.
9. After deployment, open the Railway public URL and test `/api/health`.
10. In the app, run an exam prediction and confirm the response is AI assisted.

## API

- `GET /api/exams` lists supported exams, stages, and NTA pattern data.
- `POST /api/track` accepts:

```json
{
  "exam": "JEE Main",
  "current_stage": "Applied"
}
```

It returns timeline stages, predicted dates, confidence, readiness items, and whether the response came from Groq or fallback logic.
