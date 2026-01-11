import os
import json
import hashlib
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# 2. Connect to Blockchain (Sepolia)
web3 = Web3(Web3.HTTPProvider(RPC_URL))
# Fix for Web3.py v7.0+ (Required for Sepolia)
web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

if web3.is_connected():
    print(f" Connected to Sepolia. Block: {web3.eth.block_number}")
else:
    print(" Failed to connect to Sepolia.")

account = web3.eth.account.from_key(PRIVATE_KEY)
SENDER_ADDRESS = account.address

# 3. Load AI Model
# Note: Ensure 'random_forest_fraud_model.pkl' is in the SAME folder as this file.
try:
    model = joblib.load('random_forest_fraud_model.pkl')
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Did you run the fix script? The server will run, but predictions will fail.")

# 4. Smart Contract Configuration
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "_dataHash", "type": "bytes32"},
            {"internalType": "bool", "name": "_isFraud", "type": "bool"},
            {"internalType": "uint256", "name": "_riskScore", "type": "uint256"},
            {"internalType": "string", "name": "_modelUsed", "type": "string"}
        ],
        "name": "addRecord",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# 5. API Logic
app = FastAPI()

class TransactionRequest(BaseModel):
    timestamp: int
    value: float
    min_val_received: float
    total_transactions: int

@app.get("/")
def home():
    return {"status": "Online", "network": "Sepolia"}

@app.post("/analyze")
async def analyze_transaction(tx: TransactionRequest):
    try:
        # A. Format Data for AI
        input_data = pd.DataFrame([{
            'TimeStamp': tx.timestamp,
            'Value': tx.value,
            'minValReceived': tx.min_val_received,
            'totalTransactions': tx.total_transactions
        }])
        
        # B. Make Prediction
        prediction = int(model.predict(input_data)[0])
        confidence = float(model.predict_proba(input_data)[0][1])
        is_fraud = bool(prediction == 1)

        # C. Generate Hash
        tx_json = json.dumps(tx.dict(), sort_keys=True).encode('utf-8')
        data_hash = "0x" + hashlib.sha256(tx_json).hexdigest()

        # D. Write to Blockchain
        print(f"🔗 Sending transaction... (Fraud: {is_fraud})")
        nonce = web3.eth.get_transaction_count(SENDER_ADDRESS)
        
        tx_call = contract.functions.addRecord(
            data_hash,
            is_fraud,
            int(confidence * 100),
            "RandomForest_Remote_v1"
        ).build_transaction({
            'chainId': 11155111,  # Sepolia ID
            'gas': 200000,
            'maxFeePerGas': web3.to_wei('50', 'gwei'),
            'maxPriorityFeePerGas': web3.to_wei('2', 'gwei'),
            'nonce': nonce,
        })
        
        signed_tx = web3.eth.account.sign_transaction(tx_call, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"Sent! Hash: {web3.to_hex(tx_hash)}")
        
        return {
            "status": "Success",
            "is_fraud": is_fraud,
            "confidence": f"{confidence*100:.2f}%",
            "hash": data_hash,
            "tx_link": f"https://sepolia.etherscan.io/tx/{web3.to_hex(tx_hash)}"
        }

    except Exception as e:
        print(f" Error: {e}")
        raise HTTPException(status_code=500)