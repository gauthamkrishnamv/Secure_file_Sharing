import json
import copy
import pickle
import os
from os import path
import logging
from web3 import Web3
import asyncio
from ipfs_handler import client, upload_folder, download_folder
from encryption import generate_key, generate_key_pair, address_from_private_key, encrypt_string, decrypt_string, encrypt_with_public_key, decrypt_with_private_key

logger = logging.getLogger()

with open('contract_env/build/contracts/FileApp.json') as f:
    FileAppJson = json.load(f)
with open('contract_env/build/contracts/User.json') as f:
    UserJson = json.load(f)
with open('contract_env/build/contracts/Group.json') as f:
    GroupJson = json.load(f)


# Connect to Ganache (adjust the RPC URL and port accordingly)
FILEAPPCONTRACTADDRESS = '0x49294C9521770c850b0bd668738E8fE8B380c132'


REPOPATH = 'repos';
USERDATAPATH = 'user_data'
MFSBASEPATH = '/fileApp';

ganache_url = "http://0.0.0.0:8545"
w3 = Web3(Web3.HTTPProvider(ganache_url))
websocket_url = "ws://192.168.0.10:8545"
w3_socket = Web3(Web3.WebsocketProvider(websocket_url))
accounts = w3.eth.accounts


PERMISSION = ['DEFAULT', 'READ', 'WRITE', 'INVITE']
PERMISSIONMAP = {
    'DEFAULT': 0,
    'READ': 1,
    'WRITE': 2,
    'INVITE': 3
}

