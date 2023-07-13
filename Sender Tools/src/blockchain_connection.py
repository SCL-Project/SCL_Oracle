from src.contract import Contract
import logging

class BlockchainConnection:
    def __init__(self, contract: Contract):
        self.contract = contract
        self.log = logging.getLogger("BlockchainConnection")

    def get_latest_block_number(self):
        print(f"block number: {self.contract.get_block_number()}")
        return self.contract.get_block_number()

    def get_sender_id(self):

        return self.contract.get_sender_id()

    def send_data(self, sender_PIN, order: dict, datapoint: int, status: bool, pending: bool):
        self.log.info(order)
        order_id = order['orderID']
        w3 = self.contract.get_provider()
        block = w3.eth.get_block('latest')
        baseFeePerGas = block['baseFeePerGas']
        maxPriorityFeePerGas = int(order['_gasPrice']) - baseFeePerGas - 1
        transaction_details = {
            "nonce": self.contract.get_nonce(sender_PIN, pending),
            "maxFeePerGas": int(order['_gasPrice']),  # EIP1559 gasPrice --> MaxFeePerGas
            "gas": order['_gasForDelivery'],
            "maxPriorityFeePerGas": maxPriorityFeePerGas
        }
        print(f"sending order {order_id} with datapoint {datapoint} and status {status}")

        self.log.info(f"sending order {order_id} with datapoint {datapoint} and status {status}")
        # ToDo: catch ValueError
        return self.contract.relay(sender_PIN, order_id, datapoint, status, transaction_details)

    def replace_transaction(self, sender_PIN, nonce: int, order: dict, datapoint: int, status: bool):
        order_id = order['orderID']
        transaction_details = {
            "nonce": int(nonce),
            "maxFeePerGas": int(order['_gasPrice']),
            "gas": order['_gasForDelivery']

        }
        self.log.info('replacement transaction sent')
        return self.contract.replace_transaction(sender_PIN, order_id, datapoint, status, transaction_details, order)

    def get_new_order_events(self, from_block: int, to_block:  int or str):
        return self.contract.get_new_order_events(from_block, to_block)

    def get_new_commitment_events(self, sender_id: int, from_block: int, to_block: int or str):
        return self.contract.get_new_commitment_events(sender_id, from_block, to_block)

    def get_data_delivered_events(self, from_block: int, to_block: int or str):
        return self.contract.get_data_delivered_events(from_block, to_block)

    def get_gas_price_changed_events(self, from_block: int, to_block: int or str):
        return self.contract.get_gas_price_changed(from_block, to_block)

    def get_transaction(self, tx_hash: str):
        return self.contract.get_transaction(tx_hash)
    
    def get_transaction_by_block(self, block: int, index: int):
        return self.contract.get_transaction_by_block(block, index)

    def get_transaction_receipt(self, tx_hash: str):
        return self.contract.get_transaction_receipt(tx_hash)

    def get_nonce(self, sender_PIN, pending: bool):
        return self.contract.get_nonce(sender_PIN, pending)

    def get_maxFeePerGas(self):
        return self.contract.get_maxFeePerGas()

    def update_last_block(self):
        event = self.contract.get_new_order_events()
        print(event)
