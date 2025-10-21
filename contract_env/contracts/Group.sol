// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0;

import "./User.sol";
import "./FileApp.sol";


contract Group{
    enum Status{WAITING, ACCEPTED, REJECTED}
    enum Permission{DEFAULT, READ, WRITE, INVITE}

    struct UserDetails {
        // string username;
        address userAddress;
        address userContractAddress;
        Permission permission;
        string encryptedKey;
        // string publicKey;
    }

    struct Proposal {
        string proposalMessage;
        address userContract;
        string cid;
        uint32 forVotes;
        uint32 againstVotes;
        address[] votedList;
        Status status; 
    }

    struct AP{
        address userContractAddress;
        Permission permission;
    }

    address public fileAppAddress;
    string public groupName;
    address public owner;  // user address
    string private ipfsCid; // encrypted
    mapping(address => UserDetails) private invites; // mapping of user address
    address[] private usersList; // stores the address of users (not contract address)
    mapping(address => UserDetails) private user_userDetails; // user address
    mapping(uint => Proposal) public proposals;
    // uint[] private proposalsList;
    mapping(uint => address[]) private votedList;   // mapping of proposalId to list of user's addressses those who voted
    uint proposalId = 0;
    uint32 consensusThreshold;
    uint256 precision;
    uint16 numVotingRights = 1;

    constructor(
        address _fileAppAddress, 
        string memory _groupName,
        address _userAddress, 
        uint32 _consensusThreshold, 
        uint256 _precision, 
        string memory _ipfsCid, 
        string memory encryptedKey
    ) {
        fileAppAddress = _fileAppAddress;
        groupName = _groupName;
        owner = _userAddress;
        user_userDetails[_userAddress] = UserDetails(_userAddress, msg.sender, Permission.INVITE, encryptedKey);
        usersList.push(_userAddress);
        consensusThreshold = _consensusThreshold;
        precision = _precision;
        ipfsCid = _ipfsCid;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "You are not the Owner!");
        _;
    }  

    modifier onlyMember() {
        require(user_userDetails[msg.sender].permission != Permission.DEFAULT, "Not a member!");
        _;
    }

    function getGroupInfo() onlyMember public view returns (
        string memory _groupName, 
        address _owner, 
        string memory _ipfsCid, 
        // uint _proposalId, 
        uint32 _consensusThreshold
    ) {
        return (groupName, owner, ipfsCid, consensusThreshold);
    }

    function changeConsensusThreshold(uint32 threshold, uint256 _precision) onlyOwner public {
        consensusThreshold = threshold;
        precision = _precision;
    }

    function changePermisson(address userAddress, Permission permission) public {
        require(user_userDetails[msg.sender].permission == Permission.INVITE);
        require(user_userDetails[userAddress].permission != Permission.DEFAULT, "User is not a member of the group");
		user_userDetails[userAddress].permission = permission;
    }

    function inviteUser(address inviteeAddress, address inviteeContractAddress, Permission permission, string memory encryptedKey) public {
        require(user_userDetails[msg.sender].permission == Permission.INVITE, "You do not have permission to invite!");
        // require(invites[inviteeAddress].permission == Permission.DEFAULT, "Already Invited");
        User userInstance = User(inviteeContractAddress);
        userInstance.addGroupInvite(address(this), groupName, permission, encryptedKey);
        invites[inviteeAddress] = UserDetails(inviteeAddress, inviteeContractAddress, permission, encryptedKey);
    }

    event NewMember(string key);
    function inviteAccepted(address userAddress) public returns (string memory){
        require(invites[userAddress].permission > Permission.DEFAULT, "Did not invite");
        user_userDetails[userAddress] = invites[userAddress];
        usersList.push(userAddress);
        if (invites[userAddress].permission == Permission.INVITE || invites[userAddress].permission == Permission.WRITE)
            numVotingRights++;
        string memory key = invites[userAddress].encryptedKey;
        delete invites[userAddress];
        emit NewMember(key);
        return key;
    }

    function getUsers() onlyMember public view returns (UserDetails[] memory) {
        UserDetails[] memory userDetails = new UserDetails[](usersList.length);
        for (uint i = 0; i < usersList.length; i++) {
            userDetails[i] = user_userDetails[usersList[i]];
        }
        return userDetails;
    }

    function removeMember(address userAddress) onlyMember public {
        if (user_userDetails[msg.sender].permission == Permission.INVITE || userAddress == msg.sender) {
            for (uint i = 0; i < usersList.length; i++) {
                if (usersList[i] == userAddress) {
                    usersList[i] = usersList[usersList.length-1];
                    usersList.pop();
                }
            }
            delete user_userDetails[userAddress];
        }
    }

    event NewProposal(address groupAddress, uint _proposalId);
    function newProposal(address userContract, string memory change, string memory cid) public {
        proposalId++;
        Proposal memory proposal;
        proposal.proposalMessage = change;
        proposal.userContract = userContract;
        proposal.cid = cid;
        proposal.forVotes = 0;
        proposal.againstVotes = 0;
        proposals[proposalId] = proposal;
        votedList[proposalId].push(userContract);
        emit NewProposal(address(this), proposalId);
        vote(proposalId, true);
    }

    event ProposalAccepted(uint indexed _proposalId);
    event ProposalRejected(uint indexed _proposalId);
    function vote(uint _proposalId, bool accept) onlyMember public {
        require(
            user_userDetails[msg.sender].permission == Permission.WRITE || user_userDetails[msg.sender].permission == Permission.INVITE, 
            "No voting rights"
        );
        for (uint i = 0; i < votedList[_proposalId].length; i++) {
            if (votedList[_proposalId][i] == msg.sender) 
                require(false, "Already voted");
        }
        if (accept){
            proposals[_proposalId].forVotes += 1;
            uint256 forVotePercent = proposals[_proposalId].forVotes * precision / numVotingRights;
            if (forVotePercent > consensusThreshold) {
                proposals[_proposalId].status = Status.ACCEPTED;
                ipfsCid = proposals[_proposalId].cid;
                emit ProposalAccepted(_proposalId);
            }
        }
        else{
            proposals[_proposalId].againstVotes += 1;
            uint256 againstVotePercent = proposals[_proposalId].againstVotes * precision / numVotingRights;
            if (againstVotePercent > (precision - consensusThreshold)) {
                proposals[_proposalId].status = Status.REJECTED;
                emit ProposalRejected(_proposalId);
            }
        }
    }

    function getProposals() onlyMember public view returns (Proposal[] memory) {

        Proposal[] memory proposalsList = new Proposal[](proposalId);
        for (uint i = 1; i <= proposalId; i++) {
            proposalsList[i-1] = proposals[i];
        }
        return proposalsList;
    }

    function getProposal(uint _proposalId) onlyMember public view returns(Proposal memory proposal) {
        return proposals[_proposalId];
    }
}

