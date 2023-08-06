from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.request.responseTypes import ResponseTypes

T = TypeVar("T")


#interface
class IRequestParams(ABC,Generic[T]):
    method:str
    url:str
    data:T
    headers:Dict[str,str]
    responseType:ResponseTypes
