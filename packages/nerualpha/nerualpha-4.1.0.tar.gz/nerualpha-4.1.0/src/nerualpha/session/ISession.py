from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.IBridge import IBridge
from nerualpha.providers.logger.ILogContext import ILogContext
from nerualpha.services.commandService.ICommandService import ICommandService
from nerualpha.services.config.IConfig import IConfig
from nerualpha.services.jwt.IJwt import IJWT
from nerualpha.session.IActionPayload import IActionPayload
from nerualpha.session.IFilter import IFilter
from nerualpha.session.wrappedCallback import WrappedCallback


#interface
class ISession(ABC):
    id:str
    commandService:ICommandService
    bridge:IBridge
    config:IConfig
    jwt:IJWT
    @abstractmethod
    def createUUID(self):
        pass
    @abstractmethod
    def getToken(self):
        pass
    @abstractmethod
    def log(self,level,message,context):
        pass
    @abstractmethod
    def wrapCallback(self,route,filters):
        pass
    @abstractmethod
    def constructCommandHeaders(self):
        pass
    @abstractmethod
    def constructRequestHeaders(self):
        pass
    @abstractmethod
    def executeAction(self,actionPayload,method):
        pass
