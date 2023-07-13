import json
from json.decoder import JSONDecodeError
import os
from typing import List
import requests
from requests.auth import HTTPBasicAuth
import configparser


class EnvironmentHandler:
    """EnvironmentHandler ensures that the SCA is placed in a working environment on your local machine

    Args:
        settings_path (str): Path to where your credentials, the scl-address & your network settings are stored.
        scl_path (str): Path to where the orders database is stored.
    """
    def __init__(self, settings_path, scl_path, network, scl_address=None):
        self.settings_path = f"sender/{settings_path}"
        self.scl_path = f"sender/{scl_path}"
        self.network = network
        self.credentials_path = f"{self.settings_path}/credentials.json"
        self.config_path = f"{self.settings_path}/config.ini"
        self.config_data = self.read_ini(self.config_path)
        self.multiple_credential = self.config_data["multiple_sender"]
        self.network_settings_path = f"{self.settings_path}/network_settings.json"
        if network == 'setup':
            pass
        else:
            if scl_address is None:
                self.scl_address = self.get_scl_contract_data_from_website()
            self.event_db_path = f"{self.scl_path}/orders_{self.network}/"
            self.paths = [self.settings_path, self.scl_path, self.event_db_path]
            self.files = [self.credentials_path, self.network_settings_path]
            self.setup_paths_files(self.paths, self.files)
            self.fill_network_settings_template(self.network_settings_path)

    def setup_paths_files(self, paths: List[str], files: List[str]):
        for path in paths:
            if not self.does_path_exist(path):
                self.create_folder(path)
        for file in files:
            if not self.does_path_exist(file):
                self.create_file(file)

    @staticmethod
    def does_path_exist(path: str) -> bool:
        return os.path.exists(path)

    @staticmethod
    def create_folder(path: str):
        os.mkdir(path)

    @staticmethod
    def create_file(path: str):
        with open(path, "a+"):
            pass

    @staticmethod
    def fill_network_settings_template(network_settings_path: str):
        try:
            with open(network_settings_path, 'r') as network_json:
                json.load(network_json)
        except JSONDecodeError:
            template = {
                "main_network_host": "Enter uri-endpoint/ipc-path for main-network e.g. 'http://127.0.0.1:8545'",
                "ropsten_network_host": "Enter uri-endpoint/ipc-path for ropsten-network e.g. 'http://127.0.0.1:8546'"
            }
            with open(network_settings_path, "w") as network_json:
                json.dump(template, network_json)

    def get_scl_contract_data_from_website(self):
        # TODO: get rid of environment variables once website goes public
        with open(self.network_settings_path, 'r') as network_file:
            settings_file = json.load(network_file)
            scl_address = settings_file[self.network]['address']
        print(f"SCL Oracle-address: {scl_address}")
        return scl_address


    @staticmethod
    def read_ini(file_path):
        config = configparser.ConfigParser()
        config.read(file_path)
        config_dict = {}
        for section in config.sections():
            for key in config[section]:
                config_dict[key] = config[section][key]
        config_dict['multiple_sender'] = config_dict['multiple_sender'] == "True"
        return config_dict
