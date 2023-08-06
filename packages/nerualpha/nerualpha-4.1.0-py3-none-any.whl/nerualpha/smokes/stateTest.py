from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.IBridge import IBridge
from nerualpha.session.ISession import ISession
from nerualpha.providers.state.IState import IState
from nerualpha.INeru import INeru
from nerualpha.bridge import Bridge
from nerualpha.providers.state.state import State
from nerualpha.request.requestParams import RequestParams
from nerualpha.request.requestMethods import RequestMethods
from nerualpha.neru import Neru

@dataclass
class StateSmokeTests:
    neru: INeru
    state: IState
    session: ISession
    bridge: IBridge
    healthChecksUrl: str = field(default = "https://hc-ping.com")
    def __init__(self):
        self.bridge = Bridge()
        self.neru = Neru()
        self.session = self.neru.createSession()
        self.state = State(self.session)
    
    async def getset(self,successPathname):
        key = "test-key"
        testData = "test-data"
        await self.state.set(key,testData)
        receivedData = await self.state.get(key)
        if receivedData == testData:
            requestParams = RequestParams()
            requestParams.method = RequestMethods.POST
            requestParams.url = f'{self.healthChecksUrl}/{successPathname}'
            await self.bridge.requestWithoutResponse(requestParams)
        
    
    async def delete(self,successPathname):
        key = "test-key"
        testData = "test-data"
        await self.state.set(key,testData)
        await self.state.delete(key)
        value = await self.state.get(key)
        if value is None:
            requestParams = RequestParams()
            requestParams.method = RequestMethods.POST
            requestParams.url = f'{self.healthChecksUrl}/{successPathname}'
            await self.bridge.requestWithoutResponse(requestParams)
        
    
    def reprJSON(self):
        result = {}
        dict = asdict(self)
        keywordsMap = {"from_":"from","del_":"del","import_":"import","type_":"type"}
        for key in dict:
            val = getattr(self, key)

            if val is not None:
                if type(val) is list:
                    parsedList = []
                    for i in val:
                        if hasattr(i,'reprJSON'):
                            parsedList.append(i.reprJSON())
                        else:
                            parsedList.append(i)
                    val = parsedList

                if hasattr(val,'reprJSON'):
                    val = val.reprJSON()
                if key in keywordsMap:
                    key = keywordsMap[key]
                result.__setitem__(key.replace('_hyphen_', '-'), val)
        return result
