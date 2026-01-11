
# Technical README

## Project: Blockchain Integrated Machine Learning System for Cryptocurrency Fraud Detection

---

## System Objective

Build a production-style system where machine learning performs fraud classification on cryptocurrency transactions and blockchain guarantees immutable storage of the prediction output for audit and verification.

---

## Architecture Overview

Pipeline:

Input Transaction  
→ Feature Formatting  
→ ML Inference  
→ Probability Scoring  
→ SHA-256 Hashing  
→ Smart Contract Call  
→ Ethereum Sepolia Blockchain  
→ Etherscan Verification  

System Layers:
- Machine Learning Layer (Fraud Prediction)
- Hashing Layer (Data Fingerprinting)
- Blockchain Layer (Immutable Storage)
- Application Layer (API + UI)

---

## Data and Features

Dataset: Ethereum transaction records  
Total Rows: 254,973  

Final Features Used:
- BlockHeight
- TimeStamp
- Value

Target Variable:
- isError (0 = Legit, 1 = Fraud)

Class Distribution:
- Fraud ≈ 6.13%
- Legit ≈ 93.87%

---

## Preprocessing

- Drop non-numeric and identifier columns  
- Remove wallet addresses and hashes  
- Fill missing values with 0  
- Remove zero-variance features  
- Normalize feature types  
- Stratified 80/20 train-test split  

---

## Model Training

Models Evaluated:
- Logistic Regression  
- Random Forest  
- XGBoost  

Evaluation Metrics:
- Accuracy  
- Precision  
- Recall  
- F1-Score  
- ROC-AUC  

Best Model:
- Random Forest  
- n_estimators = 100  
- class_weight = balanced  
- F1 ≈ 0.8163  

Model Export:
random_forest_fraud_model.pkl  

---

## Smart Contract Design

File: fraudRegistry.sol  

Record Structure:
FraudRecord {
  bool isFraud;
  uint256 riskScore;
  uint256 timestamp;
  string modelUsed;
  address reporter;
  bool exists;
}

Storage:
mapping(bytes32 => FraudRecord) registry;

Functions:
addRecord(bytes32 dataHash, bool isFraud, uint256 riskScore, string modelUsed)  
getRecord(bytes32 dataHash)  

Properties:
- Duplicate hash prevention  
- Immutable record storage  
- Public visibility  

Network:
Ethereum Sepolia Testnet  
Chain ID: 11155111  

---

## Hashing Logic

File: hasher.py  

Method:
- Convert input to sorted JSON  
- Encode as UTF-8  
- Apply SHA-256  
- Prefix with "0x"  

Output:
0x + 64 hex characters  

Ensures:
- Deterministic fingerprint  
- Tamper detection  
- Blockchain compatibility  

---

## Backend API

File: main.py  
Framework: FastAPI + Web3.py  

Responsibilities:
- Load trained ML model  
- Accept transaction data  
- Predict fraud and confidence  
- Generate SHA-256 hash  
- Build blockchain transaction  
- Sign with PRIVATE_KEY  
- Send to Sepolia  

Endpoint:
POST /analyze  

Input Fields:
timestamp  
value  
min_val_received  
total_transactions  

Output:
is_fraud  
confidence  
hash  
etherscan_link  

Blockchain Configuration:
- Sepolia RPC  
- PoA middleware injection  
- Chain ID validation  
- Contract function: addRecord()  

---

## Frontend

File: app.py  
Framework: Streamlit  

Responsibilities:
- User input interface  
- Local ML prediction  
- Blockchain transaction execution  
- Display transaction status and Etherscan link  

Safety Mechanisms:
- Forced Sepolia RPC  
- Chain ID verification (11155111)  
- Self-healing model fallback if file missing  

---

## Environment Configuration

Create .env file:

RPC_URL=your_sepolia_rpc  
PRIVATE_KEY=your_wallet_private_key  
CONTRACT_ADDRESS=your_deployed_contract  

Never commit private keys.

---

## Installation Guide

### 1. Clone Repository

git clone <repo-url>  
cd <repo-name>  

### 2. Create Virtual Environment

python -m venv venv  
source venv/bin/activate  
# Windows: venv\Scripts\activate  

### 3. Install Dependencies

pip install -r requirements.txt  

---

## Running the System

### Backend

python main.py  

Runs API at:
http://127.0.0.1:8000  

### Frontend

streamlit run app.py  

Access UI at:
http://localhost:8501  

---

## Deployment Flow

1. User submits transaction through UI  
2. ML model predicts fraud  
3. Input hashed with SHA-256  
4. Prediction sent to smart contract  
5. Transaction mined on Sepolia  
6. User verifies via Etherscan  

---

## Verification

Each blockchain record contains:
- Data hash  
- Fraud label  
- Confidence score  
- Model identifier  
- Reporter address  

All records are immutable and publicly auditable.

