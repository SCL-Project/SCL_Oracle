import os
import json
import time
import logging
import re
from typing import Dict
from web3 import Web3
from web3.datastructures import AttributeDict
from web3.middleware import geth_poa_middleware
from web3 import exceptions


class TransactionManager:
    def __init__(self, path: str, config: Dict, scl_path, network):
        self.indent = 4
        self.path = path
        self.config = config
        self.network = network
        self.checkpoint_path = scl_path + f'/block_checkpoint_{self.network}.txt'
        self.log = logging.getLogger("TransactionManager")

    def write_json(self, orderID: str, mode: str, order):
        with open(self.path + orderID + '.json', mode, encoding='utf-8') as file:
            file.write(json.dumps(order, ensure_ascii=False, indent=self.indent))

    def get_order_files(self):
        directory = os.fsencode(self.path)
        return [os.fsdecode(file) for file in os.listdir(directory)]

    def get_stored_orderIDs(self, is_sent: bool = None):
        stored_orderID = []
        for filename in self.get_order_files():
            with open(self.path + filename, 'r', encoding='utf-8') as orderfile:
                order = json.load(orderfile)
                if is_sent is None:
                    stored_orderID.append(order['order_data']['orderID'])
                elif order['is_sent'] == is_sent:
                    stored_orderID.append(order['order_data']['orderID'])
                else:
                    self.log.info(f'{self.network}: skipping {order["order_data"]["orderID"]}')
                    pass
        return stored_orderID

    def store_order(self, order: AttributeDict):
        stored_orderIDs = self.get_stored_orderIDs()
        if order['args']['orderID'] in stored_orderIDs:
            self.log.info(f'{self.network}: already stored order with ID:{order["args"]["orderID"]}')
            return
        orderID = str(order['args']['orderID'])
        order_data = dict(order['args'])
        event_data = {
            'tx_hash': order['transactionHash'].hex(),
            'is_sent': 0,
            'sent_date': 64701260400,  # init super far in the future
            'order_data': order_data,
            'relay_tx_hash': None,
            'nonce': 0,
            'rescheduled': 0,
            'blockNumber': order['blockNumber']
        }
        self.write_json(orderID=orderID, mode='a+', order=event_data)
        self.update_last_blocknumber()

    def get_pending_orders(self, sender_PIN: str):
        pending_orders = []
        for filename in self.get_order_files():
            with open(self.path + filename, 'r', encoding='utf-8') as orderfile:
                order = json.load(orderfile)
                if order['order_data']['_PIN'] == sender_PIN and not order['is_sent'] and order[
                    'relay_tx_hash'] is not None:
                    pending_orders.append(order)
        return pending_orders

    def get_current_orders(self):
        current_orders = []
        for filename in self.get_order_files():
            with open(self.path + filename, 'r', encoding='utf-8') as orderfile:
                order = json.load(orderfile)
                if not order['is_sent'] and order['rescheduled'] < int(self.config['reschedule_amount']) \
                        and order['order_data']['_orderDate'] < time.time():
                    current_orders.append(order)
        return current_orders

    def update_order_as_sent(self, order, relay_tx_hash, nonce):
        orderID = str(order['order_data']['orderID'])
        with open(self.path + orderID + '.json', 'r', encoding='utf-8') as orderfile:
            order = json.load(orderfile)
            order['relay_tx_hash'] = relay_tx_hash
            order['nonce'] = nonce
            order['is_sent'] = 1
            order['sent_date'] = time.time()
        with open(self.path + orderID + '.json', 'w', encoding='utf-8') as orderfile:
            orderfile.write(json.dumps(order, ensure_ascii=False, indent=self.indent))

    def store_relay_information(self, order, relay_tx_hash, nonce):
        orderID = str(order['order_data']['orderID'])
        with open(self.path + orderID + '.json', 'r', encoding='utf-8') as orderfile:
            order = json.load(orderfile)
            order['relay_tx_hash'] = relay_tx_hash
            order['nonce'] = nonce
        with open(self.path + orderID + '.json', 'w', encoding='utf-8') as orderfile:
            orderfile.write(json.dumps(order, ensure_ascii=False, indent=self.indent))

    def reschedule_order(self, order):
        orderID = str(order['order_data']['orderID'])
        with open(self.path + orderID + '.json', 'r', encoding='utf-8') as orderfile:
            order = json.load(orderfile)
            order_date = order['order_data']['_orderDate'] + int(self.config['reschedule_time'])
            order['order_data']['_orderDate'] = order_date
            order['rescheduled'] = order['rescheduled'] + 1
            order['relay_tx_hash'] = None
            order['nonce'] = 0
        with open(self.path + orderID + '.json', 'w', encoding='utf-8') as orderfile:
            orderfile.write(json.dumps(order, ensure_ascii=False, indent=self.indent))

    def update_last_blocknumber(self):
        orderfiles = self.get_order_files()

        orderfiles.sort(key=lambda f: int(re.sub('\D', '', f)))
        try:
            filename = orderfiles[-1]
            with open(self.path + filename, 'r', encoding='utf-8') as orderfile:
                order = json.load(orderfile)
                if os.path.exists(self.checkpoint_path):
                    with open(self.checkpoint_path, 'r') as checkpoint_file:
                        block_number = int(checkpoint_file.read())
                else:
                    block_number = 0

                if order['blockNumber'] > block_number:
                    block_number = order['blockNumber']
                    with open(self.checkpoint_path, 'w') as checkpoint_file:
                        checkpoint_file.write(str(block_number))
        except IndexError:
            with open(self.checkpoint_path, 'r') as checkpoint_file:
                block_number = int(checkpoint_file.read())
        return block_number
    
    def update_last_blocknumber_file(self, block_number):
        with open(self.checkpoint_path, 'w') as checkpoint_file:
            checkpoint_file.write(str(block_number))

    def get_last_blocknumber(self, provider):
        if provider == 'test':
            blockNumber = 0
        else:
            web3 = Web3(provider)
            try:
                block = web3.eth.get_block('latest')
            except exceptions.ExtraDataLengthError:
                web3.middleware_onion.inject(geth_poa_middleware, layer=0)
                block = web3.eth.get_block('latest')
            block_number = block['number']
        if os.path.exists(self.checkpoint_path):
            block_number = self.update_last_blocknumber()
        else:
            with open(self.checkpoint_path, 'w') as checkpoint_file:
                checkpoint_file.write(str(block_number))
        return block_number


    def remove_order(self, order):
        # remover order that order['sent_date'] is over a week ago? maybe adjust value in retention config.
        pass


if __name__ == '__main__':
    tx_manager = TransactionManager('../sender/scl_database/orders_main/',
                                    {'reschedule_amount': 3, 'reschedule_time': 100})
    tx_hash = '0xtesttest'
    blockNumber = 69
    order_data = {"_PIN": "0xB32a8Cc21A64E07eC2971B9AD3E2d468f760A602",
                  "orderID": 7,
                  "commitmentID": 23,
                  "_location": "a1",
                  "_orderDate": 1631476465,
                  "_gasForDelivery": 41000,
                  "_gasPrice": 30000000000,
                  "receiverAddress": "0xE563b295Fc16A0A5d67aD1E6DE958F785daD78bb"}
    event_data = {
        'tx_hash': tx_hash,
        'is_sent': 0,
        'sent_date': 0,
        'order_data': order_data,
        'relay_tx_hash': None,
        'nonce': 0,
        'rescheduled': 0,
        'blockNumber': blockNumber
    }
    # tx_manager.store_order(event_data=event_data)
    # tx_manager.get_stored_transaction_hashes()
    # tx_manager.get_pending_orders()
    # tx_manager.get_current_orders()
    # tx_manager.update_order_as_sent(event_data, 'successthxhash', 20)
    # print(tx_manager.get_last_blocknumber())