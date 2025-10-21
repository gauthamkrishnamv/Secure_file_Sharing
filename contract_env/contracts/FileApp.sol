// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0;

import "./User.sol";

contract FileApp {
    struct UserInfo {
        string username;
        address userAddress;
        address userContractAddress;
        string publicKey;
    }

    mapping(address => address) public user_contractMapping;
    UserInfo[] public userInfos;
    uint64 public length = 0;

    event UserRegistered(string username, address userAddress, address userContractAddress, string publicKey);
    function signUp(string memory _username, string memory _ipfsId, string memory _publicKey) public {
        require(bytes(_username).length > 0, "Username cannot be empty.");
        require(user_contractMapping[msg.sender] == address(0), "Already a User");
        for (uint i = 0; i < length; i++) {
            if (keccak256(abi.encodePacked(userInfos[i].username)) == keccak256(abi.encodePacked(_username))) {
                require(false, "Username exists!");
            }
        }
        address userContractAddress = address(new User(address(this), _username, _ipfsId, msg.sender, _publicKey));
        user_contractMapping[msg.sender] = userContractAddress;
        userInfos.push(UserInfo(_username, msg.sender, userContractAddress, _publicKey));
        length++;
        emit UserRegistered(_username, msg.sender, userContractAddress, _publicKey);
    }

    function getUserContractAddress(address userAddress) public view returns (address) {
        return user_contractMapping[userAddress];
    }

    function getUserInfos() public view returns (UserInfo[] memory) {
        UserInfo[] memory _userInfos = new UserInfo[](userInfos.length);
        for (uint i = 0; i < userInfos.length; i++) {
            _userInfos[i] = userInfos[i];
        }
        return _userInfos;
    }

    function leave() public {
        // require()
        for (uint i=0; i < length; i++) {
            if (msg.sender == userInfos[i].userAddress) {
                delete user_contractMapping[userInfos[i].userAddress];
                userInfos[i] = userInfos[length-1];
                userInfos.pop();
                length--;
                break;
            }
        }
        
    }
}



    // function leave() public {
    //     // require()
    //     for (uint i=0; i < length; i++) {
    //         if (msg.sender == userAddresses[i]) {
    //             delete user_contractMapping[userAddresses[i]];
    //             usernames[i] = usernames[length-1];
    //             usernames.pop();
    //             userAddresses[i] = userAddresses[length-1];
    //             userAddresses.pop();
    //             length--;
    //             break;
    //         }
    //     }
        
    // }

