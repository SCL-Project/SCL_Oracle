# Receiver-Tools

This folder provides all information needed to interact with the SCL Oracle as a receiver.

In order for your smart contract to be able to receive information from our oracle, you have to import the abstract smart contract `SCL_informed.sol` into your smart contract code before deploying.

When deploying your smart contract, you than have to pass the address of the SCL Oracle as a constructor input variable.

Once your contract is deployed, you can order information by calling the `Order`-function inside your contract.

The ordered information will then be delivered to the `mailbox` function, once the information has been provided by the sender. The inside of the mailbox function can then be modified to call subsequent actions based on the received information.

`commitmentID`  specifies the kind of information you want to order, and also the sender from which you want to order.

`query_`        with this variable you can specify even more the information you want to order. Not every commitment needs a query_

## SCL_informed.sol

SCL_informed.sol should be imported into the Solidity code of your smart contract application. It is an *abstract contract* which means, it is not a standalone contract but assists you in connecting to the oracle. 

By importing it into your contract, it allows you to call the following three functions:

### _GetTransactionCosts_

This function calculates the value you need to send with the Order function. This value corresponds to the sum of the sender fee and the gas for the delivery transaction.

### _Order_ 

This function is used to place an order as described in the corresponding commitment.

This function takes the following input variables:

`_commitmentID`     defines which commitment to order the information from

`_query`            specifies which exact information of that commitment to order (not all commitments have a query)

`_orderDate`        UTC timestamp in seconds, defines when the order should be delivered.

`_gasForMailbox`    specifies the gas limit used for delivering the information to the mailbox. Depends how much gas is used for subsequent internal calls once the information gets to the mailbox.

`_gasPriceInGwei`   specifyies the gas price used for the delivery of the order.

The SCL-Oracle automatically takes the address from which an order has been placed as the delivery address. Therefore, an order has to be placed via a smart contract and can't be done from a wallet address. This ensure that no third party can order data for you which could wrongfully trigger subsequent functions inseîde your contract.

### _CancelOrder_ 

This function allows you to cancel an unfilled order (for any reason). As a result, the sender fee will be reimbursed to the address from which the Order function was called.

### onlySCL-modifier

This modifier ensures that the `mailbox` function can only be called by the SCL Oracle, and no other address.

## Additional Information

### Smart Contracts Lab Addresses

- Polygon Mainnet: 0x6e0d61EA7eFbD198229c12Eb919BFd5C4caeDF5c
- Mumbai testnet: 0x6e0d61EA7eFbD198229c12Eb919BFd5C4caeDF5c

### Smart Contracts Lab Commitments

- 1 Random Number Generator
- 2 Excel CSV File Reader
- 3 SNB Repo Refernece Rates (SARON)
- 4 SNB Yields on Bond Issues
