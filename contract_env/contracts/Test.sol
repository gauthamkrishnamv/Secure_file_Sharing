// SPDX-License-Identifier: MIT

// pragma solidity >=0.5.0;
pragma solidity >=0.8.0;


contract Test {
    struct Prop {
        uint i;
        string f;
    }
    enum Permission{DEFAULT, READ, WRITE, INVITE}

    Prop[] public list;
    uint8 public num;
    uint32 public limit = 0;
    uint randNonce = 0;
    mapping(uint => string) public testMap;

    constructor() {
        num = 0;
        testMap[1] = 'hello world';
        // limit = 1 / 3;
    }

    event Random(uint number);
    function randomNumber() public returns(uint) {
        randNonce++;
        uint rnum =  uint(keccak256(abi.encodePacked(block.timestamp, msg.sender, randNonce)));
        emit Random(rnum);
        return rnum;
    }

    function generateKey() public view returns(bytes32) {
        return sha256(abi.encodePacked(block.timestamp, msg.sender, randNonce));
    }
    
    function getNum() public view returns (uint8) {
        return num;
    }

    function setNum(uint8 _num) public {
        num = _num;
    }

    function addProp(uint i, string memory f) public {
        list.push(Prop(i, f));
    }

    function check(uint32 numerator, uint32 denomenator, uint32 percent) public pure returns (uint256) {
        uint32 q = percent;
        uint256 places = 0;
        while (q != 0) {
            q /= 10;
            places++;
        }
        uint256 result = numerator * 10 ** places / denomenator;
        return result;

    }

    event ReturnedTuple(uint num1, uint num2);
    function returnTuple() public returns (uint num1, uint num2) {
        uint n1 = 2123;
        uint n2 = 352;
        emit ReturnedTuple(n1, n2);
        return (n1, n2);
    }

    event ReturnedMultiple(Prop[] prop);
    function multipleReturn() public pure returns (Prop[] memory, uint32[] memory) {
        uint32[] memory array = new uint32[](10);
        Prop[] memory newArray = new Prop[](10);
        for (uint32 i = 0; i < 10 ; i++ ){
            array[i] = i;
            newArray[i] = Prop(i, "hello");
        }
        // emit ReturnedMultiple(array);
        return (newArray, array);
    }

    function returnEnum() public pure returns(Permission permission){
        return Permission.INVITE;
    }
    // function delProp(uint index) public {
    //     list
    // }


}