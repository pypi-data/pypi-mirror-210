import os
import uuid

from django.conf import settings

from . import SnowyFlake


def get_uuid4_hex():
    hh = uuid.uuid4().hex
    return hh


def get_setting_value(name):
    value = os.environ.get(name, getattr(settings, name, None))
    if value is None:
        raise NotImplementedError("没有配置这个参数%s" % name)
    return value


def get_env_value(name, default=None):
    value = os.environ.get(name, default)
    if value is None:
        raise NotImplementedError("没有配置这个参数%s" % name)
    return value


def get_snowy_uuid() -> str:
    ''' 获取雪花ID
    考虑了 服务名称、pod 名称、时间序列、
    '''
    return SnowyFlake().get_snowy_uuid()
