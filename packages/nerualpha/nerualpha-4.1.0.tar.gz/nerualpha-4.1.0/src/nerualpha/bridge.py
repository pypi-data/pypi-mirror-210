import json
import os
import re
import aiohttp
import jwt
import pendulum
import time
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import asdict
from urllib.parse import urlparse, quote
from nerualpha.IBridge import IBridge
from urllib.parse import urljoin
from nerualpha.services.config.pathObject import PathObject

logging.basicConfig(level=logging.DEBUG)

class Bridge(IBridge):
    def encodeUriComponent(self, s):
        return quote(s)

    def parsePath(self, path):
        dir_name, base_name = os.path.split(path)
        name, ext = os.path.splitext(base_name)
        pathObject = PathObject()
        pathObject.root = os.path.splitdrive(path)[0] + os.sep
        pathObject.dir = dir_name
        pathObject.base = base_name
        pathObject.ext = ext
        pathObject.name = name
        return pathObject

    def testRegEx(self, str, regExp):
        if re.match(regExp, str):
            return True
        else:
            return False

    def isInteger(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def substring(self, str, start, end):
        return str[start:end]

    def jsonStringify(self, data):
        return json.dumps(data, default=lambda o: o.reprJSON(),
                          sort_keys=True, indent=4)

    def jsonParse(self, str):
        return json.loads(str)

    def getEnv(self, name):
        return os.getenv(name)
    
    def constructFormData(self, data):
        formData = aiohttp.FormData()
        for formDataObject in data:
            if hasattr(formDataObject, 'filename'):
                formData.add_field(formDataObject.name, formDataObject.value, filename=formDataObject.filename)
            else:
                formData.add_field(formDataObject.name, formDataObject.value)
        return formData

    async def request(self, params):
        method = params.method
        headers = params.headers if params.headers is not None else {}
        url = params.url
        data = params.data

        if 'Content-Type' in headers:
            if headers['Content-Type'] == 'multipart/form-data':
                data = self.constructFormData(data)
                # Delete multipart/form-date header to let aiohttp calculate its length
                del headers['Content-Type']
            elif headers['Content-Type'] == 'application/json':
                if hasattr(data, 'reprJSON'):
                    data = data.reprJSON()
                data = json.dumps(data)

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, data=data, headers=headers) as resp:
                body = await resp.read()

                if params.responseType == 'stream':
                    return body

                try:
                    return json.loads(body)
                except Exception as e:
                    pass
                return body.decode('utf-8')

    def runBackgroundTask(self, task):
        loop = asyncio.get_event_loop()
        loop.create_task(task)

    def createReadStream(self, path):
        return open(path, 'rb')

    async def requestWithoutResponse(self, params):
        await self.request(params)

    def uuid(self):
        return str(uuid.uuid4())

    def isoDate(self):
        dt = pendulum.now("UTC")
        return dt.to_iso8601_string()

    def toISOString(self, seconds):
        dt = pendulum.now("UTC")
        nt = dt.add(seconds=seconds)
        return nt.to_iso8601_string()

    def jwtSign(self, payload, privateKey, alg, options = None):
        data = {k: v for k, v in asdict(payload).items() if v is not None}

        if options is None:
            headers = {}
        else:
            headers = asdict(options)

        t = jwt.encode(data, privateKey, alg, headers)

        return t

    def jwtVerify(self, token, privateKey, algorithm):
        return jwt.decode(token, privateKey, algorithm)

    def jwtDecode(self, token):
        return jwt.decode(token, options={"verify_signature": False})

    def getSystemTime(self):
        return int(time.time())

    def log(self, logAction):
        logging.debug(logAction)

    def getObjectKeys(self, obj):
        return list(obj.keys())
