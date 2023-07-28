# Receiver-Tools

The Receiver-Tools repository provides all the information and resources needed to interact with the SCL Oracle as a receiver.

## Overview

In the SCL Oracle system, receivers have the ability to order specific off-chain information known as commitments by specifying the corresponding Commitment IDs. This repository offers the necessary tools and documentation for receivers to seamlessly integrate with the oracle and retrieve the requested information.

## Abstract Smart Contract: SCL_informed.sol

To enable your smart contract to receive information from the SCL Oracle, you need to import the abstract smart contract `SCL_informed.sol` into your own smart contract code before deploying it. This abstract contract facilitates the communication between your smart contract and the oracle, ensuring that only the oracle can send information to your smart contract.

## Usage

To utilize the SCL Oracle as a receiver, follow these steps:

1. Import the `SCL_informed.sol` abstract smart contract into your smart contract code.
2. Deploy your smart contract, passing the address of the SCL Oracle as a constructor input variable.
3. Use the `Order` function within your smart contract to place an order for the desired information.
4. Once the information becomes available, it will be delivered to the `mailbox` function in your smart contract. Modify the `mailbox` function to process the received information according to your requirements.
5. If needed, you can cancel an unfilled order using the `CancelOrder` function. This will reimburse the sender fee associated with the order.

More detailed instructions on how to order from the existing two commitments (random.org API & CSV API) are provided as a PDF file on the Intranet. Follow this link  to view it.

## SCL_informed.sol

The `SCL_informed.sol` abstract smart contract provides the following functions:

- `_GetTransactionCosts`: Calculates the value you need to send with the `Order` function, which includes the sender fee and the gas cost for the delivery transaction.
- `Order`: Places an order for the specified commitment, query, order date, gas limit, and gas price.
- `CancelOrder`: Allows you to cancel an unfilled order, resulting in a reimbursement of the sender fee.

Ensure that you import `SCL_informed.sol` and utilize its functions within your smart contract to interact with the SCL Oracle effectively.

## Additional Information

This section provides additional details about the SCL Oracle:

### Smart Contracts Lab Addresses

- Polygon Mainnet: 0x4b8781De7f9104F47eaf8B61431EbAdaB713c61f
- Mumbai Testnet: 0x4b8781De7f9104F47eaf8B61431EbAdaB713c61f

### Smart Contracts Lab Commitments

The SCL Oracle currently supports the following commitments:

- Commitment ID 1: Random Number Generator
- Commitment ID 2: Excel CSV File Reader
- Commitment ID 3: SNB Repo Reference Rates (SARON)
- Commitment ID 4: SNB Yields on Bond Issues

Please refer to the specific commitment documentation for more information on how to order the corresponding information.

## Contributing

Contributions to the Receiver-Tools repository are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](../MIT-LICENSE).

## Acknowledgements

- The Receiver-Tools repository is maintained by the Smart Contracts Lab (SCL).
- Special thanks to the SCL team for their contributions to the SCL Oracle system.
