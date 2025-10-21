// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

import "./Group.sol";

contract User{
    struct GroupInviteInfo {
        string groupName;
        address groupAddress;
        Group.Permission permission;
        string encryptedKey;
    }

    address public fileAppAddress;
    string public username;
    string public ipfsId;
    string public publicKey;
    address public owner;
    address[] public groups;  //stores address of group contracts
    mapping(address => GroupInviteInfo) private groupInvites;
    address[] private groupInvitesList;

    constructor(address _fileAppAddress, string memory _username, string memory _ipfsId, address _owner, string memory _publicKey) {
        fileAppAddress = _fileAppAddress;
        username = _username;
        ipfsId = _ipfsId;
        owner = _owner;
        publicKey = _publicKey;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can access this function");
        _;
    }

    event GroupCreated(address groupAddress);
    function createGroup(
        string memory _groupName, 
        uint32 consensusThreshold, 
        uint256 precision, 
        string memory ipfsCid,
        string memory encryptedKey
    ) onlyOwner public returns (address) {
        Group groupInstace = new Group(fileAppAddress, _groupName, msg.sender, consensusThreshold, precision, ipfsCid, encryptedKey);
        address groupAddress = address(groupInstace);
        groups.push(groupAddress);
        emit GroupCreated(groupAddress);
        return groupAddress;
    }

    function getGroups() onlyOwner public view returns (address[] memory) {
        return groups;
    }

    event newInvite(string groupName, address indexed groupAddress, Group.Permission permission, string encryptedKey);
    function addGroupInvite(address groupAddress, string memory groupName, Group.Permission permission, string memory encryptedKey) public {
        groupInvites[groupAddress] = GroupInviteInfo(groupName, groupAddress, permission, encryptedKey);
        groupInvitesList.push(groupAddress);
        emit newInvite(groupName, groupAddress, permission, encryptedKey);
    }

    function rejectInvite(address groupAddress) onlyOwner public {
        delete groupInvites[groupAddress];
        for (uint i = 0; i < groupInvitesList.length; i++) {
            if (groupInvitesList[i] == groupAddress) {
                groupInvitesList[i] = groupInvitesList[groupInvitesList.length-1];
                groupInvitesList.pop();
                break;
            }
        }
    }

    event InviteAccepted(string key);
    function acceptInvite(address groupAddress) onlyOwner public returns (string memory){
        groups.push(groupAddress);
        delete groupInvites[groupAddress];
        for (uint i = 0; i < groupInvitesList.length; i++) {
            if (groupInvitesList[i] == groupAddress) {
                groupInvitesList[i] = groupInvitesList[groupInvitesList.length-1];
                groupInvitesList.pop();
                break;
            }
        }
        Group groupInstance = Group(groupAddress);
        string memory key = groupInstance.inviteAccepted(msg.sender);
        emit InviteAccepted(key);
        return key;
    }

    function getGroupInvites() onlyOwner public view returns (GroupInviteInfo[] memory) {
        GroupInviteInfo[] memory groupInvitesInfos = new GroupInviteInfo[](groupInvitesList.length);
        for (uint i = 0; i < groupInvitesList.length; i++) {
            groupInvitesInfos[i] = groupInvites[groupInvitesList[i]];
        }
        return groupInvitesInfos;
    }

    function leaveGroup(address groupAddress) onlyOwner public {
        for (uint i = 0; i < groups.length; i++) {
            if (groups[i] == groupAddress) {
                groups[i] = groups[groups.length-1];
                groups.pop();
                break;
            }
        }

        Group groupInstance = Group(groupAddress);
        groupInstance.removeMember(address(this));
    }

    function propose(address groupAddress, string memory change, string memory cid) onlyOwner public {
        Group groupInstance = Group(groupAddress);
        groupInstance.newProposal(address(this), change, cid);
    }

    function leaveApp() onlyOwner public {}

}
        // require(groupInvites[groupAddress].permission != Group.Permission.DEFAULT, "Already invited");