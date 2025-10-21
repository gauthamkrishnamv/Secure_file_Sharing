import json
from web3 import Web3
import asyncio
import threading
import time

# from fileApp import FileApp

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
    '0x05fff2dc6051c3ad872702301ead123e42f8e42c8065b92d6257ece0ead7f010',
    '0x2b11c682db2d0a1b50854a19e86938be24c5e3f2a2c129a1b34164be77c9f8b2',
    '0x0739fd687c250050b3b81e1d8c62a1197e1371afd5304fc984e159e8f12d84ba',
    '0x55d600b27e8d2d62b96bcb871a07eb581274c585b0ad821dd4bf7da87a2ad0b0',
    '0x869c6171796d3c2955c5a6c0a3c96932c68ff3e19acc6a7c846555171eb3e982',
    '0x2f002ca0e19123ccd230cc52c741993f5848a8ee98dd8a0c24990c11d7170526',
    '0x5e4e36cf737aa7230bcde7607d3576722fa171678ca2617566ea7a52d032ac9f',
    '0x018fb96a276016093613342ae43b6da8632afefd2ce822ace466d7acc9dde1ad',
    '0x76e84733b29edcfd9161fe171ec3a20cbefa219bd5c2584c9305310ffb702667'
]
names = [
  'Amy', 'Ana', 'Ava', 'Dan',
  'Eli', 'Eva', 'Jax', 'Jen',
  'Jon', 'Kai', 'Kim', 'Leo',
  'Lia', 'Liz', 'Max', 'Mia',
  'Noa', 'Rio', 'Sam', 'Zoe'
]
choice = 0
name_test = names[choice]
private_test = privates[choice]

# add your blockchain connection information

with open('/media/rv/Store Room/Main_Project/contract_env_v1/build/contracts/Test.json') as f:
    TestJson = json.load(f)

ganache_url = "http://192.168.0.10:8545"
w3 = Web3(Web3.HTTPProvider(ganache_url))
contract = w3.eth.contract(address='0xAc3257D40b3330e63B5A29B7ee055BA5EE85679F', abi=TestJson['abi'])


import tkinter as tk

context_menu = None

def open_folder():
    print("Folder opened")

def delete_folder():
    print("Folder deleted")

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)



def handle_event(event):
    event = Web3.to_json(event)
    event = json.loads(event)
    print(event)




def main():
    threads = []
    def create_task(event_filter, handler, poll_interval=2):
        def polling():
            while True:
                # event_filter = event_filter_getter()
                for event in event_filter.get_new_entries():
                    handler(event)
                time.sleep(poll_interval)
                # print(f'listening to ', event_filter)
                print(f'listening to {event_filter}')
        
        t = threading.Thread(target=polling)
        t.start()
        threads.append(t)  
    
    create_task(contract.events.Random.create_filter(fromBlock='latest'), handle_event)
    


    

    

# def main():


#     while True:
#         await asyncio.sleep(0.1)
    # try:
    # finally:

if __name__ == "__main__":
    main()
    # asyncio.run(main())

