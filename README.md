# SwingCheck

AI golf swing analysis. A golfer uploads a short landscape video; the backend
detects body landmarks with MediaPipe Pose, computes swing biomechanics
(spine angle, hip/shoulder turn, X-Factor, shaft lean), flags mechanical
faults (early extension, reverse pivot, sway, casting, etc.), and generates a
shareable PDF report with drill recommendations.

## Stack

- **Backend:** FastAPI (Python 3.11+), PostgreSQL, Redis, Celery
- **ML / video:** MediaPipe Pose, OpenCV, FFmpeg
- **Storage / payments:** AWS S3, Stripe (Phase 2)
- **Frontend:** React Native (Expo) — single iOS/Android codebase

## Layout

```
backend/    FastAPI app, services (video, pose, analysis, S3, report, email), Celery tasks
frontend/   Expo React Native app (screens, components, navigation, api client)
ml_models/  Reserved for custom models (MediaPipe downloads at runtime)
```

## Deployment

Frontend → Vercel (Expo web), backend → Render (FastAPI + Celery + Redis +
Postgres). See [DEPLOYMENT.md](./DEPLOYMENT.md) for the full walkthrough.

## Local development

### 1. Infrastructure (PostgreSQL + Redis)

```bash
cd backend
cp .env.example .env
docker-compose up -d
```

### 2. Backend API

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py            # http://localhost:8000  (docs at /docs)
```

### 3. Celery worker

```bash
cd backend
celery -A app.tasks.celery_tasks worker --loglevel=info
```

### 4. Frontend

```bash
cd frontend
npm install
npm start                 # press i (iOS) or a (Android)
```

Verify the API:

```bash
curl http://localhost:8000/health   # {"status": "healthy"}
```

## API overview

- `POST /auth/signup` — request a magic-link sign-in
- `POST /auth/verify-magic-link` — verify token, returns user + access token
- `POST /swings/upload` — upload a swing video (multipart), kicks off async analysis
- `GET  /swings/user/all` — list a user's swings
- `GET  /swings/{id}/status` — analysis progress
- `GET  /swings/{id}/report` — completed analysis (angles + flagged issues)
- `GET  /drills` — drill library (filter by `category` / `issue_tag`)
- `GET  /account/{id}` — profile; `PATCH` to update; `/subscription` for plan

## Known limitations (Phase 2)

- Magic-link email only sends when `SENDGRID_API_KEY` is set (otherwise the
  link is logged for local dev). JWTs are placeholders — no real auth yet.
- No Stripe payment processing or webhooks.
- No coach collaboration or progress-tracking dashboard.
- Swing-phase detection uses fixed frame fractions (P1/P4/P7), not a learned
  phase classifier.
