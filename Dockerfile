FROM python:3.10-slim

WORKDIR /app

# System deps for scientific python wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code + model artifacts + feature-column source of truth
COPY serve_api.py train_mlflow.py ./
COPY random_forest_fraud_model.pkl ./random_forest_fraud_model.pkl

ENV MODEL_PATH=/app/random_forest_fraud_model.pkl
ENV MLFLOW_TRACKING_URI=http://mlflow:5000
# Leave MLFLOW_MODEL_URI unset to fall back to the local .pkl by default;
# set it (e.g. models:/fraud_random_forest/Production) to serve from the
# MLflow Model Registry instead.

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "serve_api:app", "--host", "0.0.0.0", "--port", "8000"]
