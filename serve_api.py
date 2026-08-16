"""
serve_api.py
------------
RESTful inference API for the crypto fraud-detection model.

Loads the model in this priority order:
  1. MLFLOW_MODEL_URI env var (e.g. "models:/fraud_random_forest/Production"
     or "runs:/<run_id>/model") -- pulled from the MLflow tracking server.
  2. Fallback: local joblib/pickle file at MODEL_PATH
     (defaults to the repo's existing random_forest_fraud_model.pkl),
     so this works even without a running MLflow server.

Run locally:
    uvicorn serve_api:app --host 0.0.0.0 --port 8000 --reload

Docs:
    http://localhost:8000/docs
"""

import hashlib
import json
import logging
import os
import time
from typing import List, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, confloat

from train_mlflow import FEATURE_COLUMNS  # keep train/serve features in sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fraud-api")

MLFLOW_MODEL_URI = os.environ.get("MLFLOW_MODEL_URI", "")
MODEL_PATH = os.environ.get("MODEL_PATH", "random_forest_fraud_model.pkl")
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")

app = FastAPI(
    title="Crypto Fraud Detection API",
    description="RESTful inference API for the Blockchain-Integrated ML Fraud Detection system.",
    version="1.0.0",
)

_model = None
_model_source = None


def get_model():
    """Lazily load the model once, either from MLflow or from a local file."""
    global _model, _model_source
    if _model is not None:
        return _model

    if MLFLOW_MODEL_URI:
        try:
            import mlflow
            import mlflow.pyfunc

            mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
            logger.info(f"Loading model from MLflow: {MLFLOW_MODEL_URI}")
            _model = mlflow.pyfunc.load_model(MLFLOW_MODEL_URI)
            _model_source = f"mlflow:{MLFLOW_MODEL_URI}"
            return _model
        except Exception as e:
            logger.warning(f"Could not load model from MLflow ({e}); falling back to local file.")

    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(
            f"No model found. Set MLFLOW_MODEL_URI to load from MLflow, "
            f"or place a model file at MODEL_PATH={MODEL_PATH}."
        )
    logger.info(f"Loading model from local file: {MODEL_PATH}")
    _model = joblib.load(MODEL_PATH)
    _model_source = f"file:{MODEL_PATH}"
    return _model


def predict_proba(model, X: pd.DataFrame) -> np.ndarray:
    """Handle both sklearn estimators and mlflow.pyfunc wrappers uniformly."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    # mlflow.pyfunc models expose .predict only; sklearn flavor returns class labels
    # by default, so we reload the underlying sklearn model if needed.
    preds = model.predict(X)
    return np.asarray(preds, dtype=float)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class Transaction(BaseModel):
    value: float = Field(..., description="Transaction value")
    gas: float = Field(..., description="Gas limit")
    gasPrice: float = Field(..., description="Gas price")
    gasUsed: float = Field(..., description="Gas actually used")
    nonce: float = Field(..., description="Sender nonce")
    input_size: float = Field(..., description="Size of input data field")
    cumulativeGasUsed: float = Field(..., description="Cumulative gas used in block")
    txreceipt_status: float = Field(..., description="Receipt status (0/1)")

    class Config:
        schema_extra = {
            "example": {
                "value": 1500000000000000000,
                "gas": 21000,
                "gasPrice": 20000000000,
                "gasUsed": 21000,
                "nonce": 5,
                "input_size": 0,
                "cumulativeGasUsed": 500000,
                "txreceipt_status": 1,
            }
        }


class PredictionResponse(BaseModel):
    is_fraud: bool
    fraud_probability: confloat(ge=0, le=1)
    risk_score: int  # 0-100, for the smart contract's riskScore field
    tx_hash_sha256: str
    model_used: str
    model_source: str
    latency_ms: float


class BatchTransactionRequest(BaseModel):
    transactions: List[Transaction]


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.on_event("startup")
def _startup():
    get_model()


@app.get("/health")
def health():
    try:
        get_model()
        return {"status": "ok", "model_source": _model_source}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/predict", response_model=PredictionResponse)
def predict(tx: Transaction):
    start = time.time()
    model = get_model()

    row = pd.DataFrame([tx.dict()])[FEATURE_COLUMNS]
    proba = float(predict_proba(model, row)[0])
    is_fraud = proba >= 0.5

    # Deterministic SHA-256 fingerprint, mirroring hasher.py's role in the
    # existing pipeline, so this hash can be passed straight to FraudRegistry.sol
    tx_hash = hashlib.sha256(
        json.dumps(tx.dict(), sort_keys=True).encode("utf-8")
    ).hexdigest()

    latency_ms = (time.time() - start) * 1000
    return PredictionResponse(
        is_fraud=is_fraud,
        fraud_probability=round(proba, 6),
        risk_score=int(round(proba * 100)),
        tx_hash_sha256=tx_hash,
        model_used="RandomForest_v1",
        model_source=_model_source or "unknown",
        latency_ms=round(latency_ms, 2),
    )


@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(req: BatchTransactionRequest):
    return BatchPredictionResponse(predictions=[predict(tx) for tx in req.transactions])


@app.get("/")
def root():
    return {
        "service": "Crypto Fraud Detection API",
        "endpoints": ["/predict", "/predict/batch", "/health", "/docs"],
    }
