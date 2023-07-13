import json
from json.decoder import JSONDecodeError


class NetworkSettingsHandler:
    def __init__(self, path, network):
        self.path = path
        self.network = network
        self.network_settings_dictionary = self.get_host_dictionary(path)
        self.host = self.network_settings_dictionary[self.network]['network']

    def get_host(self, network: str):
        network_settings_dictionary = self.get_host_dictionary(self.path)
        try:
            self.host = network_settings_dictionary[self.network]['network']
            return self.host
        except ValueError:
            raise ValueError("invalid Network")

    @staticmethod
    def get_host_dictionary(path):
        network_settings = None
        with open(path) as f:
            try:
                network_settings = json.load(f)
            except JSONDecodeError:
                print("invalid settings")
        return network_settings
