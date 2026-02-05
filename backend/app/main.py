from fastapi import FastAPI
from backend.app.api.v1.routes import router as v1_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Incident Decision Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1|\d{1,3}(\.\d{1,3}){3})(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok"}

