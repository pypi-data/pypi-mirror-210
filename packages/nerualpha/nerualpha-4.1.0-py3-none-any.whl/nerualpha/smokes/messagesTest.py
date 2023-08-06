from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.IBridge import IBridge
from nerualpha.session.ISession import ISession
from nerualpha.providers.messages.IMessages import IMessages
from nerualpha.INeru import INeru
from nerualpha.bridge import Bridge
from nerualpha.providers.messages.messages import Messages
from nerualpha.providers.messages.contracts.messageContact import MessageContact
from nerualpha.providers.messages.contracts.smsMessage import SMSMessage
from nerualpha.request.requestParams import RequestParams
from nerualpha.request.requestMethods import RequestMethods
from nerualpha.providers.state.state import State
from nerualpha.neru import Neru

@dataclass
class MessagesSmokeTests:
    neru: INeru
    messages: IMessages
    session: ISession
    bridge: IBridge
    healthChecksUrl: str = field(default = "https://hc-ping.com")
    def __init__(self):
        self.bridge = Bridge()
        self.neru = Neru()
        self.session = self.neru.createSession()
        self.messages = Messages(self.session)
    
    async def onMessage(self,callback,fromNumber,toNumber):
        fromContact = MessageContact()
        fromContact.type_ = "sms"
        fromContact.number = fromNumber
        toContact = MessageContact()
        toContact.type_ = "sms"
        toContact.number = toNumber
        await self.messages.onMessage(callback,fromContact,toContact).execute()
    
    async def onEvent(self,callback,fromNumber,toNumber):
        clientContact = MessageContact()
        clientContact.type_ = "sms"
        clientContact.number = fromNumber
        applicationContact = MessageContact()
        applicationContact.type_ = "sms"
        applicationContact.number = toNumber
        await self.messages.onMessageEvents(callback,clientContact,applicationContact).execute()
    
    async def sendMessage(self,fromNumber,toNumber,message):
        smsMessage = SMSMessage()
        smsMessage.from_ = fromNumber
        smsMessage.to = toNumber
        smsMessage.text = message
        await self.messages.send(smsMessage).execute()
    
    async def checkIncomingMessageAndHitHealthEndpointIfSuccess(self,message,expectedMessage,successPathname):
        if message == expectedMessage:
            requestParams = RequestParams()
            requestParams.method = RequestMethods.POST
            requestParams.url = f'{self.healthChecksUrl}/{successPathname}'
            await self.bridge.requestWithoutResponse(requestParams)
        
    
    async def checkIncomingEventAndHitHealthEndpointIfSuccess(self,sessionId,status,successPathname):
        session = self.neru.getSessionById(sessionId)
        state = State(session)
        if status == "submitted":
            await state.incrby("submitted",1)
        
        if status == "delivered":
            await state.incrby("delivered",1)
        
        submitted = await state.get("submitted") or 0
        delivered = await state.get("delivered") or 0
        if submitted and delivered:
            requestParams = RequestParams()
            requestParams.method = RequestMethods.POST
            requestParams.url = f'{self.healthChecksUrl}/{successPathname}'
            await self.bridge.requestWithoutResponse(requestParams)
            await state.set("events",None)
        
    
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
