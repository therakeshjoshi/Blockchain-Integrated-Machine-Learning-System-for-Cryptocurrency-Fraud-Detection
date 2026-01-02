// SPDX-License-Identifier: MIT
pragma solidity ^0.8.3;
// Array - dynamic or fxed size
//Initialization
//Insert (push), get, update, delete, pop, length
//Creating array in memory
//Returning array from function

contract Array {
    uint[] public nums = [1, 2, 3];//dynamic
    uint[4] public numsFixedSize = [4, 5, 6, 7]; //fixed size

    function examples() external {
        nums.push(4); //[1,2,3 4]
        uint x = nums[1];
        nums[2] = 777; // [1, 2, 777, 4]
        delete nums[1];//[1, 0, 777, 4]
        nums.pop(); //[1, 0, 777]
        nums.length;

        //createing array in memory
        uint[] memory a = new uint[](5); //fixed size
    }
    function returnArray() external view returns (uint[] memory){
        return nums;
    }

}