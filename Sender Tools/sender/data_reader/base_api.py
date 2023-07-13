from abc import ABC, abstractmethod
from typing import Tuple
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
