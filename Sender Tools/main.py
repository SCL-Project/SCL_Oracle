import argparse
import configparser
import logging
import logging.handlers as handlers
from typing import List
from web3.providers.base import BaseProvider
import web3
import json
import asyncio
from src.environment_handler import EnvironmentHandler
from src.credential_handler import CredentialHandler
from src.multiple_credential_handler import MultipleCredentialHandler
from src.transaction_manager import TransactionManager
from src.network_settings_handler import NetworkSettingsHandler
from src.contract_factory import ContractFactory
from src.sca import SCA
from sender.data_reader.data_loader import load_apis
from src.blockchain_connection import BlockchainConnection
import sys

# prints logo when starting the sca
def print_logo():
    with open("sca.txt", "r") as f0:
        print(f0.read())

# asks to provide a node link is none is already specified
def setup_provider_json(network: str, path: str):
    print("You have not yet setup a working web3 provider. Please do so now:")
    with open(path, "r") as network_json:
        any_previous_network_data = json.load(network_json)
    any_previous_network_data[f'{network}_network_host'] = str(input(f"Please enter your uri-endpoint or"
                                                                     f" path to your geth-node for the "
                                                                     f"{network} network:\n"))
    with open(path, "w") as network_json:
        json.dump(any_previous_network_data, network_json)

# tries to connect via https, if not..
def get_https_provider(network: str, network_settings_handler: NetworkSettingsHandler) -> BaseProvider:
    return web3.HTTPProvider(network_settings_handler.get_host(network))

# ... tires to connect via websocket, if not...
def get_websocket_provider(network: str, network_settings_handler: NetworkSettingsHandler) -> BaseProvider:
    return web3.WebsocketProvider(network_settings_handler.get_host(network))

# ... tries to connect via ipc
def get_ipc_provider(network: str, network_settings_handler: NetworkSettingsHandler) -> BaseProvider:
    return web3.IPCProvider(network_settings_handler.get_host(network))

# connects to node
def get_provider(network: str, network_settings_handler: NetworkSettingsHandler):
    provider = None
    if network_settings_handler.get_host(network)[0:2] == "ws":
        print("Attempting connection via websocket-provider")
        provider = get_websocket_provider(network, network_settings_handler)
    elif network_settings_handler.get_host(network)[0:4] == "http":
        print("Attempting connection via HTTP-provider")
        provider = get_https_provider(network, network_settings_handler)
    elif network_settings_handler.get_host(network)[-3:] == "ipc":
        print("Attempting connection via IPC-Provider")
        provider = get_ipc_provider(network, network_settings_handler)
    else:
        return provider, True
    flag = check_connection_to_web3(provider)
    return provider, not flag

# tests connection
def check_connection_to_web3(provider):
    if provider.isConnected():
        outcome = "successful"
    else:
        outcome = "not successful"
    print(f'Connection to {provider} was {outcome}')
    return provider.isConnected()

# 
def start_scas(scas: List[SCA], provider):
    loop = asyncio.get_event_loop()
    loop.set_debug(False)
    task1 = asyncio.gather(*[sca.get_min_gas_price_block(provider) for sca in scas])
    task2 = asyncio.gather(*[sca.run() for sca in scas])
    all_tasks = asyncio.gather(task1, task2)
    try:
        loop.run_until_complete(all_tasks)
        print("task ran successfully")
    except Exception as e:
        print(e)
        logging.exception("loop exception")


def get_active_networks():
    active_networks = []
    with open('sender/settings/network_settings.json', 'r') as network_file:
        settings_file = json.load(network_file)
        for network in settings_file.keys():
            if settings_file[network]['is_active']:
                active_networks.append(network)
    print(f"active networks {active_networks}")
    return active_networks


