from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.bridge import Bridge
from nerualpha.IBridge import IBridge
from nerualpha.session.ISession import ISession
from nerualpha.providers.assets.assets import Assets
from nerualpha.neru import Neru
from nerualpha.request.requestParams import RequestParams
from nerualpha.request.requestMethods import RequestMethods

@dataclass
class AssetsSmokeTests:
    assets: Assets
    session: ISession
    bridge: IBridge
    healthChecksUrl: str = field(default = "https://hc-ping.com")
    def __init__(self):
        self.bridge = Bridge()
        neru = Neru()
        self.session = neru.createSession()
        self.assets = Assets(self.session)
    
    async def uploadAndGetRemoteFile(self,filePath,remoteDir,successPathname):
        files = [filePath]
        await self.assets.uploadFiles(files,remoteDir).execute()
        file = await self.assets.getRemoteFile(remoteDir + "/" + filePath).execute()
        if file is not None:
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
