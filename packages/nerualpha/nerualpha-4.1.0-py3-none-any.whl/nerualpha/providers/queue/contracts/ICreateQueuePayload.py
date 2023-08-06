from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.session.IWrappedCallback import IWrappedCallback
from nerualpha.providers.queue.contracts.IQueueRate import IQueueRate


#interface
class ICreateQueuePayload(ABC):
    name:str
    active:bool
    rate:IQueueRate
    callback:IWrappedCallback