def get_configuration(argv):
    if argv is None:
        argv = sys.argv

    # Parse any conf_file specification
    # We make this parser with add_help=False so that
    # it doesn't parse -h and print help.
    conf_parser = argparse.ArgumentParser(
        description=__doc__, # printed with -h/--help
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # Turn off help, so we print all options in response to -h
        add_help=False
        )
    conf_parser.add_argument("-c", "--conf_file",
                        help="Specify config file", metavar="FILE")
    args, remaining_argv = conf_parser.parse_known_args()

    defaults = {"rtime": 86400,   # todo: set reschedule time to odd fraction/day set to hourly
                "rmax": 3,        # todo: set rmax to 50 reschedule amount
                "thresh": 0.8,    # threshhold
                "rot": 1,    # rotation
                "ret": "10 days"    # retention
                 }

    if args.conf_file:
        config = configparser.ConfigParser()
        data = config.read([args.conf_file])
        print(data)
        defaults.update(dict(config.items("Defaults")))

    # Parse rest of arguments
    # Don't suppress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser]
        )
    parser.set_defaults(**defaults)
    parser.add_argument("--rtime", help="Amount of time sca waits before trying to resend")
    parser.add_argument("--rmax", help="Maximum attempts sca tries to send data before deleting order")
    parser.add_argument("-t","--thresh", help="Threshhold ratio gasprice from order to current market gasprice")
    parser.add_argument("-rot", help= "rotation log files in Days")
    parser.add_argument("-ret", help="retention time log files")
    args = parser.parse_args(remaining_argv)
    print("Reschedule time is \"{}\"".format(args.rtime))
    print("Reschedule Max is \"{}\"".format(args.rmax))
    print("Threshhold is \"{}\"".format(args.thresh))
    print("Rotation is \"{}\"".format(args.rot))
    print("Retention is \"{}\"".format(args.ret))
    return args.rtime, args.rmax, args.thresh, args.rot, args.ret


def setup_logging(argv):

    logging_filename = 'sender/main.log'
    logging.getLogger('main')
    handler = handlers.RotatingFileHandler(logging_filename, maxBytes=1024 ** 3, backupCount=2)
    logging.basicConfig(level=logging.INFO, handlers=[handler],
                        format='%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')


    resend_time, resend_tries_max, threshhold, rotation, retention = get_configuration(argv)

def setup_scas(networks, credential_handler):
    scas = []
    for network in networks:
        env = EnvironmentHandler(settings_path="settings", scl_path="scl_database", network=network)
        scl_address = env.scl_address
        network_settings_handler = NetworkSettingsHandler(path=env.network_settings_path, network=network)
        transaction_manager = TransactionManager(path=env.event_db_path, config=env.config_data, scl_path=env.scl_path,
                                                 network=network)
        flag = True
        provider = None
        while flag:
            provider, flag = get_provider(network=network, network_settings_handler=network_settings_handler)
            if flag:
                setup_provider_json(network=network,
                                    path=env.network_settings_path)
        contract = ContractFactory(network, scl_address, provider, credential_handler, env.multiple_credential).build_contract()
        from_block = transaction_manager.get_last_blocknumber(provider)
        bc_connection = BlockchainConnection(contract)
        apis = load_apis() # todo potentially change apis loaded depending on network?
        if apis:
        
            scas.append(SCA(credential_handler=credential_handler,
                        transaction_manager=transaction_manager,
                        environment_handler=env,
                        bc_connection=bc_connection,
                        apis=apis,
                        from_block=from_block))
        # TODO SCA should have from_block as member variable
    return scas, provider


def main(argv=None):
    print_logo()
    setup_logging(argv)
    env = EnvironmentHandler(settings_path="settings", scl_path="scl_database", network='setup')
    if env.multiple_credential:
        credential_handler = MultipleCredentialHandler(credentials_path=env.credentials_path)
    else:
        credential_handler = CredentialHandler(credentials_path=env.credentials_path)
    networks = get_active_networks()
    scas, provider = setup_scas(networks, credential_handler)
    try: 
        start_scas(scas, provider)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
