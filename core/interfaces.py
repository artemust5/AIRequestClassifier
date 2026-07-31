from abc import ABC, abstractmethod
from typing import List
from core.models import RawRequest, ParsedRequest

class DataReader(ABC):
    @abstractmethod
    def read(self, filepath: str) -> List[RawRequest]:
        pass

class DataWriter(ABC):
    @abstractmethod
    def write_json(self, data: List[ParsedRequest], filepath: str) -> None:
        pass

    @abstractmethod
    def write_report(self, data: List[ParsedRequest], filepath: str) -> None:
        pass

class LLMClient(ABC):
    @abstractmethod
    async def process_request_async(self, request: RawRequest) -> ParsedRequest:
        pass