class FileApp:
    def __init__(self):
        self.file_app_contract_address = FILEAPPCONTRACTADDRESS
        self.contract = w3.eth.contract(abi=FileAppJson['abi'], address=FILEAPPCONTRACTADDRESS)
        self.username = ''
        self.user_address = ''
        self.user_contract = None
        self.user_contract_address = ''
        self.public_key = ''
        self.private_key = ''
        self.groups = {}
        self.users = []
        self.user_address_name_dict = {}
        self.invites = {}
        self.last_read_block_user_registered = 0
        self.last_read_block_new_invite = 0

    def sign_up(self, username, eth_private_key):
        address = address_from_private_key(eth_private_key)
        if address not in accounts:
            raise Exception('The account does not exists!')
            # print('The account does not exists!')

        self.user_address = address
        self.username = username
        
        key_pair = generate_key_pair();
        self.public_key = key_pair['publicKey']
        self.private_key = key_pair['privateKey']
        # print(self.public_key)
        gas = self.contract.functions.signUp(self.username, '', self.public_key).estimate_gas({'from': self.user_address})
        self.contract.functions.signUp(self.username, '', self.public_key).transact({'from': self.user_address, 'gas': gas})
        self.user_contract_address = self.contract.functions.getUserContractAddress(self.user_address).call({'from': self.user_address})
        self.user_contract = w3.eth.contract(abi=UserJson['abi'], address=self.user_contract_address)
        self.get_users_infos()
        # self.save_state()
    
    def get_users_infos(self):
        infos = self.contract.functions.getUserInfos().call({'from': self.user_address})
        self.users = []
        self.user_address_name_dict = {}
        for info in infos:
            temp_dict = {
                'username': info[0],
                'userAddress': info[1],
                'userContractAddress': info[2],
                'publicKey': info[3]
            }
            self.user_address_name_dict[info[1]] = info[0] 
            self.users.append(temp_dict)


    def user_registered_event_filter(self):
        return self.user_contract.events.newInvite.create_filter(fromBlock=self.last_read_block_user_registered)

    def handle_user_registered(self, event):
        event = Web3.to_json(event)
        event = json.loads(event)
        args = event['args']
        temp_dict = {
            'username': args['username'],
            'userAddress': args['userAddress'],
            'userContractAddress': args['userContractAddress'],
            'publicKey': args['publicKey']
        }
        self.user_address_name_dict[args['userAddress']] = args['username']
        logger.debug(f'User Registered: {temp_dict["username"]}')
        self.users.append(temp_dict)
        self.last_read_block_user_registered = event['blockNumber']



    def get_invites(self):
        invites = self.user_contract.functions.getGroupInvites().call({'from': self.user_address})
        self.invites = {}
        for invite in invites:
            self.invites[invite[1]] = [invite[0], PERMISSION[invite[2]], invite[3]]

    def new_invite_event_filter(self):
        return self.user_contract.events.newInvite.create_filter(fromBlock=self.last_read_block_new_invite)

    def handle_new_invite(self, event):
        event = Web3.to_json(event)
        event = json.loads(event)
        args = event['args']
        self.invites[args['groupAddress']] = [args['groupName'], PERMISSION[args['permission']], args['encyptedKey']]
        self.last_read_block_new_invite = event['blockNumber']

    def update_invtes(self):
        pass

    def reject(self, group_address):
        gas = self.user_contract.functions.rejectInvite(group_address).estimate_gas({'from': self.user_address})
        self.user_contract.functions.rejectInvite(group_address).transact({'from': self.user_address, 'gas': gas})
        del self.invites[group_address]
    
    def accept_invite(self, group_address):
        gas = self.user_contract.functions.acceptInvite(group_address).estimate_gas({'from': self.user_address})
        tx_hash =self.user_contract.functions.acceptInvite(group_address).transact({'from': self.user_address, 'gas': gas})
        tx_rec = w3.eth.get_transaction_receipt(tx_hash)
        # log = self.user_contract.events.InviteAccepted().process_receipt(tx_rec)
        # group_key = log[0]['args']['key']
        group_key = self.invites[group_address][2]
        print(group_key)
        del self.invites[group_address]
        self.groups[group_address] = Group.copy_group(group_address, group_key, self)

    def create_group(self, group_name, consensus_threshold):
        new_group = Group.new_group(group_name, consensus_threshold, self)
        self.groups[new_group.address] = new_group

    def save_state(self):
        temp_obj = copy.copy(self) 
        temp_obj.contract = None
        temp_obj.user_contract = None
        for address, group in temp_obj.groups.items():
            temp_obj.groups[address] = copy.copy(group)
            temp_obj.groups[address].contract = None 
            temp_obj.groups[address].file_app_obj.contract = None
            temp_obj.groups[address].file_app_obj.user_contract = None


        with open(path.join(USERDATAPATH, f'{self.username}.pkl'), 'wb') as file:
            pickle.dump(temp_obj, file)

        temp_obj.contract = w3.eth.contract(abi=FileAppJson['abi'], address=FILEAPPCONTRACTADDRESS)
        temp_obj.user_contract = w3.eth.contract(abi=UserJson['abi'], address=temp_obj.user_contract_address)
        for address, group in temp_obj.groups.items():
            temp_obj.groups[address].contract = w3.eth.contract(abi=GroupJson['abi'], address=address)
            temp_obj.groups[address].file_app_obj = temp_obj
            # temp_obj.groups[address].file_app_obj.contract = temp_obj.contract
            # temp_obj.groups[address].file_app_obj.user_contract = temp_obj.user_contract

        
        print('State Saved')
        

    @staticmethod
    def login(username, private_key):
        # try:
        address = address_from_private_key(private_key)
        file_app = None
        with open(path.join(USERDATAPATH, f'{username}.pkl'), 'rb') as file:
            file_app = pickle.load(file)
        
        if file_app.user_address != address:
            raise ValueError('Invalid private key!')
        
        file_app.contract = w3.eth.contract(abi=FileAppJson['abi'], address=FILEAPPCONTRACTADDRESS)
        file_app.user_contract = w3.eth.contract(abi=UserJson['abi'], address=file_app.user_contract_address)
        
        for address, group in file_app.groups.items():
            file_app.groups[address].contract = w3.eth.contract(abi=GroupJson['abi'], address=address)
            file_app.groups[address].file_app_obj = file_app
            # file_app.groups[address].file_app_obj.user_contract = file_app.user_contract

        print(file_app.user_contract)
        return file_app
        

