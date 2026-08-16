"""
train_mlflow.py
----------------
Trains (or re-trains) the Random Forest fraud-detection model used in
Blockchain-Integrated-Machine-Learning-System-for-Cryptocurrency-Fraud-Detection,
tracking every run with MLflow: params, metrics, confusion matrix,
feature importance plot, and the model artifact itself (registered
in the MLflow Model Registry).

USAGE
-----
    # 1. Start a local MLflow tracking server (in a separate terminal):
    mlflow server --host 0.0.0.0 --port 5000 \
        --backend-store-uri sqlite:///mlflow.db \
        --default-artifact-root ./mlruns

    # 2. Run training:
    python train_mlflow.py --data data/ethereum_transactions.csv

    # 3. Open the UI:
    http://localhost:5000

NOTE ON FEATURE_COLUMNS
------------------------
Update FEATURE_COLUMNS below to match the exact columns used in
`training_the_model.ipynb`. The values here are placeholders based on
the README (Ethereum tx dataset, target = isError). Keeping this list
consistent between training and serving is critical -- serve_api.py
imports it from this file so both stay in sync.
"""

import argparse
import os

import joblib
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# EDIT THIS to match your actual training notebook's feature set exactly.
# ---------------------------------------------------------------------------
FEATURE_COLUMNS = [
    "value",
    "gas",
    "gasPrice",
    "gasUsed",
    "nonce",
    "input_size",
    "cumulativeGasUsed",
    "txreceipt_status",
]
TARGET_COLUMN = "isError"

MLFLOW_EXPERIMENT_NAME = "crypto-fraud-detection"
MLFLOW_MODEL_ARTIFACT_PATH = "model"
REGISTERED_MODEL_NAME = "fraud_random_forest"


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    missing = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c not in df.columns]
    if missing:
        raise ValueError(
            f"Dataset is missing expected columns: {missing}. "
            f"Update FEATURE_COLUMNS in train_mlflow.py to match your dataset."
        )
    return df


def build_plots(y_test, y_pred, model, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay(cm, display_labels=["Legit", "Fraud"]).plot(ax=ax, cmap="Blues")
    ax.set_title("Confusion Matrix")
    cm_path = os.path.join(out_dir, "confusion_matrix.png")
    fig.tight_layout()
    fig.savefig(cm_path)
    plt.close(fig)

    # Feature importance
    importances = pd.Series(model.feature_importances_, index=FEATURE_COLUMNS).sort_values()
    fig, ax = plt.subplots(figsize=(6, 4))
    importances.plot(kind="barh", ax=ax, color="steelblue")
    ax.set_title("Feature Importance")
    fi_path = os.path.join(out_dir, "feature_importance.png")
    fig.tight_layout()
    fig.savefig(fi_path)
    plt.close(fig)

    return cm_path, fi_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to training CSV")
    parser.add_argument("--n_estimators", type=int, default=100)
    parser.add_argument("--max_depth", type=int, default=None)
    parser.add_argument("--test_size", type=float, default=0.2)
    parser.add_argument("--random_state", type=int, default=42)
    parser.add_argument(
        "--tracking_uri",
        default=os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"),
        help="MLflow tracking server URI",
    )
    parser.add_argument("--out_model_path", default="artifacts/random_forest_fraud_model.pkl")
    args = parser.parse_args()

    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    df = load_data(args.data)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y
    )

    with mlflow.start_run() as run:
        params = dict(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            class_weight="balanced",
            random_state=args.random_state,
        )
        mlflow.log_params(params)
        mlflow.log_param("test_size", args.test_size)
        mlflow.log_param("n_features", len(FEATURE_COLUMNS))
        mlflow.log_param("features", ",".join(FEATURE_COLUMNS))

        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba),
        }
        mlflow.log_metrics(metrics)
        print("Metrics:", metrics)

        cm_path, fi_path = build_plots(y_test, y_pred, model, out_dir="mlflow_plots")
        mlflow.log_artifact(cm_path)
        mlflow.log_artifact(fi_path)

        # Log + register the model with MLflow (this is what serve_api.py loads)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path=MLFLOW_MODEL_ARTIFACT_PATH,
            registered_model_name=REGISTERED_MODEL_NAME,
        )

        # Also drop a plain joblib copy so the existing app.py / repo layout
        # keeps working unchanged if it loads random_forest_fraud_model.pkl directly.
        os.makedirs(os.path.dirname(args.out_model_path), exist_ok=True)
        joblib.dump(model, args.out_model_path)
        mlflow.log_artifact(args.out_model_path)

        print(f"\nRun ID: {run.info.run_id}")
        print(f"Model URI: runs:/{run.info.run_id}/{MLFLOW_MODEL_ARTIFACT_PATH}")
        print(f"Registered as: {REGISTERED_MODEL_NAME}")


if __name__ == "__main__":
    main()
