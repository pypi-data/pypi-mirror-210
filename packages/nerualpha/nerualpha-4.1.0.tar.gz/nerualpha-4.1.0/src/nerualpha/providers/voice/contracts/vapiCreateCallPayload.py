from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.providers.voice.contracts.IChannelPhoneEndpoint import IChannelPhoneEndpoint
from nerualpha.providers.voice.contracts.IVapiCreateCallOptions import IVapiCreateCallOptions
from nerualpha.providers.voice.contracts.IVapiCreateCallPayload import IVapiCreateCallPayload

@dataclass
class VapiCreateCallPayload(IVapiCreateCallPayload):
    ncco: List[Dict[str,object]]
    to: List[IChannelPhoneEndpoint]
    from_: IChannelPhoneEndpoint
    ringing_timer: int = None
    length_timer: int = None
    machine_detection: str = None
    random_from_number: bool = None
    def __init__(self,from_,to,ncco,options = None):
        self.from_ = from_
        self.to = to
        self.ncco = ncco
        if options is not None:
            if options.machineDetection is not None:
                self.machine_detection = options.machineDetection
            
            if options.randomFromNumber is not None:
                self.random_from_number = options.randomFromNumber
            
            if options.ringingTimer is not None:
                self.ringing_timer = options.ringingTimer
            
            if options.lengthTimer is not None:
                self.length_timer = options.lengthTimer
            
        
    
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
