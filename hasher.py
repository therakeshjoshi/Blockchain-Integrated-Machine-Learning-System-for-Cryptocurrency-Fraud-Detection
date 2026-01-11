import hashlib
import json

def generate_hash(transaction_data):
    clean_data = {}
    for key, value in transaction_data.items():
        if hasattr(value, 'item'): 
            value = value.item()
        clean_data[key] = value
      
    transaction_string = json.dumps(clean_data, sort_keys=True)
    
   
    encoded_transaction = transaction_string.encode('utf-8')
    hash_object = hashlib.sha256(encoded_transaction)
    hex_dig = hash_object.hexdigest()
    
    return "0x" + hex_dig  

if __name__ == "__main__":
  
    sample_tx = {
        'TimeStamp': 1529873859,
        'Value': 0.5,
        'minValReceived': 0.01,
        'totalTransactions': 12
    }
    
    fingerprint = generate_hash(sample_tx)
    print(f"Input Data: {sample_tx}")
    print(f"Generated SHA-256 Hash: {fingerprint}")
