# -*- coding=utf-8 -*-
from lilybbs.action.base import BaseAction
from lilybbs.exc import NotLoggedIn
from lilybbs.utils import wrap_zh


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
        lines = self.body.split(u'\r\n')
        body = []
        for l in lines:
            body.append(u'\r\n'.join(wrap_zh(l, self.MAXC)))
        self.body = {'title': self.title, 'text': body}
        if self.pid:
            self.body['reid'] = self.pid
            self.body['pid'] = self.gid

    def parse(self):
        if 'Refresh' in self.html:
            return
        else:
            raise NotLoggedIn()

