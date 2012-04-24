# -*- coding: utf-8 -*-
from urllib2 import URLError

class Error(Exception):
    DEFAULT_MESSAGE = u'出错了'.encode('utf-8')
    def __init__(self, message=None):
        super(Error, self).__init__(message or self.DEFAULT_MESSAGE)

class ContentError(Error):
    DEFAULT_MESSAGE = u'无法解析页面'.encode('utf-8')
    def __init__(self, message=None):
        super(ContentError, self).__init__(message or self.DEFAULT_MESSAGE)

class NetworkError(Error):
    DEFAULT_MESSAGE = u'网络抽风了'.encode('utf-8')
    def __init__(self, message=None):
        super(NetworkError, self).__init__(message or self.DEFAULT_MESSAGE)

