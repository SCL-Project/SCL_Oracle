# Server Convenience Application (SCA)

The Server Convenience Application (SCA) is a server application designed to simplify the process for senders of the SCL oracle. This application provides an automated solution for fulfilling orders placed by receivers for specific off-chain information known as commitments. The SCA is designed as a Python-based Docker container that can be easily deployed on the sender's server.

## Overview

In the context of this application, senders have the ability to register commitments on the SCL oracle. These commitments represent various types of off-chain information that receivers can request. Previously, senders had to manually fulfill each order individually for each commitment. However, with the SCA, this process is streamlined and automated.

The SCA enables senders to link their commitments to an API. When a new order arrives for a particular commitment (identified using Commitment IDs) and the specified order date has been reached, the SCA automatically initiates an API call to gather the requested information. Once the information is retrieved, the SCA calls the relay function on the SCL oracle using the sender's registered wallet address. This relay function then sends the information to the smart contract of the receiver.

## Features

- Simplifies the order fulfillment process for senders of the SCL oracle.
- Provides automation for retrieving and relaying off-chain information.
- Allows senders to link their commitments to an API.
- Supports identification of commitments using Commitment IDs.
- Initiates API calls to gather ordered information.
- Utilizes registered wallet addresses for relaying information to receivers' smart contracts.
- Dockerized application for easy deployment on a sender's server.
- Developed using Python.

## Usage

To use the SCA, follow these steps:

1. Clone this repository to your local machine.
2. Configure the necessary environment variables, such as API credentials and wallet addresses, in the `.env` file.
3. Build the Docker image by running `docker build -t sca-app .` in the root directory of the application.
4. Start the Docker container using `docker run -d --name sca-container sca-app`.
5. Register your commitments with the SCL oracle using the provided API endpoints.
6. Monitor the SCA for incoming orders.
7. Once an order arrives for a commitment and the order date is reached, the SCA will automatically make an API call to retrieve the requested information.
8. The SCA will then relay the information to the receiver's smart contract using your registered wallet address.

## Configuration

The SCA requires certain environment variables to be set for proper functioning. Create a `.env` file in the root directory of the application and populate it with the following variables:

### data_loader.py

This file is used to link an API to a commitmentID.

The `data_loader.py` file located at `Sender Tools/sender/data_reader/data_loader.py` needs to be configured as follows:

```python
from sender.data_reader.api.{api-name} import {api-name}

def load_apis() -> Dict[int, BaseAPI]:
    return {{commitmentID}: {api-name}()

```

- you need to import your API class into the file
- you need to specify the commitmentID and link it to the respective API class.

### {api-filename}.py

This file is used to to make an api call. The file is located at `Sender Tools/sender/api`.

## Contributing

Contributions to the SCA are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- The SCA is built using Python and Docker.
- Special thanks to the developers and contributors of the SCL oracle for their support and guidance.
