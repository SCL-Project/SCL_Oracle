import json


def reduce_abi(abi):
    reduced_abi = []
    desired_keys = {
        'dataDelivered',
        'newOrder',
        'Relay',
        'GetSenderID',
        'GasPriceChanged'
    }
    for i, val in enumerate(abi):
        try:
            if abi[i]['name'] in desired_keys:
                reduced_abi.append(abi[i])
        except KeyError:
            pass
    return reduced_abi


if __name__ == "__main__":
    with open('contract_abi.json') as file:
        reduced_abi = reduce_abi(json.load(file))
    with open('reduced_contract_abi.json', 'w') as f:
        json.dump(reduced_abi, f, indent=4)
