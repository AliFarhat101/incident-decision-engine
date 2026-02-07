# Incident Decision Engine

A lightweight ML-powered system that classifies application and CI logs into incident types
and outputs deterministic operational decisions (severity, action, team).

**Stack**: FastAPI, React, TF-IDF + Logistic Regression, DVC, MLflow (via DagsHub)

**Workflow**: feature branches → dev → staging → main
