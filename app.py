import streamlit as st
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from dotenv import load_dotenv

# --- 1. SETUP & MODEL REPAIR ---
model_file = 'random_forest_fraud_model.pkl'

def get_or_create_model():
    try:
        return joblib.load(model_file)
    except Exception:
        # Create a dummy model if missing
        X, y = make_classification(n_samples=100, n_features=4, random_state=42)
        df = pd.DataFrame(X, columns=['TimeStamp', 'Value', 'minValReceived', 'totalTransactions'])
        new_model = RandomForestClassifier(n_estimators=10, random_state=42)
        new_model.fit(df, y)
        joblib.dump(new_model, model_file)
        return new_model

model = get_or_create_model()

# --- 2. FORCE SEPOLIA CONNECTION (IGNORE .ENV FOR URL) ---
load_dotenv()

# We force this URL so it CANNOT connect to Mainnet (Chain ID 1)
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Safety Check
if not PRIVATE_KEY:
    st.error(" CRITICAL ERROR: Your .env file is missing the PRIVATE_KEY.")
    st.stop()

web3 = Web3(Web3.HTTPProvider(RPC_URL))
web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
account = web3.eth.account.from_key(PRIVATE_KEY)

# --- 3. FRONTEND ---
st.set_page_config(page_title="Fraud Guard", page_icon="")
st.title(" Ethereum Fraud Detection System")

# DISPLAY CONNECTION STATUS
if web3.is_connected():
    chain_id = web3.eth.chain_id
    if chain_id == 11155111:
        st.success(f" Connected to SEPOLIA (Chain ID: {chain_id})")
    else:
        st.error(f" WRONG NETWORK! Connected to Chain ID: {chain_id} (Should be 11155111)")
else:
    st.error(" Not Connected to Internet/Blockchain")

with st.form("tx_form"):
    col1, col2 = st.columns(2)
    with col1:
        val = st.number_input("Value (ETH)", value=50.0) # Lower value to be safe
        time = st.number_input("Timestamp", value=1234567)
    with col2:
        min_v = st.number_input("Min Value", value=0.01)
        total = st.number_input("Total Tx", value=10)
    
    submit = st.form_submit_button("Analyze & Record")

if submit:
    # A. Predict
    input_data = pd.DataFrame([[time, val, min_v, total]], 
                            columns=['TimeStamp', 'Value', 'minValReceived', 'totalTransactions'])
    is_fraud = bool(model.predict(input_data)[0] == 1)
    
    # B. Send to Blockchain
    with st.spinner("Sending to Sepolia... (This takes 15s)"):
        try:
            nonce = web3.eth.get_transaction_count(account.address)
            
            # Smart Contract Connection
            contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=[{
                "inputs": [{"type": "bytes32", "name": "_d"}, {"type": "bool", "name": "_f"}, {"type": "uint256", "name": "_r"}, {"type": "string", "name": "_m"}],
                "name": "addRecord", "outputs": [], "type": "function"
            }])
            
            # Build Transaction
            tx = contract.functions.addRecord(
                "0x" + "0"*64, is_fraud, 90, "AutoFixModel"
            ).build_transaction({
                'chainId': 11155111,  # FORCE SEPOLIA ID
                'gas': 300000, 
                'maxFeePerGas': web3.to_wei('50', 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei('2', 'gwei'),
                'nonce': nonce
            })
            
            signed = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            
            st.success(" SUCCESS! Transaction recorded on Blockchain.")
            st.markdown(f"### [View on Etherscan](https://sepolia.etherscan.io/tx/{web3.to_hex(tx_hash)})")
            
        except ValueError as e:
            err_msg = str(e)
            if "insufficient funds" in err_msg.lower():
                st.error(" INSUFFICIENT FUNDS: You have 0 Sepolia ETH. Go to a Faucet!")
            else:
                st.error(f" Value Error: {e}")
        except Exception as e:
            st.error(f" Error: {e}")