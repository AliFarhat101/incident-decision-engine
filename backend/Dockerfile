FROM python:3.10-slim

WORKDIR /app

# System deps (small, safe)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy source
COPY backend /app/backend

# Expose API port
EXPOSE 8000

# Run
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

