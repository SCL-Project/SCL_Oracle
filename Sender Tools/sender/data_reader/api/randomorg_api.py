from typing import Tuple
import requests
from abc import ABC, abstractmethod

# DONT USE MUSLTIPLE_NUMBER_HELPER IF YOU ONLY WANT ONE RANDOM NUMBER.
# IT WILL RESULT IN THE WRONG OUTPUT.

# UPPER BOUND MUST BE <= 999999999


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


class RandomOrgAPI(BaseAPI):

    # @variable location is the query relating to the order
    def get_data(self, location: str) -> Tuple[int, bool]:
        
        # the location string gets spit up into their own individual arguments
        borders = location.split(" ")
        
        # if 3 arguments are given, set the second as the lower border and the third as upper border
        if len(borders) == 3:
            n = borders[0]
            upper = borders[2]
            lower = borders[1]

        # if 2 arguments are given, set the second argument as upper border and set lower border to zero
        elif len(borders) == 2:
            n = borders[0]
            upper = borders[1]
            lower = 0

        # if only 1 argument is given, define the range as [0,1]
        elif len(borders) == 1:
            n = borders[0]
            lower = 0
            upper = 1

        # in case 0 or more than two arguments are given, define the range as [0,1] and n as 1
        else:
            n = borders[0]
            lower = 0
            upper = 1

        print(f"n = {n}, lower = {lower}, upper = {upper}")

        # call random.org API function with the defined borders
        result, status = self.random_nr(n, lower, upper)
        print(f"random number = {result}")
        return result, status
    

    def random_nr(self, n, lower, upper):

        # define API url that is being used
        url = "https://api.random.org/json-rpc/2/invoke"

        # declare the required information needed for the API in a format it can understand
        # with the range [lower,upper]
        payload = {
                    "jsonrpc": "2.0",
                    "method": "generateIntegers",
                    "params": {
                        "apiKey": "4d0b0789-0e4f-4ea4-a49f-2e5e67855f01",
                        "n": n, # specify how many random numbers
                        "min": lower,
                        "max": upper, # don't enter anything > 999999999 
                        # "replacement": True # only relevant if n > 1
                    },
                    "id": 69 # will also be returned in the response
                }

        # make the API call
        response = requests.post(url, json=payload, timeout=5)
        
        # wait for the response and react accordingly
        if response.ok:
            n = int(n)
            # case differentiation depending on n
            if n == 1:
                try:
                    result = response.json()["result"]["random"]["data"][0]
                    return result, True
                except requests.Timeout:
                    print("Request timed out.")
                except requests.RequestException as e:
                    print("Some error occurred: ", str(e))
                    return -2, False
            
            # You can create at most 999999999 random numbers according to this function,
            # however this is further restricted by solidity, which can handle
            # at most 78 digits for the result_int of this function.
            elif n > 1:
                i = 0
                result = []
                helper = []

                for number in response.json()["result"]["random"]["data"]:
                    # the ordered random integers is concatenated into one large integer
                    result.append(str(number))
                    # the lengths of each random number are appended to a helper list
                    helper.append(len(str(number)))
                    i += 1
                    
                # the lengths of each random number are appended to this large integer
                for length in helper:
                    result.append(str(length))

                # the total number of random numbers ordered is also appended, since we need to know 
                # how many digits the number of random numbers has (single digits vs. double digits (triple digits would be too much anyway))
                result.append(str(i))

                # Lastly, we append the number of digits that the number of ordered random numbers has.
                # This is the last thing we need to append since we know that this must have only 1 digit (max = 9)
                # (since ordered numbers in the triple digits would be too mush anyway).
                # This means that this last helper digit will always be a single digit and thus doesn't need its own helper digit anymore.
                result.append(str(len(str(i))))
                result_int = int(''.join(result))
                return result_int, True

            else:
                print("n cannot be < 1")
                return -1, False
        else:
            return -1, False


# test to call the script individually with the command <python .\randomorg_api.py> 
# used to test if the API call gives us the requested random number
#  location can be modified as wishes for testing purposes       
if __name__ == '__main__':
    obj = RandomOrgAPI()
    location = "4 1 1000"
    print(obj.get_data(location))
