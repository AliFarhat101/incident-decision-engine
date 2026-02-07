# Deployment

## Backend (Docker image)
The backend is containerized and pushed to DockerHub on merges to `staging`.

- Health: `/health`
- Predict: `POST /api/v1/predict`

### DockerHub
Image:
- `afarhat101/incident-decision-engine-backend:staging`
- `afarhat101/incident-decision-engine-backend:<commit_sha>`

## Frontend (Vercel)
Frontend is deployed on Vercel and points to the public backend URL via env var:

- `VITE_API_BASE=<PUBLIC_BACKEND_URL>`
- `VITE_SUPABASE_URL=<...>`
- `VITE_SUPABASE_ANON_KEY=<...>`

