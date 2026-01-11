// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FraudRegistry {
    
   
    struct FraudRecord {
        bool isFraud;       
        uint256 riskScore;  
        uint256 timestamp;  
        string modelUsed;   
        address reporter;   
        bool exists;        
    }


    mapping(bytes32 => FraudRecord) public registry;


    event RecordAdded(bytes32 indexed dataHash, bool isFraud, uint256 timestamp);

    
    function addRecord(bytes32 _dataHash, bool _isFraud, uint256 _riskScore, string memory _modelUsed) public {
        
        require(!registry[_dataHash].exists, "Record already exists for this hash!");

        registry[_dataHash] = FraudRecord({
            isFraud: _isFraud,
            riskScore: _riskScore,
            timestamp: block.timestamp,
            modelUsed: _modelUsed,
            reporter: msg.sender,
            exists: true
        });

    
        emit RecordAdded(_dataHash, _isFraud, block.timestamp);
    }

    
    function getRecord(bytes32 _dataHash) public view returns (bool, uint256, string memory, address) {
        require(registry[_dataHash].exists, "No record found for this hash");
        
        FraudRecord memory rec = registry[_dataHash];
        return (rec.isFraud, rec.riskScore, rec.modelUsed, rec.reporter);
    }
}