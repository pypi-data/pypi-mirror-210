from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.bridge import Bridge
from nerualpha.IBridge import IBridge
from nerualpha.smokes.schedulerTestPayload import SchedulerTestPayload
from nerualpha.session.ISession import ISession
from nerualpha.INeru import INeru
from nerualpha.providers.scheduler.IScheduler import IScheduler
from nerualpha.providers.scheduler.scheduler import Scheduler
from nerualpha.providers.scheduler.contracts.startAtParams import StartAtParams
from nerualpha.providers.scheduler.contracts.intervalParams import IntervalParams
from nerualpha.providers.scheduler.contracts.untilParams import UntilParams
from nerualpha.request.requestParams import RequestParams
from nerualpha.request.requestMethods import RequestMethods
from nerualpha.providers.state.state import State
from nerualpha.neru import Neru

@dataclass
class SchedulerSmokeTests:
    scheduler: IScheduler
    neru: INeru
    session: ISession
    bridge: IBridge
    maxInvocations: int = field(default = 2)
    healthChecksUrl: str = field(default = "https://hc-ping.com")
    def __init__(self):
        self.bridge = Bridge()
        self.neru = Neru()
        self.session = self.neru.createSession()
        self.scheduler = Scheduler(self.session)
    
    async def scheduleOnce(self,callback):
        params = StartAtParams()
        params.startAt = self.bridge.isoDate()
        params.callback = callback
        params.payload = SchedulerTestPayload()
        await self.scheduler.startAt(params).execute()
    
    async def scheduleRecurring(self,callback):
        params = StartAtParams()
        params.startAt = self.bridge.isoDate()
        params.callback = callback
        params.payload = SchedulerTestPayload()
        params.interval = IntervalParams()
        params.interval.cron = "*/1 * * * *"
        params.interval.until = UntilParams()
        params.interval.until.maxInvocations = self.maxInvocations
        params.interval.until.date = self.bridge.toISOString(3 * 60)
        await self.scheduler.startAt(params).execute()
    
    async def onScheduledOnce(self,payload,successPathname):
        if payload == "test payload":
            requestParams = RequestParams()
            requestParams.method = RequestMethods.POST
            requestParams.url = f'{self.healthChecksUrl}/{successPathname}'
            await self.bridge.requestWithoutResponse(requestParams)
        
    
    async def onScheduledRecurring(self,sessionId,successPathname):
        session = self.neru.getSessionById(sessionId)
        state = State(session)
        await state.incrby("count",1)
        count = await state.get("count")
        if count is self.maxInvocations:
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
