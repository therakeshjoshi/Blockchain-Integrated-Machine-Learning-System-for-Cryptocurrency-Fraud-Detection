// SPDX-License-Identifier: MIT
pragma solidity ^0.8.3;

contract DigitalNotebook {
    mapping(address => string[]) private notes;


    function addNote(string calldata _note) external {
    notes[msg.sender].push(_note);
}

function getMyNotes() external view returns (string[] memory) {
    return notes[msg.sender];
}





}