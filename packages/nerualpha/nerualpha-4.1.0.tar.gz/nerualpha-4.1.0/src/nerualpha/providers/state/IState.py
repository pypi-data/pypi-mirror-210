from dataclasses import dataclass, field, asdict
from typing import Dict, List, Generic, TypeVar
from abc import ABC, abstractmethod

from nerualpha.providers.state.expireOptions import ExpireOptions


#interface
class IState(ABC):
    @abstractmethod
    def set(self,key,value):
        pass
    @abstractmethod
    def get(self,key):
        pass
    @abstractmethod
    def delete(self,key):
        pass
    @abstractmethod
    def hdel(self,htable,key):
        pass
    @abstractmethod
    def hexists(self,htable,key):
        pass
    @abstractmethod
    def hgetall(self,htable):
        pass
    @abstractmethod
    def hmget(self,htable,keys):
        pass
    @abstractmethod
    def hvals(self,htable):
        pass
    @abstractmethod
    def hget(self,htable,key):
        pass
    @abstractmethod
    def hincrby(self,htable,key,value):
        pass
    @abstractmethod
    def hlen(self,htable):
        pass
    @abstractmethod
    def hset(self,htable,keyValuePairs):
        pass
    @abstractmethod
    def rpush(self,list,value):
        pass
    @abstractmethod
    def lpush(self,list,value):
        pass
    @abstractmethod
    def rpop(self,list,count):
        pass
    @abstractmethod
    def lpop(self,list,count):
        pass
    @abstractmethod
    def lrem(self,list,value,count):
        pass
    @abstractmethod
    def ltrim(self,list,startPos,endPos):
        pass
    @abstractmethod
    def linsert(self,list,before,pivot,value):
        pass
    @abstractmethod
    def lindex(self,list,position):
        pass
    @abstractmethod
    def lset(self,list,position,value):
        pass
    @abstractmethod
    def incrby(self,key,value):
        pass
    @abstractmethod
    def decrby(self,key,value):
        pass
    @abstractmethod
    def expire(self,key,seconds,option = None):
        pass
    @abstractmethod
    def llen(self,list):
        pass
    @abstractmethod
    def lrange(self,list,startPos,endPos):
        pass
