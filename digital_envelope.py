import base64
import os
import sys
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from shutil import copyfile
import time
from socket import *
target_host = "127.0.0.1"
client_host = "0.0.0.0"
port = 13000
buf = 1024
target_addr = (target_host, port)
client_addr = (client_host, port)

print("0.reciever generate public, private key and sent public key to sender")
print("1.Wait for public key from reciever")
print("2.Write a message and send")
print("3.send the defalut message")
print("4.wait for message from sender")
default_message='encrypt me! [Default Message]'
message = 'encrypt me! [Default Message]'
while 1:
    i=int(input('\nchoose: '))
    if i==0:
        # Builc Socket
        UDPSock = socket(AF_INET, SOCK_DGRAM)
        
        # Generate Public key and Private Key
        private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
        )
        public_key = private_key.public_key()
        print(public_key)
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        #store private key in a file named pem
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        f=open('private_key.pem', 'wb')
        f.write(pem)
        f.close()
        #store public  key in a file named pem
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        f=open('public_key.pem', 'wb')
        f.write(pem)
        f.close()
        #sent to people
        UDPSock.sendto("publickey".encode(), target_addr)
        UDPSock.sendto(pem, target_addr)
        print("[ Sented my Public Key ]")
        UDPSock.close()
        os._exit(0)
    if i==1:
        UDPSock = socket(AF_INET, SOCK_DGRAM)
        UDPSock.bind(client_addr)
        print("[ Wait for Public Key ]")
        while True:
            (data, client_addr) = UDPSock.recvfrom(buf)
            (data2, client_addr) = UDPSock.recvfrom(buf)
            if(data.decode()=="publickey"):
                print("Received message:\n" + data2.decode())
                f=open('public_key.pem', 'wb')
                f.write(data2)
                f.close()
                print("[ Received Public Key ]")
                time.sleep(0.5)
                UDPSock.close()
                os._exit(0)
    if i==2:
        message = input("input your message : ")
        print("your message is : "+message)
        i=3
    if i==3:
        #3
        if message == default_message:
            print("Your message is: "+message)
        #generate random key
        UDPSock = socket(AF_INET, SOCK_DGRAM)
        randomkey = Fernet.generate_key()
        #open reciever's public key
        with open("public_key.pem", "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        #encrypt the message with random key
        encrypted_meassage = Fernet(randomkey).encrypt(message.encode());
        
        #encrypt the random key with reciever's public
        encrypted = public_key.encrypt(
            randomkey,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        UDPSock.sendto(encrypted_meassage, target_addr) 
        UDPSock.sendto(encrypted, target_addr) 
        print("[Message encrypted]")
        print(encrypted_meassage)
        print("[generate random key]:")
        print(randomkey.decode())
        print("\n[ Message sent ]")
        UDPSock.close()
        os._exit(0)
    if i==4:
        UDPSock = socket(AF_INET, SOCK_DGRAM)
        with open("private_key.pem", "rb") as key_file:
            private_key=serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

        UDPSock.bind(client_addr)

        print("Waiting to receive messages...")
        while True:
            (e_message, client_addr) = UDPSock.recvfrom(buf)
            (e_key, client_addr) = UDPSock.recvfrom(buf)
            #print("Received message: " + e_message.decode())
            #print("Received randomkey: " + e_key)
            if e_message !="":
                #decrypt the encrypt random key
                decrypted_key = private_key.decrypt(
                    e_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                #
                randomkey=decrypted_key.decode()
                decrypted_message = Fernet(randomkey).decrypt(e_message)
                print("[The Message]:"+decrypted_message.decode())
                print("\n[Message encrypted]")
                print(e_message)
                print("[Random key]\n"+decrypted_key.decode())
                break
        UDPSock.close()
        os._exit(0)
        #read file
    
    
    