import asyncio

from eth_abi.codec import ABICodec
from web3 import Web3
from web3._utils.filters import construct_event_filter_params
from web3.datastructures import AttributeDict
from web3.exceptions import TimeExhausted
from web3._utils.events import get_event_data
from typing import List
import logging


class Contract:
    """Contract class for creating an instance of SCL-smart contract. Includes functionalities for interacting with it.

    Args:
        contract: Current deployed SCL-oracle smart contract
        senders (dict): Credentials of logged-in sender(s).
    """

    def __init__(self, contract, senders: dict):
        self.contract = contract
        self.senders = senders
        self.wallets = list(self.senders.keys())
        self.log = logging.getLogger("Contract")

    def __str__(self):
        return f"Contract(contract={self.contract}, senders={self.senders})"

    def get_provider(self):
        return self.contract.web3

    def get_sender_id(self):       
        first_item = list(self.senders.items())[0]
        pinx = first_item[0]
        idxy = self.contract.functions.GetSenderID().call({"from": pinx})
        print(f"sender ID = {idxy}")
        return idxy

    def get_all_events(self, event, from_block: int, to_block: int):
        web3 = self.contract.web3
        abi = event._get_event_abi()
        codec: ABICodec = web3.codec
        address = self.contract.address

        data_filter_set, event_filter_params = construct_event_filter_params(
            abi,
            codec,
            address=address,
            fromBlock=from_block,
            toBlock=to_block
        )

        logs = web3.eth.get_logs(event_filter_params)
        all_events = []
        for log in logs:
            evt = get_event_data(codec, abi, log)
            all_events.append(evt)
        return all_events

    def get_logs(self, from_block, to_block, topics):
        return self.contract.web3.eth.get_logs(
            {'fromBlock': from_block,
             'toBlock': to_block,
             'topics': [
                 topics
             ]
             }
        )

    def get_new_commitment_events(self, sender_id: int, from_block: int, to_block: int) -> List[AttributeDict]:
        w3 = self.contract.web3
        new_commitment_event = self.contract.events.newCommitment
        event_signature_hash = w3.keccak(text="newCommitment(int64,int64)").hex()
        list_commitment_events = self.get_logs(from_block, to_block, event_signature_hash)
        commitment_events = [
            get_event_data(
                new_commitment_event.web3.codec,
                new_commitment_event._get_event_abi(),
                event
            )
            for event in list_commitment_events
        ]
        return [event for event in commitment_events if
                dict(event)['args']['_PIN'] in self.wallets and dict(event)['address'] == self.contract.address]

    def get_new_order_events(self, from_block: int, to_block: int or str) -> List[AttributeDict]:
        w3 = self.contract.web3
        event_signature_hash = w3.keccak(text="newOrder(address,uint32,int64,string,uint32,uint40,uint64,address)").hex()
        new_order_event = self.contract.events.newOrder
        list_order_events = self.get_logs(from_block, to_block, event_signature_hash)
        order_events = [
            get_event_data(
                new_order_event.web3.codec,
                new_order_event._get_event_abi(),
                event
            )
            for event in list_order_events
        ]
        return [event for event in order_events if
                dict(event)['args']['_PIN'] in self.wallets and dict(event)['address'] == self.contract.address]

    def get_data_delivered_events(self, from_block: int, to_block: int or str):
        w3 = self.contract.web3
        data_delivered_event = self.contract.events.dataDelivered
        event_signature_hash = w3.keccak(text="dataDelivered(uint32,bool,bool)").hex()
        list_data_delivered_events = self.get_logs(from_block, to_block, event_signature_hash)
        data_delivered_events = [
            get_event_data(
                data_delivered_event.web3.codec,
                data_delivered_event._get_event_abi(),
                event
            )
            for event in list_data_delivered_events
        ]
        return data_delivered_events

    def get_gas_price_changed(self, from_block: int, to_block: int or str):
        w3 = self.contract.web3
        gas_price_changed_event = self.contract.events.gasPriceChanged
        event_signature_hash = w3.keccak(text="gasPriceChanged(uint32,uint64)").hex()
        list_gas_price_changed_events = self.get_logs(from_block, to_block, event_signature_hash)
        gas_price_changed_events = [
            get_event_data(
                gas_price_changed_event.web3.codec,
                gas_price_changed_event._get_event_abi(),
                event
            )
            for event in list_gas_price_changed_events
        ]
        return gas_price_changed_events

    def get_nonce(self, sender_PIN, pending: bool):
        return self.contract.web3.eth.get_transaction_count(sender_PIN)

    def relay(self, sender_PIN, order_id, datapoint, status, transaction_details):
        tx = self.contract.functions.Relay(order_id, datapoint, status).buildTransaction(transaction_details)
        signed_tx = self.contract.web3.eth.account.sign_transaction(tx, private_key=self.senders[sender_PIN])
        tx_hash = self.contract.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        nonce = transaction_details['nonce']
        tx_hash = self.wait_for_transaction_receipt(tx_hash)
        self.log.info(f'txhash: {tx_hash}')
        return {'nonce': nonce, 'relay_tx_hash': tx_hash}

    def replace_transaction(self, sender_PIN, order_id, datapoint, status, transaction_details):
        return self.relay(sender_PIN, order_id, datapoint, status, transaction_details)

    def wait_for_transaction_receipt(self, tx_hash: bytes):
        try:
            self.contract.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            print("sent")
        except (TimeExhausted, TimeoutError, asyncio.exceptions.TimeoutError):
            print('Transaction was not mined in 60 second. Gas Price might be too low.')
        return tx_hash.hex()

    def get_transaction(self, tx_hash: str):
        return self.contract.web3.eth.get_transaction(tx_hash)

    def get_transaction_receipt(self, tx_hash: str):
        return self.contract.web3.eth.get_transaction_receipt(tx_hash)

    def get_block_number(self):
        return self.contract.web3.eth.block_number

    def get_transaction_by_block(self, block: int, index: int):
        return self.contract.web3.eth.get_transaction_by_block(block, index)

    def get_maxFeePerGas(self):
        try:
            maxPriorityFeePerGas = self.contract.web3.eth.max_priority_fee
        except ValueError:
            self.log.exception("Connected with ganache, does not support max_priority_fee as of 2.5.22")
            return self.contract.web3.eth.gas_price
        baseFeePerGas = self.contract.web3.eth.fee_history(10, 'latest')['baseFeePerGas']
        return maxPriorityFeePerGas + sum(baseFeePerGas) / len(baseFeePerGas)