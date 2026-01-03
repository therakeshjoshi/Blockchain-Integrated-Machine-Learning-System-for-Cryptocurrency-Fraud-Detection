// SPDX-License-Identifier: MIT
pragma solidity ^0.8.3;

contract DigitalNotebook {

    struct Note {
        string message; 
        uint timestamp;   
    }

    mapping(address => Note[]) private userNotes;  
    uint public totalNotes;                      

    function addNote(string calldata _message) external {
        Note memory newNote = Note({
            message: _message,
            timestamp: block.timestamp
        });

        userNotes[msg.sender].push(newNote);  
        totalNotes++;                        
    }

   
    function getNotes() external view returns (Note[] memory) {
        return userNotes[msg.sender];
    }
}
