# -*- coding=utf-8 -*-
from urlparse import urlparse, parse_qs

from lilybbs.action.base import BaseAction
from lilybbs.models import Post


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
        self.body = {}

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

