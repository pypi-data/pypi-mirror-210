from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod



#interface
class ICommandService(ABC):
    @abstractmethod
    def executeCommand(self,url,method,data = None,headers = None):
        pass
