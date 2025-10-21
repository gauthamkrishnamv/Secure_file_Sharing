import os
import shutil
from cryptography.fernet import Fernet
import ipfshttpclient
from encryption import generate_key

client = ipfshttpclient.connect()


def upload_folder(directory_path, key):
    # Generate encryption key
    fernet = Fernet(key)

    # Create a temporary directory to store encrypted files
    encrypted_directory = os.path.join(directory_path, '__encrypted')
    os.makedirs(encrypted_directory, exist_ok=True)
    
    # Encrypt and upload files
    for root, dirs, files in list(os.walk(directory_path)):
#         os.makedirs(os.path.join(encrypted_directory, root), exist_ok=True)
        for filename in files:
            # Read the file
            file_path = os.path.join(root, filename)
            with open(file_path, 'rb') as file:
                file_data = file.read()

            # Encrypt the file data
            encrypted_data = fernet.encrypt(file_data)
            
            # Save the encrypted data to the temporary directory
            encrypted_file_path = os.path.join(encrypted_directory, root,filename)
            os.makedirs(os.path.join(encrypted_directory, root), exist_ok=True)
            with open(encrypted_file_path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)

    # Upload the encrypted directory to IPFS
    response = client.add(os.path.join(encrypted_directory, directory_path), recursive=True)

    # Remove the temporary directory
    shutil.rmtree(encrypted_directory)

    # Return the CID of the uploaded directory
    cid = list(filter(lambda x: x['Name'] == os.path.basename(directory_path), response))[0]['Hash']
    return cid


def download_folder(cid, folder_name, key, destination_path='repos'):
    fernet = Fernet(key)

    client.get(cid, destination_path)
    
    curr_path = os.path.join(destination_path, cid)
    new_path = os.path.join(destination_path, folder_name)
    shutil.rmtree(new_path, ignore_errors=True)
    os.rename(curr_path, new_path)
    for root, dirs, files in list(os.walk(new_path)):
        for filename in files:
            # Read the file
            file_path = os.path.join(root, filename)
            with open(file_path, 'rb') as file:
                print(file_path)
                decrypted_data = fernet.decrypt(file.read())

            with open(file_path, 'wb') as file:
                file.write(decrypted_data)



if __name__ == '__main__':
    key = generate_key()
    print(key)
    upload_folder('repos/group_03', key)