
# NTA Exam Tracker — Know Before You Check

> AI-assisted milestone predictions for JEE Main, NEET, and CUET students — so you stop refreshing and start preparing.

## 🔴 Live Demo

**[https://bwmi-production.up.railway.app/](https://bwmi-production.up.railway.app/)**

---

## The Problem

Every year, millions of Indian students appear for JEE Main, NEET, and CUET. After the exam ends, they face weeks of uncertainty — when will the answer key drop? When will results come? Students never receive a clear, personalized timeline. Notices appear on the NTA website without warning. There is no way to know what is coming next or when. Students refresh the page daily, sometimes for weeks, not knowing whether to wait or prepare.

---

## The Solution

NTA Exam Tracker gives students a personalized exam journey map:

- Select your **exam** (JEE Main, NEET, or CUET)
- Select your **current stage** (Applied, Admit Card Released, Exam Done, Answer Key Out)
- See **predicted upcoming milestones** with estimated dates
- See **confidence scores** based on historical NTA patterns
- Get **stage-specific readiness guidance** — exactly what to do right now
- Hit **Refresh Plan** to regenerate the AI-assisted prediction

---

## How It Works

```
Synthetic NTA historical pattern data (2019–2024)
        ↓
Groq AI analyzes patterns and generates predictions
        ↓
Predicted milestones + confidence scores
        ↓
Stage-specific actionable readiness guidance
```

The app uses synthetic historical data reflecting NTA exam cycles from 2019 to 2024. Groq AI analyzes these patterns to generate personalized milestone predictions with confidence percentages. Confidence tapers as predictions extend further into the future.

---

## ⚠️ Important Disclaimer

- All predicted dates are **estimates only**, based on synthetic historical NTA patterns
- These are **not official NTA notices or announcements**
- This is an **independent student project**
- It is **not affiliated with, endorsed by, or operated by NTA**
- Always verify dates on the [official NTA website](https://nta.ac.in)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript |
| Backend | FastAPI, Python |
| AI Inference | Groq |
| Containerization | Docker |
| Deployment | Railway |

---

## Codex Usage

GitHub Codex was used as the primary development tool throughout this project. Codex assisted with:

- Scaffolding the FastAPI backend structure and API endpoints
- Building the React frontend component architecture
- Integrating the Groq AI client and prediction pipeline
- Writing the fallback logic for when AI inference is unavailable
- Mobile-responsive UI refinements
- Dockerfile and Railway deployment configuration

Codex accelerated development significantly — the working full-stack prototype was running locally within the first session.

---

## Features

- Personalized exam journey map per student
- AI-assisted milestone predictions (Groq)
- Confidence scores on future predictions
- Historical-pattern-based estimates (2019–2024)
- Stage-specific readiness guidance
- Supports JEE Main, NEET, and CUET
- Responsive mobile UI
- Graceful fallback when AI inference is unavailable

---

## Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

Create `backend/.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:8000`

---

## Deployment (Railway)

1. Push repository to GitHub
2. Create new Railway project → Deploy from GitHub repo
3. Add environment variable in Railway dashboard:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```
4. Railway uses the `Dockerfile` and `railway.json` automatically
5. Deployment completes and live URL is assigned

---

## Project Structure

```
BWMI/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, routes
│   │   ├── predictor.py     # Groq AI integration + fallback
│   │   └── exam_data.py     # Synthetic NTA historical patterns
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   └── main.tsx         # React app
│   └── package.json
├── railway.json
└── README.md
```

---

## Future Improvements

- Real-time NTA notice monitoring
- Push notifications when a new stage is detected
- Expanded exam coverage (GATE, CUET-PG, state board exams)
- Student account to track multiple exams simultaneously

---

## Submission — Build What Moves India Hackathon

- **Hackathon:** Build What Moves India
- **Live URL:** https://bwmi-production.up.railway.app/
- **Repository:** https://github.com/Mufeed06-cmd/BWMI
- **Built with:** GitHub Codex + Groq AI

---

*This project was built as part of the Build What Moves India hackathon. It is an independent student project and is not affiliated with or endorsed by NTA.