class Group:
    def __init__(self, name, consensus_threshold, precision, file_app_obj) -> None:
        self.name = name
        self.consensus_threshold = consensus_threshold
        self.precision = precision
        self.file_app_obj = file_app_obj
        
        self.group_key = None

        self.local_path = ''
        self.mfs_path = ''
        self.ipfs_cid = None
        self.ipfs_cid_encrypted = None
        self.temp_cid = ''
        self.temp_cid_encrypted = None
        self.curr_cid = self.ipfs_cid
        # self.ipfs_path = ''

        self.owner = ''
        self.address = ''
        self.contract = None

        self.permission = ''
        self.users = []
        # self.invites = {}
        self.proposals = []

        self.last_read_block_new_member = 0
        self.last_read_block_new_proposal = 0
        self.last_read_block_proposal_accepted = 0
        self.last_read_block_proposal_rejected = 0
    
    def set_contract(self):
        self.contract = w3.eth.contract(abi=GroupJson['abi'], address=self.address)

    @staticmethod
    def calc_precision(consensus_threshold):
        q = consensus_threshold
        places = 0
        while q >= 1:
            q = q / 10
            places += 1
        return 10 ** places
    
    @staticmethod
    def new_group(group_name, consensus_threshold, file_app_obj):
        precision = Group.calc_precision(consensus_threshold)
        new_group = Group(group_name, consensus_threshold, precision, file_app_obj)
        new_group.owner = file_app_obj.user_address
        new_group.permission = 'INVITE'
        new_group.create_dir()
        new_group.create_contract()
        return new_group

    def create_dir(self):
        if self.file_app_obj.user_contract:
            self.group_key = generate_key()
            self.local_path = path.join(REPOPATH, self.name)
            # self.mfs_path = path.join(MFSBASEPATH, self.name)
            os.mkdir(self.local_path)
            response = client.add(self.local_path)
            self.ipfs_cid = list(filter(lambda x: x['Name']==os.path.basename(self.local_path),response))[0]['Hash']
            self.ipfs_cid_encrypted = encrypt_string(self.group_key ,self.ipfs_cid)
            self.curr_cid = self.ipfs_cid
            print('Directory created')

    def create_contract(self):
        self.encrypted_key = encrypt_with_public_key(self.file_app_obj.public_key, self.group_key)
        gas = self.file_app_obj.user_contract.functions.createGroup(
            self.name, 
            self.consensus_threshold, 
            self.precision, 
            self.ipfs_cid_encrypted,
            self.encrypted_key
        ).estimate_gas({'from': self.file_app_obj.user_address})
        
        tx_hash = self.file_app_obj.user_contract.functions.createGroup(
            self.name, 
            self.consensus_threshold, 
            self.precision, 
            self.ipfs_cid_encrypted,
            self.encrypted_key
        ).transact({'from': self.file_app_obj.user_address, 'gas': gas})
        tx_rec = w3.eth.get_transaction_receipt(tx_hash)
        log = self.file_app_obj.user_contract.events.GroupCreated().process_receipt(tx_rec)
        self.address = log[0]['args']['groupAddress']
        self.contract = w3.eth.contract(abi=GroupJson['abi'], address=self.address)
        self.get_users()
        print('New Group contract created address = ', self.address)

    
    @staticmethod
    def copy_group(group_address, encrypted_group_key, file_app_obj):
        group_contract = w3.eth.contract(abi=GroupJson['abi'], address=group_address)
        group_info = group_contract.functions.getGroupInfo().call({'from': file_app_obj.user_address})
        group = Group(
            group_info[0], 
            group_info[3],
            Group.calc_precision(group_info[3]),
            file_app_obj
        )
        group.group_key = decrypt_with_private_key(file_app_obj.private_key, encrypted_group_key)

        group.local_path = os.path.join(REPOPATH, group.name)
        group.ipfs_cid = decrypt_string(group.group_key, group_info[2])
        group.ipfs_cid_encrypted = group_info[2]
        group.curr_cid = group.ipfs_cid
        
        group.owner = group_info[1]
        group.address = group_address
        group.contract = group_contract

        group.get_users()
        group.get_proposals()
        group.download_dir()

        return group
    
    def get_users(self):
        self.users = []
        self.file_app_obj.get_users_infos()
        user_details = self.contract.functions.getUsers().call({'from': self.file_app_obj.user_address})
        for user in user_details:
            self.users.append({
                'userAddress': user[0],
                'userContractAddress': user[1],
                'permission': PERMISSION[user[2]],
                'encryptedKey': user[3],
                'username': self.file_app_obj.user_address_name_dict[user[0]]
            })

    def get_proposals(self):
        self.proposals = []
        proposals = self.contract.functions.getProposals().call({'from': self.file_app_obj.user_address})
        for proposal in proposals:
            self.proposals.append({
				'proposalMessage': proposal[0],
				'userContract': proposal[1],
				'cid': proposal[2],
				'forVotes': proposal[3],
				'againstVotes': proposal[4],
				'votedList': proposal[5],
				'status': proposal[6],
                'voted': False
            })
    
    def get_proposal(self, proposal_id):
        return self.contract.functions.getProposal(proposal_id).call({'from': self.file_app_obj.user_address})

    def download_dir(self):
        download_folder(self.ipfs_cid, self.name, self.group_key, REPOPATH)

    def invite(self, user_dict, permission):
        print(f'Inviting {user_dict}')
        encrypted_key = encrypt_with_public_key(user_dict['publicKey'], self.group_key)
        gas = self.contract.functions.inviteUser(
            user_dict['userAddress'], 
            user_dict['userContractAddress'],
            PERMISSIONMAP[permission],
            encrypted_key
        ).estimate_gas({'from': self.file_app_obj.user_address})

        self.contract.functions.inviteUser(
            user_dict['userAddress'],
            user_dict['userContractAddress'],
            PERMISSIONMAP[permission],
            encrypted_key
        ).transact({'from': self.file_app_obj.user_address, 'gas': gas})
        
    def propose(self, change_string):
        print(f'Proposing with string: {change_string}, self.local_path={self.local_path}')
        self.temp_cid = upload_folder(self.local_path, self.group_key)
        self.temp_cid_encrypted = encrypt_string(self.group_key, self.temp_cid)
        gas = self.contract.functions.newProposal(
            self.file_app_obj.user_contract_address, 
            change_string, 
            self.temp_cid_encrypted).estimate_gas({'from': self.file_app_obj.user_address})
        self.contract.functions.newProposal(
            self.file_app_obj.user_contract_address, 
            change_string, 
            self.temp_cid_encrypted).transact({'from': self.file_app_obj.user_address, 'gas': gas})
        self.get_proposals()

    def vote(self, proposal_id, accept: bool):
        gas = self.contract.functions.vote(proposal_id+1, accept).estimate_gas({'from': self.file_app_obj.user_address})
        self.contract.functions.vote(proposal_id+1, accept).transact({'from': self.file_app_obj.user_address, 'gas': gas})
        self.proposals[proposal_id]['voted'] = True


    def proposal_accepted(self, proposal_id):
        self.proposals[proposal_id-1]['status'] = 1
        self.ipfs_cid_encrypted = self.proposals[proposal_id-1]['cid']
        self.ipfs_cid = decrypt_string(self.group_key, self.ipfs_cid_encrypted)
        self.download_dir()

        
    def proposal_rejected(self, proposal_id=None):
        self.proposals[proposal_id-1]['status'] = 2
        # if self.proposals[proposal_id]['cid'] == self.temp_cid_encrypted:

    
    def new_member_event_filter(self):
        return self.contract.events.NewMember.create_filter(fromBlock=self.last_read_block_new_member)
    
    def handle_new_member(self, event):
        logger.debug("New member joined!")
        event = Web3.to_json(event)
        event = json.loads(event)
        self.get_users()
        self.last_read_block_new_member = event['blockNumber']


    def new_proposal_event_filter(self):
        return self.contract.events.NewProposal.create_filter(fromBlock=self.last_read_block_new_proposal)
    
    def handle_new_proposal(self, event):
        event = Web3.to_json(event)
        event = json.loads(event)
        args = event['args']
        logger.debug(f'New Proposal! {args}')
        self.get_proposals()
        self.last_read_block_new_proposal = event['blockNumber']

    
    def proposal_accepted_event_filter(self):
        return self.contract.events.ProposalAccepted.create_filter(fromBlock=self.last_read_block_proposal_accepted)
    
    def proposal_rejected_event_filter(self):
        return self.contract.events.ProposalRejected.create_filter(fromBlock=self.last_read_block_proposal_rejected)

    def handle_proposal_accepted(self, event):
        event = Web3.to_json(event)
        event = json.loads(event)
        args = event['args']
        logger.debug(f'Proposal Accepted for group: {self.name} {args}')
        self.proposal_accepted(args['_proposalId'])
        self.last_read_block_proposal_accepted = event['blockNumber']

    def handle_proposal_rejected(self, event):
        event = Web3.to_json(event)
        event = json.loads(event)
        args = event['args']
        logger.debug(f'Proposal Rejected for group: {self.name} {args}')
        self.proposal_rejected(args['_proposalId'])
        self.last_read_block_proposal_rejected = event['blockNumber']

    def view_change(self, proposal_id, temp_name='__proposal'):
        self.prop_cid_encrypted = self.proposals[proposal_id]['cid']
        self.prop_cid = decrypt_string(self.group_key, self.temp_cid_encrypted)
        download_folder(self.prop_cid, self.name, self.group_key, os.path.join(REPOPATH,temp_name))
        return os.path.join(REPOPATH,temp_name)
        
    def revert_change(self):
        if self.temp_cid:
            if self.curr_cid == self.temp_cid:
                self.curr_cid = self.ipfs_cid
            else:
                self.curr_cid = self.temp_cid

            download_folder(self.curr_cid, self.name, self.group_key, REPOPATH)


