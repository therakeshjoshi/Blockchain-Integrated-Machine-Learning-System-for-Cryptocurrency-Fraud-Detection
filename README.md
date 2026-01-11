
# Blockchain-Integrated Machine Learning System for Cryptocurrency Fraud Detection

## Project Overview
This repository contains a production-style implementation of a fraud detection system that integrates machine learning inference with blockchain-based auditability. A supervised learning model is trained on Ethereum transaction data to classify fraudulent activity. Each prediction is cryptographically hashed and immutably recorded on the Ethereum Sepolia test network using a Solidity smart contract.

---

## Technology Stack

- Python 3.10+
- Pandas, NumPy
- Scikit-learn, XGBoost
- FastAPI
- Streamlit
- Web3.py
- Solidity ^0.8.0
- Ethereum Sepolia Testnet (Chain ID: 11155111)

---

## Repository Structure

.
├── training_model.ipynb
├── first_order_df.csv
├── random_forest_fraud_model.pkl
├── fraudRegistry.sol
├── hasher.py
├── main.py
├── app.py
├── .env.example
└── README.md

---

## Machine Learning Pipeline

### Dataset
- Total records: 254,973
- Features: BlockHeight, TimeStamp, Value
- Target: isError (0/1)
- Fraud ratio: ~6.13%

### Preprocessing
- Dropped: TxHash, From, To, Index, Unnamed
- Filled missing values with zero
- Removed zero-variance features
- Train-test split: 80/20 (stratified)

### Model Training
Models evaluated:
- Logistic Regression (balanced)
- Random Forest (balanced)
- XGBoost (scale_pos_weight)

Metrics:
- Accuracy, Precision, Recall, F1, ROC-AUC

Selected Model:
- Random Forest
- n_estimators=100
- class_weight=balanced
- F1 ≈ 0.8163

Export:
random_forest_fraud_model.pkl

---

## Smart Contract (fraudRegistry.sol)

### Struct
FraudRecord {
  bool isFraud;
  uint256 riskScore;
  uint256 timestamp;
  string modelUsed;
  address reporter;
  bool exists;
}

### Storage
mapping(bytes32 => FraudRecord) registry;

### Functions
addRecord(bytes32, bool, uint256, string)
getRecord(bytes32)

### Network
- Sepolia Testnet
- Chain ID: 11155111

---

## Hashing (hasher.py)

SHA256(sorted JSON(transaction_data))
Output: 0x + 64 hex characters

---

## Backend (main.py)

Framework:
- FastAPI + Web3.py

Model Load:
joblib.load("random_forest_fraud_model.pkl")

Endpoint:
POST /analyze

Input:
timestamp: int
value: float
min_val_received: float
total_transactions: int

Output:
is_fraud
confidence
hash
etherscan_link

Blockchain:
- Sepolia RPC
- PoA middleware
- Local signing with PRIVATE_KEY
- Contract call: addRecord()

---

## Frontend (app.py)

Framework:
- Streamlit

Features:
- Transaction input form
- Local ML inference
- Blockchain write
- Etherscan link display

Safety:
- Forced Sepolia RPC
- Chain ID check: 11155111
- Self-healing model fallback

---

## Environment

.env
RPC_URL=
PRIVATE_KEY=
CONTRACT_ADDRESS=

---

## Installation

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

---

## Run

Backend:
python main.py

Frontend:
streamlit run app.py

---

## Flow

User Input → ML Prediction → SHA256 → Smart Contract → Sepolia → Etherscan
```
