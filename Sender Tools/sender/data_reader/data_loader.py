from typing import Dict
from sender.data_reader.api import *
from sender.data_reader.base_api import BaseAPI
from sender.data_reader.api.excel_api import ExcelAPI
from sender.data_reader.api.random_api import RandomAPI
from sender.data_reader.api.whitelist_api import WhiteListAPI
from sender.data_reader.api.sbb_api import SBBAPI
from sender.data_reader.api.openweather_api import OpenWeatherAPI
from sender.data_reader.api.coinbase_api import CoinbaseAPI
from sender.data_reader.api.alphavantage_api import AlphaVantageAPI
from sender.data_reader.api.snb_api import SNBAPI
from sender.data_reader.api.metals_api import MetalsAPI
from sender.data_reader.api.coingecko_api import CoinGeckoAPI
from sender.data_reader.api.gas_station_api import GasStationAPI
from sender.data_reader.api.blockcyper_api import BlockcyperAPI
from sender.data_reader.api.randomorg_api import RandomOrgAPI
from sender.data_reader.api.csv_api import CsvAPI


def load_apis() -> Dict[int,BaseAPI]:
    return {1: RandomOrgAPI(),
            2: CsvAPI(),
            3: SNBAPI(1),
            4: SNBAPI(5),
            5: CoinGeckoAPI(1),
            6: AlphaVantageAPI(1),
            }   
