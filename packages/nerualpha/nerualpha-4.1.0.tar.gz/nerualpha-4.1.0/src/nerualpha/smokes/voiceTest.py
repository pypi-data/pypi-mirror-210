from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.INeru import INeru
from nerualpha.session.ISession import ISession
from nerualpha.providers.voice.IVoice import IVoice
from nerualpha.providers.voice.voice import Voice
from nerualpha.providers.voice.contracts.vapiEventParams import VapiEventParams
from nerualpha.neru import Neru
from nerualpha.providers.voice.contracts.channelPhoneEndpoint import ChannelPhoneEndpoint
from nerualpha.providers.voice.contracts.IChannelPhoneEndpoint import IChannelPhoneEndpoint
from nerualpha.providers.voice.contracts.IAcceptInboundCallEvent import IAcceptInboundCallEvent
from nerualpha.providers.state.state import State
from nerualpha.providers.state.IState import IState
from nerualpha.request.requestParams import RequestParams
from nerualpha.bridge import Bridge

@dataclass
class VoiceSmokeTests:
    events: List[str]
    bridge: Bridge
    state: IState
    voice: IVoice
    session: ISession
    neru: INeru
    def __init__(self):
        self.bridge = Bridge()
        self.neru = Neru()
        self.session = self.neru.createSession()
        self.voice = Voice(self.session)
        self.state = State(self.session)
        self.events = []
    
    async def checkIncomingEventsAndHitHealthEndpointIfSuccessful(self,status,successPathname):
        await self.state.incrby(status,1)
        started = await self.state.get("started")
        ringing = await self.state.get("ringing")
        answered = await self.state.get("answered")
        completed = await self.state.get("completed")
        allEventsReceived = started and ringing and answered and completed
        if allEventsReceived:
            requestParams = RequestParams()
            requestParams.method = "POST"
            requestParams.url = f'https://hc-ping.com/{successPathname}'
            await self.bridge.requestWithoutResponse(requestParams)
            self.events = []
        
        return
    
    async def answer(self,event):
        conversation = await self.voice.createConversation()
        await conversation.acceptInboundCall(event).execute()
        await conversation.sayText({"text": "Hello from Vonage!"}).execute()
    
    async def onInboundCall(self,callback,to):
        vonageNumber = ChannelPhoneEndpoint(to)
        await self.voice.onInboundCall(callback,vonageNumber).execute()
    
    async def call(self,fromNumber,toNumber,eventCallback):
        _fromNumber = ChannelPhoneEndpoint(fromNumber)
        _toNumber = ChannelPhoneEndpoint(toNumber)
        toNumbers = [_toNumber]
        nccoActions = [{"action": "talk","text": "Hello from Vonage! Listening for DTMF input..."},{"action": "input","type": ["dtmf"],"dtmf": {"maxDigits": 1,"submitOnHash": True,"timeOut": 10}}]
        response = await self.voice.vapiCreateCall(_fromNumber,toNumbers,nccoActions).execute()
        onEventParams = VapiEventParams()
        onEventParams.callback = eventCallback
        onEventParams.vapiUUID = response.uuid
        await self.voice.onVapiEvent(onEventParams).execute()
    
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
