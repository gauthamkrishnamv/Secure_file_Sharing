import os
import json
import hashlib
import base64
from eth_keys import keys
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

def generate_key():
    return Fernet.generate_key()

def encrypt_string(key, plaintext):
    cipher_suite = Fernet(key)
    encrypted_text = cipher_suite.encrypt(plaintext.encode())
    return encrypted_text.decode('utf-8')

def decrypt_string(key, ciphertext):
    cipher_suite = Fernet(key)
    decrypted_text = cipher_suite.decrypt(ciphertext.encode('utf-8'))
    return decrypted_text.decode()


def generate_key_pair():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    # with open("private.pem", "w") as private_file:
    #     private_file.write(private_key)

    # with open("public.pem", "w") as public_file:
    #     public_file.write(public_key)

    return {
        'privateKey': private_key,
        'publicKey': public_key
    }

def encrypt_with_public_key(public_key, data):
    rsa_public_key = serialization.load_pem_public_key(public_key.encode('utf-8'))
    encrypted_data = rsa_public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encrypted_data_base64 = base64.b64encode(encrypted_data).decode('utf-8')
    return encrypted_data_base64

def decrypt_with_private_key(private_key, encrypted_data_base64):
    rsa_private_key = serialization.load_pem_private_key(
        private_key.encode('utf-8'),
        password=None
    )
    encrypted_data = base64.b64decode(encrypted_data_base64)
    decrypted_data = rsa_private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_data

def address_from_private_key(private_key_hex):
    private_key = keys.PrivateKey(bytes.fromhex(private_key_hex[2:]))
    public_key = private_key.public_key
    address = public_key.to_checksum_address()
    return address

if __name__ == '__main__':
    kp = generate_key_pair()
    # print(type(kp['publicKey'].decode('base-64')))
    print(type(kp['publicKey']))



