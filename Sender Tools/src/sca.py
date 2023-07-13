from src.blockchain_connection import BlockchainConnection
from sender.data_reader.base_api import BaseAPI
from web3.providers.base import BaseProvider
from typing import Tuple, Dict, List
import asyncio
import json
from web3.datastructures import AttributeDict
from src.credential_handler import CredentialHandler
from src.transaction_manager import TransactionManager
from src.environment_handler import EnvironmentHandler
from web3.exceptions import TransactionNotFound
import logging
from web3 import Web3


class SCA:
    def __init__(
            self,
            credential_handler: CredentialHandler,
            transaction_manager: TransactionManager,
            bc_connection: BlockchainConnection,
            environment_handler: EnvironmentHandler,
            apis: Dict[int, BaseAPI],
            from_block: int = 0,
            to_block: int or str = "latest",  # This is awkward
            gas_price: int = 0
    ):
        self.log = logging.getLogger("SCA")

        self.credentials_handler = credential_handler
        self.transaction_manager = transaction_manager
        self.environment_handler = environment_handler
        self.bc_connection = bc_connection
        self.apis = apis
        self.from_block = from_block
        print("from block: ", from_block)
        self.max_block_range = 5000
        self.to_block = self.bc_connection.get_latest_block_number()
        if self.to_block - self.from_block > self.max_block_range:
            self.to_block = self.from_block + self.max_block_range
        self.gas_Price = gas_price
        self.senderID = self.bc_connection.get_sender_id()
        self.sleep_time = 10

    async def run(self):
        # TODO: integrate SCA Activity test
        while True:
            try:
                if self.to_block -100000 > self.from_block:
                    self.to_block = self.from_block + 100000
                if self.to_block > self.from_block:
                    self.log.info(f"handle blocks in {self.transaction_manager.network}"
                                  f" {self.from_block}, {self.to_block}")
                    self.handle_new_orders()
                    self.handle_current_orders()
                    self.from_block = self.to_block
                else:
                    self.log.info(f"No new block found. Sleeping for {self.sleep_time} seconds")
                    pass
                    # print(f"No new block found. Sleeping for {self.sleep_time} seconds")
                self.to_block = self.bc_connection.get_latest_block_number()
                self.transaction_manager.update_last_blocknumber_file(self.to_block)

                if self.to_block - self.from_block > self.max_block_range:
                    self.to_block = self.from_block + self.max_block_range
                await asyncio.sleep(self.sleep_time)
            except TimeoutError:
                self.log.exception("TimeoutError")

                self.max_block_range = int(self.max_block_range/2)
                self.to_block=self.from_block+self.max_block_range
                self.transaction_manager.update_last_blocknumber_file(self.to_block)

    def handle_new_orders(self):
        order_events = self.get_new_order_events()
        sent_transactions = self.transaction_manager.get_stored_orderIDs()
        cleaned_order_events = self.clean_order_events(order_events, sent_transactions)
        self.handle_upcoming_orders(cleaned_order_events)

    def get_valid_commitment_events(self):
        return self.bc_connection.get_new_commitment_events(self.from_block, self.to_block, self.senderID)

    def get_new_order_events(self):
        return self.bc_connection.get_new_order_events(self.from_block, self.to_block)

    def clean_order_events(self, order_events: List[AttributeDict], db_transactions) -> List[AttributeDict]:
        order_events = self.drop_already_sent(order_events, db_transactions)
        order_events = self.drop_orders_with_data_delivered_event(order_events)
        order_events = self.drop_activity_tests_orders(order_events)
        return order_events

    @staticmethod
    def drop_already_sent(order_events: List[AttributeDict], db_transactions: List[str]) -> List[AttributeDict]:
        cleaned_order_events = []
        for order_event in order_events:
            if order_event["transactionHash"] not in db_transactions:
                cleaned_order_events.append(order_event)

        return cleaned_order_events

    def drop_orders_with_data_delivered_event(self, order_events: List[AttributeDict]) -> List[AttributeDict]:
        cleaned_order_events = []
        data_delivered_events = self.bc_connection.get_data_delivered_events(self.from_block, self.to_block)
        for order_event in order_events:
            already_sent = False
            for data_delivered_event in data_delivered_events:
                if order_event['args']['orderID'] == data_delivered_event['args']['orderID']:
                    already_sent = True
            if not already_sent:
                cleaned_order_events.append(order_event)

        return cleaned_order_events

    def update_gas_price_order(self, order, new_gasprice):
        with open(self.transaction_manager.path + str(order['order_data']['orderID']) + '.json', 'r') as orderfile:
            order = json.load(orderfile)
            order['order_data']['_gasPrice'] = new_gasprice

        with open(self.transaction_manager.path + str(order['order_data']['orderID']) + '.json', 'w',
                  encoding='utf-8') as file:
            file.write(json.dumps(order, ensure_ascii=False, indent=self.transaction_manager.indent))

    def check_update_gas_price_order(self, order):
        gas_price_changed_events = self.bc_connection.get_gas_price_changed_events(from_block=order['blockNumber'],
                                                                                   to_block=self.to_block)
        affected_order_events = [event for event in gas_price_changed_events if
                                 order['order_data']['orderID'] == event['args']['OrderID']]
        if len(affected_order_events) != 0:
            if len(affected_order_events) > 1:
                affected_order_events = [affected_order_events[-1]]
            self.update_gas_price_order(order, new_gasprice=affected_order_events[0]['args']['_newGasPrice'])

    @staticmethod
    def drop_activity_tests_orders(order_events: List[AttributeDict]) -> List[AttributeDict]:
        cleaned_order_events = []
        for order_event in order_events:
            if order_event["args"]["_location"] != 'SCA_Activity_Test':
                cleaned_order_events.append(order_event)

        return cleaned_order_events

    def handle_upcoming_orders(self, cleaned_order_events: List[AttributeDict]):
        for order in cleaned_order_events:
            event_data = order['args']
            self.log.info(f"{self.transaction_manager.network}: storing order {event_data['orderID']}")
            self.transaction_manager.store_order(order)

    def handle_pending_orders(self, order, pending_orders, sender_PIN):
        for pending_order in pending_orders:
            relay_tx_hash = pending_order['relay_tx_hash']
            nonce = pending_order['nonce']
            order_data = pending_order['order_data']
            self.log.debug(f"Pending transaction found (orderID: {order_data['orderID']}"
                           f" and gas_Price: {order_data['_gasPrice']})")
            try:
                self.bc_connection.get_transaction_receipt(relay_tx_hash)
                self.transaction_manager.update_order_as_sent(pending_order, relay_tx_hash, nonce)
                self.log.info('Pending order updated to sent')
            except TransactionNotFound:
                if nonce < self.bc_connection.get_nonce(sender_PIN, False):
                    # TODO: insert bool dropped?
                    self.log.info('(nonce) Pending transaction dropped. No need to replace it.')
                    self.transaction_manager.update_order_as_sent(pending_order, relay_tx_hash, nonce)
                else:
                    # replace transaction
                    self.log.info('Trying to replace pending transaction..')
                    self.replace_transaction(sender_PIN, order, nonce, pending_order)

    def handle_current_orders(self):
        current_orders = self.get_current_orders()
        for order in current_orders:
            order_data = order['order_data']
            sender_PIN = order_data['_PIN']
            pending_orders = self.get_pending_orders(sender_PIN)
            # compare gasPrice with gasPrices used in the last mined block
            if int(order_data['_gasPrice']) < float(self.environment_handler.config_data['threshold']) * self.gas_Price:
                self.transaction_manager.reschedule_order(order)
                self.log.info(f"Order with OrderID {order_data['orderID']} has a gasPrice which is too low."
                              f" ({order_data['_gasPrice']}). Order rescheduled")
            # check for pending orders
            elif len(pending_orders) == 0:
                try:
                    datapoint, status = self.get_data_from_api(order_data['commitmentID'], order_data['_location'])
                    self.send_data(sender_PIN, order, datapoint, status, True)
                except KeyError:
                    self.log.exception(f"Commitment ID {order_data['commitmentID']} not associated with any api")
            else:
                self.handle_pending_orders(order, pending_orders, sender_PIN)

    def get_pending_orders(self, sender_PIN: str):
        return self.transaction_manager.get_pending_orders(sender_PIN)

    def get_current_orders(self):
        return self.transaction_manager.get_current_orders()

    def get_data_from_api(self, commitment_id: int, location: str) -> Tuple[int, bool]:
        return self.apis[commitment_id].get_data(location)

    def update_relay_status(self, order, transaction_detail):
        relay_tx_hash = transaction_detail['relay_tx_hash']
        nonce = transaction_detail['nonce']
        try:
            self.bc_connection.get_transaction_receipt(relay_tx_hash)
            self.log.info('updating as sent order')
            self.transaction_manager.update_order_as_sent(order, relay_tx_hash, nonce)
        except TransactionNotFound:
            self.transaction_manager.store_relay_information(order, relay_tx_hash, nonce)

    def send_data(self, sender_PIN, order, datapoint, status, pending):
        self.check_update_gas_price_order(order)
        transaction_details = self.bc_connection.send_data(sender_PIN, order['order_data'], datapoint, status, pending)
        self.update_relay_status(order, transaction_details)

    def replace_transaction(self, sender_PIN, order, nonce, pending_order):
        order_data = order['order_data']
        if int(order_data['_gasPrice']) > 1.125 * int(pending_order['order_data']['_gasPrice']):
            try:
                # send replacement transaction
                datapoint, status = self.get_data_from_api(order_data['commitmentID'], order_data['_location'])
                transaction_details = self.bc_connection.replace_transaction(sender_PIN, nonce, order_data, datapoint,
                                                                             status)
                # reschedule pending transaction
                self.transaction_manager.reschedule_order(pending_order)
                return self.update_relay_status(order, transaction_details)
            except KeyError:
                self.log.exception(f"Commitment ID {order_data['commitmentID']} not associated with any api")
        else:
            self.log.debug('Gas Price of current orders to low to replace the pending transaction')
            self.transaction_manager.reschedule_order(order)
            return self.transaction_manager.reschedule_order(order)

    async def get_min_gas_price_block(self, provider):
        # TODO: add better estimate (i.e. eth gas station or scl api)
        maxFeePerGas = self.bc_connection.get_maxFeePerGas()
        while True:
            gas_prices = []
            i = 0
            while True:
                try:
                    gas_prices.append(self.bc_connection.get_transaction_by_block(self.to_block, i)['gasPrice'])
                    i += 1
                except TransactionNotFound:  # This Error gets thrown on Main/Ropsten network
                    break
                except ValueError:  # This Error gets thrown on Ganache-local network
                    self.log.exception("ValueError_get_min_gas_price_block")
                    break
            try:
                self.gas_Price = min(gas_prices)
                self.log.info(f'gasPrice updated to {self.gas_Price} (maxFeePerGas estimated to {maxFeePerGas}')
            except ValueError:
                self.log.exception("ValueError_get_min_gas_price_block")
                web3 = Web3(provider)
                self.gas_Price = web3.eth.generate_gas_price()
                self.log.info(f'gasPrice updated to {self.gas_Price} (maxFeePerGas estimated to {maxFeePerGas}')
                pass
            await asyncio.sleep(3600)
