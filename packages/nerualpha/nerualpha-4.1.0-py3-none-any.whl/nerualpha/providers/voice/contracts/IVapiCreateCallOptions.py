from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod



#interface
class IVapiCreateCallOptions(ABC):
    ringingTimer:int
    lengthTimer:int
    machineDetection:str
    randomFromNumber:bool
