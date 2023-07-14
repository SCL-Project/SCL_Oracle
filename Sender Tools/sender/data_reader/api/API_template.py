from typing import Tuple
import requests
from abc import ABC, abstractmethod

# The BaseAPI class is needed to receive the query from the order
# This functionshould not be changed
# @variable location refers to the _query
class BaseAPI(ABC):
    @abstractmethod
    def get_data(self,location: str) -> Tuple[int, bool]:
        """
        returns data given location
        Args:
            location: string that holds location data, e.g. 'A1' for an excel
        Returns
            datapoint: an integer
            status: True if no error, else False
        """


class API_Class_Name(BaseAPI):

    # @function get_data receives the _query
    # the query is analysed, and the respective api function is called
    # @variable location is the query relating to the order
    def get_data(self, location: str) -> Tuple[int, bool]:
        
        # Inside this function, you can define how the _query (referred to as "location") is being processed.
        # for example, you can split the location to retrieve multiple arguments from the query
        # and define different API- calls depending on the query

        # in this example, we split the location variable into two variables by seperating them by a space
        # location = "arg1 arg2"
        args = location.split(" ")
        query_arg1 = args[0]
        query_arg2 = args[1]

        # At the end of this function, you will need to call the API function to retrieve the result
        # you than have to return the result together with the booleran variable "status" which will be
        # set to "true", if the API call was succesfull, and "false" otherwise
        # call random.org API function with the defined borders
        result, status = self.api_function(query_arg1, query_arg2)
        print(f"random number = {result}")
        return result, status
    

    def api_function(query_arg1, query_arg2):

        # define API url that is being used
        url = "https://api.random.org/json-rpc/2/invoke"

        # declare the required information needed for the API in a format it can understand
        payload = {
                    "jsonrpc": "2.0",
                    "method": "generateIntegers",
                    "params": {
                        "apiKey": "4d0b0789-0e4f-4ea4-a49f-2e5e67855f01",
                        "min": query_arg1,
                        "max": query_arg2, # don't enter anything > 999999999 
                        # "replacement": True # only relevant if n > 1
                    },
                    "id": 69 # will also be returned in the response
                }

        # make the API call
        response = requests.post(url, json=payload, timeout=5)
        
        # wait for the response and react accordingly
        if response.ok:
            #define here what gets returned when the API call was succesfull
            return response,True
            
        else:
            # define here what gets returned when the API call was not successful
            return -1, False


# test to call the script individually with the command <python .\API_template.py> 
# used to test if the API call gives us the expected result
# location can be modified as wished for testing purposes       
if __name__ == '__main__':
    obj = API_Class_Name()
    location = "insert your test query here"
    print(obj.get_data(location))
