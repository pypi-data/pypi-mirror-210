from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.providers.queue.IQueue import IQueue
from nerualpha.IBridge import IBridge
from nerualpha.services.config.IConfig import IConfig
from nerualpha.session.ISession import ISession
from nerualpha.providers.queue.contracts.ICreateQueueOptions import ICreateQueueOptions
from nerualpha.providers.queue.contracts.createQueuePayload import CreateQueuePayload
from nerualpha.providers.queue.contracts.queueRate import QueueRate
from nerualpha.providers.queue.contracts.ICreateQueuePayload import ICreateQueuePayload
from nerualpha.request.requestParams import RequestParams
from nerualpha.request.requestMethods import RequestMethods
from nerualpha.session.requestInterfaceWithParams import RequestInterfaceWithParams
from nerualpha.providers.queue.contracts.queueDetailsResponse import QueueDetailsResponse
from nerualpha.providers.queue.contracts.IUpdateQueueOptions import IUpdateQueueOptions
from nerualpha.providers.queue.contracts.updateQueuePayload import UpdateQueuePayload
from nerualpha.providers.queue.contracts.IUpdateQueuePayload import IUpdateQueuePayload

@dataclass
class Queue(IQueue):
    session: ISession
    config: IConfig
    bridge: IBridge
    provider: str = field(default = "queue-service")
    def __init__(self,session):
        self.session = session
        self.bridge = session.bridge
        self.config = session.config
    
    def createQueue(self,name,callback,options):
        payload = CreateQueuePayload()
        payload.name = name
        payload.callback = self.session.wrapCallback(callback,[])
        payload.active = options.active
        payload.rate = QueueRate()
        payload.rate.maxInflight = options.maxInflight
        payload.rate.msgPerSecond = options.msgPerSecond
        requestParams = RequestParams()
        requestParams.method = RequestMethods.POST
        requestParams.data = payload
        requestParams.url = self.config.getExecutionUrl(self.provider,"queue")
        requestParams.headers = self.session.constructRequestHeaders()
        return RequestInterfaceWithParams(self.session,requestParams)
    
    def updateQueue(self,queueName,options):
        payload = UpdateQueuePayload()
        payload.rate = QueueRate()
        payload.rate.maxInflight = options.maxInflight
        payload.rate.msgPerSecond = options.msgPerSecond
        requestParams = RequestParams()
        requestParams.method = RequestMethods.POST
        requestParams.data = payload
        requestParams.url = self.config.getExecutionUrl(self.provider,f'queue/{queueName}')
        requestParams.headers = self.session.constructRequestHeaders()
        return RequestInterfaceWithParams(self.session,requestParams)
    
    def list(self):
        requestParams = RequestParams()
        requestParams.method = RequestMethods.GET
        requestParams.data = None
        requestParams.url = self.config.getExecutionUrl(self.provider,"queue")
        requestParams.headers = self.session.constructRequestHeaders()
        return RequestInterfaceWithParams(self.session,requestParams)
    
    def getQueueDetails(self,name):
        requestParams = RequestParams()
        requestParams.method = RequestMethods.GET
        requestParams.data = None
        requestParams.url = self.config.getExecutionUrl(self.provider,f'queue/{name}')
        requestParams.headers = self.session.constructRequestHeaders()
        return RequestInterfaceWithParams(self.session,requestParams)
    
    def deleteQueue(self,name):
        requestParams = RequestParams()
        requestParams.method = RequestMethods.DEL
        requestParams.data = None
        requestParams.url = self.config.getExecutionUrl(self.provider,f'queue/{name}')
        requestParams.headers = self.session.constructRequestHeaders()
        return RequestInterfaceWithParams(self.session,requestParams)
    
    def pauseQueue(self,name):
        requestParams = RequestParams()
        requestParams.method = RequestMethods.PUT
        requestParams.data = None
        requestParams.url = self.config.getExecutionUrl(self.provider,f'queue/{name}/pause')
        requestParams.headers = self.session.constructRequestHeaders()
        return RequestInterfaceWithParams(self.session,requestParams)
    
    def resumeQueue(self,name):
        requestParams = RequestParams()
        requestParams.method = RequestMethods.PUT
        requestParams.data = None
        requestParams.url = self.config.getExecutionUrl(self.provider,f'queue/{name}/resume')
        requestParams.headers = self.session.constructRequestHeaders()
        return RequestInterfaceWithParams(self.session,requestParams)
    
    def enqueue(self,name,data):
        requestParams = RequestParams()
        requestParams.method = RequestMethods.POST
        requestParams.data = data
        requestParams.url = self.config.getExecutionUrl(self.provider,f'queue/{name}/enqueue')
        requestParams.headers = self.session.constructRequestHeaders()
        return RequestInterfaceWithParams(self.session,requestParams)
    
    def enqueueSingle(self,name,data):
        return self.enqueue(name,[data])
    
    def deadLetterList(self,name):
        requestParams = RequestParams()
        requestParams.method = RequestMethods.GET
        requestParams.data = None
        requestParams.url = self.config.getExecutionUrl(self.provider,f'queue/{name}/deadletter')
        requestParams.headers = self.session.constructRequestHeaders()
        return RequestInterfaceWithParams(self.session,requestParams)
    
    def deadLetterDequeue(self,name,count = 1):
        requestParams = RequestParams()
        requestParams.method = RequestMethods.POST
        requestParams.data = None
        requestParams.url = self.config.getExecutionUrl(self.provider,f'queue/{name}/deadletter/pop',{"count": self.bridge.jsonStringify(count)})
        requestParams.headers = self.session.constructRequestHeaders()
        return RequestInterfaceWithParams(self.session,requestParams)
    
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
