# SCL Oracle

The SCL Oracle is a decentralized oracle system that allows senders and receivers to interact with off-chain information on the blockchain. This repository contains the necessary tools and documentation for both senders and receivers to seamlessly integrate with the SCL Oracle.

## Overview

The SCL Oracle serves as a bridge between on-chain smart contracts and off-chain data sources, enabling the retrieval and delivery of real-world information to the blockchain. It ensures the secure and reliable transmission of off-chain data, enhancing the capabilities and functionality of smart contracts.

The repository is structured into two main sub-folders:

- **Sender Tools**: Contains the necessary resources and information for senders to interact with the SCL Oracle, including the sender README.md file and related tools.

- **Receiver Tools**: Provides all the information and resources needed for receivers to interact with the SCL Oracle, including the receiver README.md file and relevant tools.

## Sender Tools

The Sender Tools folder contains everything required for senders to utilize the SCL Oracle for automating the fulfillment of off-chain information requests. It includes the sender README.md file, which provides a comprehensive guide on how to set up and configure the server application (SCA) to link commitments, automate API calls, and relay information to receivers' smart contracts.

## Receiver Tools

The Receiver Tools folder provides all the necessary information and resources for receivers to seamlessly integrate with the SCL Oracle. It includes the receiver README.md file, which guides receivers on how to import the abstract smart contract (`SCL_informed.sol`) into their own smart contract, place orders for specific commitments, and process the received information in their smart contract's `mailbox` function.

## Usage

To utilize the SCL Oracle as a sender or receiver, follow these steps:

1. Navigate to the respective Sender Tools or Receiver Tools sub-folder.
2. Follow the instructions provided in the README.md file specific to your role (sender or receiver).
3. Configure the necessary environment variables and dependencies.
4. Deploy and interact with the SCL Oracle as per the guidelines provided in the respective README.md files.

Please note that both senders and receivers need to ensure they have the required access and authorization to interact with the SCL Oracle and fulfill information requests securely.

## Contributing

Contributions to the SCL Oracle repository are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](./MIT-LICENSE).

## Acknowledgements

- The SCL Oracle is developed and maintained by the Smart Contracts Lab (SCL) team.
- Special thanks to the developers and contributors of the SCL Oracle for their support and guidance.
