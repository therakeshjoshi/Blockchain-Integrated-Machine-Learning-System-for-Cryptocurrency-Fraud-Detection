
# Blockchain Integrated Machine Learning System for Cryptocurrency Fraud Detection

##  Project Overview
This repository documents the development of a **Blockchain-Integrated Machine Learning System** designed to detect and record fraudulent transactions.

# Ethereum Fraud Detection: AI + Blockchain Audit

## Stack
- Python 3.10+
- Pandas, NumPy, Scikit-learn, XGBoost
- FastAPI
- Streamlit
- Web3.py
- Solidity ^0.8.0
- Ethereum Sepolia Testnet

---

## Structure

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

## ML Pipeline

### Dataset
- Rows: 254,973  
- Features: BlockHeight, TimeStamp, Value  
- Target: isError (0/1)  
- Fraud ratio: ~6.13%

### Preprocessing
- Drop: TxHash, From, To, Index, Unnamed  
- Fill NA: 0  
- Remove zero-variance features  
- Train-test split: 80/20 (stratified)

### Models
- Logistic Regression  
- Random Forest  
- XGBoost  

### Selected Model
- Random Forest  
- n_estimators=100  
- class_weight=balanced  
- F1 ≈ 0.8163  

### Export
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

### Framework
FastAPI + Web3.py  

### Load
joblib.load("random_forest_fraud_model.pkl")  

### Endpoint
POST /analyze  

### Input
timestamp: int  
value: float  
min_val_received: float  
total_transactions: int  

### Output
is_fraud  
confidence  
hash  
etherscan_link  

### Blockchain
- Sepolia RPC  
- PoA middleware  
- Local signing using PRIVATE_KEY  
- Contract call: addRecord()  

---

## Frontend (app.py)

### Framework
Streamlit  

### Features
- User input form  
- Local ML prediction  
- Blockchain write  
- Etherscan link display  

### Safety
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

## Install

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

