import os

from web3 import Web3
from web3.providers.base import BaseProvider
from web3.middleware import geth_poa_middleware
from src.credential_handler import CredentialHandler
from src.multiple_credential_handler import MultipleCredentialHandler
from src.contract import Contract
from src.environment_handler import EnvironmentHandler
    

class ContractFactory:
    def __init__(self, network, address: str, provider: BaseProvider, credential_handler: CredentialHandler or MultipleCredentialHandler, multiple_credential: bool):
        self.network = network
        self.address = Web3.toChecksumAddress(address)
        self.provider = provider
        self.credential_handler = credential_handler
        self.multiple_credential = multiple_credential
        print(f"smartcontract address = {self.address}")
        print(f"smartcontract network = {self.network}")



    def build_contract(self) -> Contract:
        web3 = Web3(self.provider)
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        abi = self.load_abi()
        contract = web3.eth.contract(address=self.address, abi=abi)
        if self.multiple_credential:
            return Contract(contract, self.credential_handler.senders)
        else:
            return Contract(contract, {self.credential_handler.pin:self.credential_handler.private_key})

    @staticmethod
    def load_abi():
        import json
        with open('abi/contract_abi.json') as abi:
            return json.load(abi)
        #return EnvironmentHandler.get_scl_contract_data_from_website()['abi']
