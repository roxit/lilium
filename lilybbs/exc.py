# -*- coding: utf-8 -*-


class LilyError(Exception):
    DEFAULT_MESSAGE = u'出错了'.encode('utf-8')

    def __init__(self, message=None):
        super(LilyError, self).__init__(message or self.DEFAULT_MESSAGE)


class ContentError(LilyError):
    DEFAULT_MESSAGE = u'无法解析页面'.encode('utf-8')

    def __init__(self, message=None):
        super(ContentError, self).__init__(message or self.DEFAULT_MESSAGE)


class NetworkError(LilyError):
    DEFAULT_MESSAGE = u'网络抽风了'.encode('utf-8')

    def __init__(self, message=None):
        super(NetworkError, self).__init__(message or self.DEFAULT_MESSAGE)


class InvalidLogin(LilyError):
    DEFAULT_MESSAGE = u'登录错误'.encode('utf-8')

    def __init__(self, message=None):
        super(InvalidLogin, self).__init__(message or self.DEFAULT_MESSAGE)


class NotLoggedIn(LilyError):
    DEFAULT_MESSAGE = u'没有登录'.encode('utf-8')

    def __init__(self, message=None):
        super(NotLoggedIn, self).__init__(message or self.DEFAULT_MESSAGE)

