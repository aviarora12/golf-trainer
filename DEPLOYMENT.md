# Deployment

SwingCheck has two deployable pieces:

| Piece | Host | Why |
|-------|------|-----|
| **Frontend** (Expo web SPA) | Vercel | Static site served from `frontend/dist` |
| **Backend** (FastAPI + Celery + Redis + Postgres) | Render | Long-running services Vercel can't host |

CI (`.github/workflows/ci.yml`) runs the backend pytest suite and the frontend
web build on every PR and push to `main`.

---

## 1. Backend on Render

The repo ships a blueprint at [`render.yaml`](./render.yaml) that provisions
everything together:

- **web** — FastAPI API (Docker, health check `/health`)
- **worker** — Celery worker (`celery -A app.tasks.celery_tasks worker`)
- **redis** — internal Redis (Celery broker/result backend)
- **postgres** — managed `swingcheck_db`

### Steps

1. In the Render dashboard: **New → Blueprint** and select this repository.
2. Render reads `render.yaml` and creates the web service, worker, Redis, and
   Postgres. `DATABASE_URL` and `REDIS_URL` are wired automatically; `SECRET_KEY`
   is auto-generated.
3. Fill in the secrets marked `sync: false` (dashboard → each service → Environment):

   | Variable | Needed by | Notes |
   |----------|-----------|-------|
   | `AWS_ACCESS_KEY_ID` | web, worker | S3 video/report storage |
   | `AWS_SECRET_ACCESS_KEY` | web, worker | |
   | `AWS_S3_BUCKET` | web, worker | e.g. `swingcheck-videos` |
   | `AWS_REGION` | web, worker | defaults to `us-west-2` |
   | `STRIPE_SECRET_KEY` | web | Phase 2 (payments) |
   | `SENDGRID_API_KEY` | web | magic-link email; if unset, links are logged |

4. Deploy. The API will be live at `https://<your-web-service>.onrender.com`
   (verify with `GET /health` → `{"status":"healthy"}`).

> The worker and web share the same Docker image (`backend/Dockerfile`); the
> worker just overrides the start command. Both must have the AWS + Redis +
> Postgres env vars to process swings end to end.

---

## 2. Frontend on Vercel

Configured by [`frontend/vercel.json`](./frontend/vercel.json) — builds the Expo
web export (`npx expo export -p web`) into `dist` and serves it as an SPA.

### Steps

1. In Vercel, import this repository.
2. Set **Root Directory** to `frontend` (Settings → General). This is required —
   without it Vercel builds the repo root and fails.
3. Add the environment variable:

   | Variable | Value |
   |----------|-------|
   | `EXPO_PUBLIC_API_URL` | your Render API URL, e.g. `https://swingcheck-api.onrender.com` |

4. Deploy. The build command and output dir come from `vercel.json`.

---

## 3. Wiring them together

The frontend reads the backend URL from `EXPO_PUBLIC_API_URL` at build time
(see `frontend/src/services/api.js`). After both are deployed:

1. Set `EXPO_PUBLIC_API_URL` in Vercel to the Render API URL.
2. **Redeploy the frontend** so the new value is baked into the bundle.
3. (CORS) The backend currently allows all origins (`allow_origins=["*"]` in
   `backend/main.py`). Tighten this to the Vercel domain before going to
   production.

Until `EXPO_PUBLIC_API_URL` is set, the deployed web app loads but its
upload/analyze calls fall back to `http://localhost:8000` and won't resolve.

---

## Local development

See the root [`README.md`](./README.md) for running Postgres + Redis (Docker),
the API, the Celery worker, and the Expo app locally. Run backend tests with:

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```
