// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

contract StateVariables {
    uint public myUint = 123;

    function foo() external returns (uint) {
        uint notStateVariable = 456;
        return notStateVariable;
    }
}