if __name__ == '__main__':
    privates = [
        '0x79299ed468098134277cdfda3eb99a91ec009cde9952c9fcd77fc081954a3bf7',
        '0x218f27a77110bbb1d3a52bdca1d343f08eac0eaf60a0de8e5466e3355237846c',
        '0x8cb39f89698e21d67c1d31d41c302467ec01a4014e049a84399c96fc07b7e54b',
        '0xd0c17d90995536bef8d9304ed44cde79436c88920820a9c574706a66b0942d8d',
        '0xa7e69ae6823d3eeb96c23a53f4d2357560f86b63c8f52b8082569022877bf45b',
        '0x5f5f71ae02499f9effd10a63a4eb3d829dd0f417137b7b680888027e35e2a5b3',
        '0xc579ce50164e3a8df1719dc68716a36d676d7d4330a15e7a5162423e52be6a13',
        '0xc4c16c18e63b0526364433bef5afdad98c0413cd373d90a188a78b72a13fdaa9',
        '0x5edc51c13b817328d77f8d1febe32214d7ee1bfa3e528fb372cfca5d3183ade8',
        '0x2515e7ad78aa4564af4dc97ad9d835879577b0e2f174d6092edb9644239959b7',
        '0x3d26bbf81b2b3bc994df31b81e2f5ab78e2e8d4c6882f07901a10950067b1eef',
        '0x05fff2dc6051c3ad872702301ead123e42f8e42c8065b92d6257ece0ead7f010'   
    ]
    names = [
    'Amy', 'Ana', 'Ava', 'Dan',
    'Eli', 'Eva', 'Jax', 'Jen',
    'Jon', 'Kai', 'Kim', 'Leo',
    'Lia', 'Liz', 'Max', 'Mia',
    'Noa', 'Rio', 'Sam', 'Zoe'
    ]
    name = names[9]
    private = privates[9]
    name
    # file_app = FileApp()
    # file_app = FileApp()
    # file_app.sign_up(name, private)
    file_app = FileApp().login(name, private)
    # file_app.get_users_infos()
    print(file_app.username)
    file_app.create_group('sdgssa', 50)
    print(file_app.groups.keys())
    file_app.save_state()
    # file_app.sign_up('amy', '0x79299ed468098134277cdfda3eb99a91ec009cde9952c9fcd77fc0453954a3bf7')
    # print(file_app.user_contract_address)