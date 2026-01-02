// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;
//Data types - values and references
contract ValueTypes {
    bool public b = true;
    uint public u = 123; //unit is a 256 bit unsigned integer
    int public i =  - 123;
    int public j = 123;
    int public minInt = type(int).min;
    int public maxInt = type(int).max;
    address public addr = 0x5B38Da6a701c568545dCfcB03FcB875f56beddC4;
}