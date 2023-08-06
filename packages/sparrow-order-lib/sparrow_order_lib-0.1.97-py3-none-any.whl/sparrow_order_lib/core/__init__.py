import os
import time
import socket
import hashlib

class SnowyFlake(object):
    ''' 计算雪花ID '''

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self._last_timestamp = -1
        self._sequence = 0
        self._hostname = socket.gethostname()
        self._service_name = os.environ.get("SERVICE_NAME", "sparrow-order-lib")

    def get_snowy_uuid(self):
        ''' 获取雪花id '''
        timestamp = time.time()
        if timestamp == self._last_timestamp:
            self._sequence += 1
        else:
            self._last_timestamp = timestamp
            self._sequence = 0
        snowy_uuid_str = f"{self._service_name}:{self._hostname}:{timestamp}:{self._sequence}"
        return hashlib.md5(snowy_uuid_str.encode()).hexdigest()
