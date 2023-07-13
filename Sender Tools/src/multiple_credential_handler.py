import json
from .sca_encryption import decrypt

class MultipleCredentialHandler:
    senders: dict

    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.load_credentials()
        self.get_pk()

    def load_credentials(self):
        with open(self.credentials_path) as f:
            self.senders = json.load(f)
        print(f"\nWelcome back to the SCA\nYou are connected with\n: {self.senders}\n")

    def get_pin(self):
        return list(self.senders.keys())

    def get_pk(self):
        for pin in self.get_pin():
            self.senders[pin] = self.senders[pin]
