# MLOps additions: MLflow + Docker + REST API

Files to drop into the root of your repo:

- `train_mlflow.py` — trains the RandomForest and logs params/metrics/plots/model to MLflow
- `serve_api.py` — FastAPI REST inference service
- `Dockerfile` — containerizes the API
- `docker-compose.yml` — runs MLflow tracking server + API together
- `requirements.txt` — merge into your existing requirements

## 1. Before running: fix `FEATURE_COLUMNS`

Open `train_mlflow.py`, edit the `FEATURE_COLUMNS` list (top of file) to
exactly match the columns your `training_the_model.ipynb` uses to train
`random_forest_fraud_model.pkl`. `serve_api.py` imports this same list so
training and serving never drift apart. Also update the `Transaction`
pydantic model in `serve_api.py` to match if the field names differ.

## 2. Train with MLflow tracking

```bash
pip install -r requirements.txt

# start the tracking server
mlflow server --host 0.0.0.0 --port 5000 \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlruns

# in another terminal
python train_mlflow.py --data path/to/ethereum_transactions.csv
```

Open http://localhost:5000 to see runs, metrics (accuracy/precision/recall/
F1/ROC-AUC), the confusion matrix, feature-importance plot, and the
registered model `fraud_random_forest`.

## 3. Run the API locally (no Docker)

```bash
uvicorn serve_api:app --host 0.0.0.0 --port 8000 --reload
```

Test:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"value":1.5e18,"gas":21000,"gasPrice":2e10,"gasUsed":21000,
       "nonce":5,"input_size":0,"cumulativeGasUsed":500000,"txreceipt_status":1}'
```

Docs UI: http://localhost:8000/docs

## 4. Run everything containerized

```bash
docker compose up --build
```

This starts:
- `mlflow` on port **5000**
- `fraud-api` on port **8000** (loads the local `.pkl` by default; set
  `MLFLOW_MODEL_URI=models:/fraud_random_forest/Production` in
  `docker-compose.yml` to instead serve straight from the registry)

## 5. Wiring into the rest of the pipeline

`/predict` already returns a `tx_hash_sha256` field computed the same way
`hasher.py` does, plus `risk_score` (0–100) matching `FraudRecord.riskScore`
in `FraudRegistry.sol` — so `main.py` (or your Streamlit app) can call this
API instead of loading the pickle directly, then pass `is_fraud`,
`risk_score`, and `tx_hash_sha256` straight into the smart-contract call.
