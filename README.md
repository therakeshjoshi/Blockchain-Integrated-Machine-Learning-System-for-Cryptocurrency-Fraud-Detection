# Blockchain-Integrated Machine Learning System for Cryptocurrency Fraud Detection

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Solidity](https://img.shields.io/badge/Solidity-0.8.0-lightgrey)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.22-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## System Objective
This project builds a production-style system where Machine Learning performs real-time fraud classification on cryptocurrency transactions, while Blockchain technology guarantees the immutable storage of prediction outputs. This ensures a transparent, tamper-proof audit trail for every AI decision made.

## Architecture Overview
The system operates on a four-layer architecture designed for security and verification:

1.  **Machine Learning Layer:** A Random Forest classifier that predicts fraud probability.
2.  **Hashing Layer:** Generates deterministic SHA-256 "fingerprints" of transaction data.
3.  **Blockchain Layer:** Stores the fingerprint and prediction result on the Ethereum Sepolia Testnet.
4.  **Application Layer:** A full-stack interface (Streamlit & FastAPI) for user interaction.

### Workflow Pipeline
Input Transaction -> Feature Formatting -> ML Inference -> Probability Scoring -> SHA-256 Hashing -> Smart Contract Call -> Ethereum Sepolia Blockchain -> Etherscan Verification

## Machine Learning Model
The AI engine is trained on 254,973 Ethereum transaction records to detect anomalous patterns.

* **Dataset:** Ethereum Transaction History
* **Target Variable:** isError (0 = Legit, 1 = Fraud)
* **Class Distribution:** Fraud ~6.13% | Legit ~93.87%
* **Best Model:** Random Forest Classifier
    * n_estimators: 100
    * class_weight: balanced
    * **F1-Score:** ~0.8163

## Smart Contract (The Ledger)
The FraudRegistry.sol contract acts as the immutable registry.

* **Network:** Ethereum Sepolia Testnet
* **Chain ID:** 11155111
* **Storage Structure:**
    ```solidity
    struct FraudRecord {
        bool isFraud;       // AI Prediction
        uint256 riskScore;  // Confidence Score
        uint256 timestamp;  // Time of Analysis
        string modelUsed;   // Model Version (e.g., "RandomForest_v1")
        address reporter;   // Wallet Address of the Reporter
    }
    ```
* **Key Properties:** Duplicate hash prevention, public visibility, and immutable storage.

## Installation & Setup

### Prerequisites
* Python 3.8+
* MetaMask Wallet (funded with Sepolia ETH)
* Alchemy/Infura RPC URL

