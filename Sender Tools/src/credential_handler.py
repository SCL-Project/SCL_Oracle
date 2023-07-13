from json.decoder import JSONDecodeError
import json
from web3 import Web3
from eth_account import Account
import stdiomask
from .sca_encryption import encrypt, decrypt
from cryptography.fernet import InvalidToken


class CredentialHandler:
    pin: str
    encrypted_private_key: str
    private_key: str
    new_credentials: bool

    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.new_credentials = False
        while True:
            self.load_credentials()
            if self.new_credentials:
                break
            else:
                self.password_check()
                break

    def load_credentials(self):
        with open(self.credentials_path) as f:
            try:
                data = json.load(f)
                self.pin = data['pin']
                self.encrypted_private_key = data["encrypted_private_key"]
            except JSONDecodeError:
                print('\nWelcome to the Sender Convenience Applet (SCA)\n'
                      '\nIn order to use the SCA, a brief set-up is required')
                self.create_credentials()
                return 

        print(f"\nWelcome back to the SCA\nYou are connected with\nPIN: {self.pin}\n")

    def create_credentials(self):
        self.new_credentials = True
        while True:
            try:
                self.pin = Web3.toChecksumAddress(input("1. Please enter your PIN address:"))
                break
            except ValueError:
                print("Please enter a valid public key as your PIN address")
        while True:
            self.private_key = stdiomask.getpass("2. Please enter the private key corresponding to your PIN"
                                                 " \n(it will be encrypted and stored exclusively on your machine):\n")
            account = Account.from_key(self.private_key)
            print(account.address)
            if account.address == self.pin:
                break
            else:
                print("The private key you have entered does not correspond to your public key:\n{self.pin}")
        while True:
            password_1 = stdiomask.getpass("Please enter a password to encrypt your private key:\n")
            password_2 = stdiomask.getpass("Confirm Password:\n")
            if password_1 == password_2:
                break
            else:
                print("Passwords do not match.")
        encrypted_private_key = encrypt(self.private_key, password_1)
        self.private_key = ''
        file_args = {
            "pin": self.pin,
            "encrypted_private_key": encrypted_private_key,
        }
        self.write_credentials(file_args)

    def write_credentials(self, file_args):

        with open(self.credentials_path, "w") as f:
            f.write(json.dumps(file_args))
            print(f"Your credentials have been modified\nPIN: {self.pin}\n")

    def change_credentials(self):
        change_credentials = ""
        while change_credentials not in ["y", "n"]:
            change_credentials = input("Do you wish to change your credentials? (y/n): \n")
        if change_credentials == "y":
            self.create_credentials()

    def password_check(self) -> bool:
        password = stdiomask.getpass("Your private key is encrypted. Please enter your password to decrypt it:\n")
        wrong_password_count = 0

        while True:
            try:
                self.private_key = decrypt(self.encrypted_private_key, password)
                return True
            except InvalidToken:
                if wrong_password_count == 3:
                    open(self.credentials_path, "w").close()
                    print("Your credentials have been deleted. Reenter them in order to get started")
                    return False
                else:
                    wrong_password_count += 1
                    password = stdiomask.getpass(f'Invalid password. Please try again ({wrong_password_count}'
                                                 f' out of 3):\n')
