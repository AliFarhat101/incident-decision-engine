# Incident Decision Engine (LIDE)

A production-style **Machine Learning in Production** project that classifies incident logs and outputs **structured, deterministic decisions** suitable for automation (no free-text explanations).

---

## Live URLs

- **Frontend (Netlify):** https://lide-lb.netlify.app  
- **Backend (Render):** https://incident-decision-engine-backend.onrender.com  

Quick checks:
- `GET /health` → https://incident-decision-engine-backend.onrender.com/health  
- `POST /api/v1/predict` → https://incident-decision-engine-backend.onrender.com/api/v1/predict  

---

## What it does

Input: a log line / error message (CI logs, application logs, service errors)

Output (JSON):
- `incident_type` (db_error, timeout, config, auth, unknown)
- `severity`
- `action`
- `team`
- `confidence`

The goal is **automation-readiness** (routing, alerts, runbooks), not explanation.

---

## Architecture

```
Frontend (React/Vite)  --->  Backend (FastAPI)
                                 |
                                 +-- ML classifier (TF-IDF + Logistic Regression)
                                 +-- Rule-based fallback (safe if model missing)
                                 |
                                 +-- Decision mapping (type -> severity/action/team)
                                 |
                                 +-- Optional: Supabase history (frontend writes)
```

---

## Data, versions, and model

### Dataset
- Base dataset: HDFS logs (published dataset)
- Processed into incident examples and labels

### Data versioning (DVC)
We maintain versioned processed datasets:
- `incidents_v1.csv` (baseline coverage)
- `incidents_v2.csv` (+200–500 synthetic variants per class for robustness)

### Model
- TF-IDF + Logistic Regression
- Evaluation uses **group-based split** to reduce template leakage
- Metrics tracked: accuracy, macro F1

---

## Experiment tracking (MLflow on DagsHub)

Tracking UI:
- https://dagshub.com/AliFarhat101/incident-decision-engine.mlflow

Runs:
- `v1_group_split`
- `v2_group_split`

Artifacts logged:
- model (`incident_clf.joblib`)
- metadata (`model_meta.json`)

See: `docs/mlflow.md`

---

## Testing

Project requirement satisfied:
- **Unit tests:** 3
- **Integration tests:** 3
- **E2E tests:** 3 (Playwright)

Run backend tests:
```bash
pytest -q
```

Run frontend E2E tests:
```bash
cd frontend
npx playwright test
```

---

## CI/CD & Docker

- GitHub Actions runs tests on PRs (branch protection enabled)
- Backend is containerized and pushed to DockerHub on merges to `staging`

DockerHub image:
- `afarhat101/incident-decision-engine-backend:staging`
- `afarhat101/incident-decision-engine-backend:<commit_sha>`

---

## How to run locally

### Backend (Docker)
```bash
docker compose up --build
```

### Frontend (dev)
Create `frontend/.env.local` (do not commit):
```env
VITE_API_BASE=http://localhost:8000
VITE_SUPABASE_URL=YOUR_SUPABASE_URL
VITE_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
```

Run:
```bash
cd frontend
npm install
npm run dev -- --host
```

---

## Team & collaboration

Developed by a team of 2 with visible collaboration:
- feature branches
- PRs and reviews
- protected branches (`dev` → `staging` → `main`)
- CI checks gating merges

---

## Notes (security & production)
- CORS is explicitly allowlisted for the deployed frontend origin.
- Supabase policies are configured for demo use; production would add auth and stricter RLS.

# Incident Decision Engine (LIDE)

A production-style **Machine Learning in Production** project that classifies incident logs and outputs **structured, deterministic decisions** suitable for automation (no free-text explanations).

---

## Live URLs

- **Frontend (Netlify):** https://lide-lb.netlify.app  
- **Backend (Render):** https://incident-decision-engine-backend.onrender.com  

Quick checks:
- `GET /health` → https://incident-decision-engine-backend.onrender.com/health  
- `POST /api/v1/predict` → https://incident-decision-engine-backend.onrender.com/api/v1/predict  

---

## What it does

Input: a log line / error message (CI logs, application logs, service errors)

Output (JSON):
- `incident_type` (db_error, timeout, config, auth, unknown)
- `severity`
- `action`
- `team`
- `confidence`

The goal is **automation-readiness** (routing, alerts, runbooks), not explanation.

---

## Architecture

```
Frontend (React/Vite)  --->  Backend (FastAPI)
                                 |
                                 +-- ML classifier (TF-IDF + Logistic Regression)
                                 +-- Rule-based fallback (safe if model missing)
                                 |
                                 +-- Decision mapping (type -> severity/action/team)
                                 |
                                 +-- Optional: Supabase history (frontend writes)
```

---

## Data, versions, and model

### Dataset
- Base dataset: HDFS logs (published dataset)
- Processed into incident examples and labels

### Data versioning (DVC)
We maintain versioned processed datasets:
- `incidents_v1.csv` (baseline coverage)
- `incidents_v2.csv` (+200–500 synthetic variants per class for robustness)

### Model
- TF-IDF + Logistic Regression
- Evaluation uses **group-based split** to reduce template leakage
- Metrics tracked: accuracy, macro F1

---

## Experiment tracking (MLflow on DagsHub)

Tracking UI:
- https://dagshub.com/AliFarhat101/incident-decision-engine.mlflow

Runs:
- `v1_group_split`
- `v2_group_split`

Artifacts logged:
- model (`incident_clf.joblib`)
- metadata (`model_meta.json`)

See: `docs/mlflow.md`

---

## Testing

Project requirement satisfied:
- **Unit tests:** 3
- **Integration tests:** 3
- **E2E tests:** 3 (Playwright)

Run backend tests:
```bash
pytest -q
```

Run frontend E2E tests:
```bash
cd frontend
npx playwright test
```

---

## CI/CD & Docker

- GitHub Actions runs tests on PRs (branch protection enabled)
- Backend is containerized and pushed to DockerHub on merges to `staging`

DockerHub image:
- `afarhat101/incident-decision-engine-backend:staging`
- `afarhat101/incident-decision-engine-backend:<commit_sha>`

---

## How to run locally

### Backend (Docker)
```bash
docker compose up --build
```

### Frontend (dev)
Create `frontend/.env.local` (do not commit):
```env
VITE_API_BASE=http://localhost:8000
VITE_SUPABASE_URL=YOUR_SUPABASE_URL
VITE_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
```

Run:
```bash
cd frontend
npm install
npm run dev -- --host
```

---

## Team & collaboration

Developed by a team of 2 with visible collaboration:
- feature branches
- PRs and reviews
- protected branches (`dev` → `staging` → `main`)
- CI checks gating merges

---

## Notes (security & production)
- CORS is explicitly allowlisted for the deployed frontend origin.
- Supabase policies are configured for demo use; production would add auth and stricter RLS.


