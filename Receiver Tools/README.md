# Receiver-Tools

This folder offers several tools that simplify the interaction with the Smart Contracts Lab oracle.

## SCL_informed.sol

SCL*informed.sol should be imported into the Solidity code of your smart contract application. It is an \_abstract contract* which means it is not a standalone contract but assists you in connecting to the oracle. By importing it into your contract, it allows you to call the following three functions:

- The _GetTransactionCosts_ function calculates the value you need to send with the Order function. This value corresponds to the sum of the sender fee and the gas for the delivery transaction.

- The _Order_ function is used to place an order as described in the corresponding commitment.

- The _CancelOrder_ function allows you to cancel an unfilled order (for any reason). As a result, the sender fee will be reimbursed to the address from which the Order function was called .

## Additional Information

### Smart Contracts Lab Addresses

- Polygon Mainnet: 0x6e0d61EA7eFbD198229c12Eb919BFd5C4caeDF5c
- Mumbai testnet: 0x6e0d61EA7eFbD198229c12Eb919BFd5C4caeDF5c

### Smart Contracts Lab Commitments

- 1 Random Number Generator
