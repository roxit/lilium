# -*- coding=utf-8 -*-
from urlparse import urlparse, parse_qs

from lilybbs.action.base import BaseAction
from lilybbs.exc import FrequencyLimitExceeded, NotLoggedIn
from lilybbs.models import Post
from lilybbs.utils import wrap_zh


class FetchPostAction(BaseAction):
    ACTION = 'bbscon'

    def __init__(self, client, board, pid, num):
        super(FetchPostAction, self).__init__(client)
        self.board = board
        self.pid = pid
        self.num = num

    def setup(self):
        self.params = {'board': self.board,
                'file': self.pid2str(self.pid),
                'num': self.num}
        self.payload= {}

    def parse(self):
        txt = self.soup.find('textarea').text
        ret = Post(self.board, self.pid, self.num)
        ret.parse_post(txt)
        # works for archived post
        s = self.soup.findAll('a')[-1]['href']
        gid = parse_qs(urlparse(s).query).get('gid', None)
        if gid is not None:
            ret.gid = gid[0]
        else:
            ret.gid = None
        return ret


class ComposeAction(BaseAction):
    ACTION = 'bbssnd'
    MAXC = 78

    def __init__(self, client, board, title, body,
            pid=None, gid=None):
        super(ComposeAction, self).__init__(client)
        self.board = board
        self.title = title
        self.body = body
        self.pid = pid
        self.gid = gid

    def setup(self):
        self.params = {'board': self.board}
        self.body = self.body.replace(u'\r\n', u'\n')
        self.body = self.body.replace(u'\r', u'\n')
        lines = self.body.split(u'\n')
        body = []
        for l in lines:
            body.append(u'\r\n'.join(wrap_zh(l, self.MAXC)))
        self.payload = {'title': self.title, 'text': '\r\n'.join(body)}
        if self.pid:
            self.payload['reid'] = self.pid
            self.payload['pid'] = self.gid

    def parse(self):
        if 'Refresh' in self.html:
            return True
        else:
            if u'两次发文间隔过密' in self.soup.text:
                raise FrequencyLimitExceeded()
            raise NotLoggedIn(self.soup.text)

