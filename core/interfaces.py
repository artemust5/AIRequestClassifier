from abc import ABC, abstractmethod
from typing import List, Dict, Any

class DataReader(ABC):
    @abstractmethod
    def read(self, filepath: str) -> List[Dict[str, Any]]:
        pass

class DataWriter(ABC):
    @abstractmethod
    def write(self, data: List[Dict[str, Any]], filepath: str) -> None:
        pass