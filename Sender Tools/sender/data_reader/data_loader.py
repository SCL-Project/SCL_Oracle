from typing import Dict
from sender.data_reader.api import *
from sender.data_reader.base_api import BaseAPI

from sender.data_reader.api.randomorg_api import RandomOrgAPI
from sender.data_reader.api.API_template import API_Class_Name


def load_apis() -> Dict[int,BaseAPI]:
    return {1: RandomOrgAPI(),
            2: API_Class_Name(),
            }   
