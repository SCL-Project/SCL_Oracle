/* SCL Parent Contract "SCL_informed.sol"
   Copyright (c) 2019-2020 Smart Contracts Lab
   To order data from Smart Contracts Lab: 
   
     (1) Import this file into your Solidity file.
     
     (2) Let your contract inherit the abstract contract "SCL_informed".
        
     (3) Use the view function GetTransactionCosts to determine the accurate ETH value for the function call. 
     
     (4) Let one of your functions call the Order function. 
       
     (5) Implement the Mailbox function in your smart contract.
     
     (6) Doublecheck that the modifier "onlySCL" is added to your implementation of the Mailbox function.
    
   Example: 
      
     pragma solidity ^0.8.0; 
     
     import "https://github.com/BlockchainPresence/Blockchain-Project/blob/master/Version%201.1.10%20(active)/Use%20Cases/SCL_informed.sol"

     contract yourContract is SCL_informed {
        
         function Mailbox(uint _orderID, int88 _data, bool _statusFlag) override external payable onlySCL {
         ...
         }
         
         uint32 orderID = SCL.ORDER.value(SCL.GetTransactionCosts(_commitmentID,_gasForMailbox)) (_commitmentID,_gasForMailbox,_location,_orderDate);
      }
    
*/
//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

interface SCL_interface {
    function GetTransactionCosts(
        int64 _commitmentID,
        uint40 _gasForMailbox,
        uint gasPriceInGwei
    ) external view returns (uint transactionCost);

    function Order(
        int64 commitmentID,
        string calldata _query,
        uint32 _orderDate,
        uint40 _gasForMailbox,
        uint64 _gasPriceInGwei
    ) external payable returns (uint32 orderID);

    function cancelOrder(uint32 _orderID) external payable;
}

abstract contract SCL_informed {
    SCL_interface SCL;
    address payable public SCL_Address;
    modifier onlySCL() {
        require(msg.sender == SCL_Address);
        _;
    }

    event ReceiverConnection(address Rec, address indexed SC);

    constructor(address payable addr) {
        emit ReceiverConnection(msg.sender, address(this));
        SCL_Address = addr;
        SCL = SCL_interface(addr);
    }

    function getSCLAddr() external view returns (address payable) {
        return SCL_Address;
    }

    function Mailbox(
        uint32 _orderID,
        int88 _data,
        bool _statusFlag
    ) external payable virtual;

    function getData() public view virtual returns (int88);

    function get_single_random_number() public view virtual returns (int88);

    function multiple_random_numbers() public virtual;

    function get_multiple_random_numbers() public view virtual returns (uint256[] memory);

    function single_csv_datapoint() public virtual;

    function get_single_csv_datapoint() public view virtual returns (string memory);

    function multiple_csv_datapoints() public virtual;

    function get_multiple_csv_datapoints() public view virtual returns (string[] memory);

    fallback() external payable virtual;

    receive() external payable virtual {}
}
