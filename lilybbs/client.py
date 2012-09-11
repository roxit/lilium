# -*- coding: utf-8 -*-
import logging
import os
import json

from lilybbs.action import *
from lilybbs.connection import Connection
from lilybbs.models import BoardManager, Session

logging.getLogger().setLevel(logging.DEBUG)

ROOT_DIR = os.path.dirname(__file__)


class Client:

    def __init__(self, session=None):
        self.conn = Connection()
        self.session = None
        if session:
            self.load_session(session)
        #self.bm = BoardManager()

    def load_session(self, session):
        if isinstance(session, basestring):
            session = Session.create(session)
        if session:
            self.conn.load_session(session)
        self.session = session

    def check_session(self, **kwargs):
        return CheckSessionAction.run(self)

    def login(self, username, password, **kwargs):
        return LogInAction.run(self, username, password)

    def logout(self, **kwargs):
        return LogOutAction.run(self)

    def compose(self, board, title, body, pid=None, gid=None, **kwargs):
        '''
        title can have as many as 49 ascii chars,
        which is 24.5 chinese chars
        '''
        pid = int(pid) if pid else None
        gid = int(pid) if gid else None
        return ComposeAction.run(self, board, title, body, pid, gid)

    def fetch_post(self, board, pid, num, **kwargs):
        pid = int(pid)
        num = int(num)
        return FetchPostAction.run(self, board, pid, num)

    def fetch_topic(self, board, pid, idx=None, **kwargs):
        pid = int(pid)
        idx = int(idx) if idx else None
        return FetchTopicAction.run(self, board, pid, idx)

    def fetch_page(self, board, idx=None, **kwargs):
        idx = int(idx) if idx else None
        return FetchPageAction.run(self, board, idx)

    def fetch_top(self, **kwargs):
        return FetchTopAction.run(self)

    def fetch_hot(self, **kwargs):
        return FetchHotAction.run(self)

    def fetch_subscription(self, **kwargs):
        return FetchSubscriptionAction.run(self)

    def fetch_all_board(self, **kwargs):
        bm = FetchBoardManagerAction.run(self)
        bm.dump_xml()

    def fetch_emoticon(self, **kwargs):
        ret = FetchEmoticonAction.run(self)
        fn = os.path.join(ROOT_DIR, 'assets/emoticon.json')
        with open(fn, 'w') as f:
            json.dump(ret, f)


if __name__ == '__main__':
    client = Client()
    #client.fetch_all_board()
    #client.fetch_emoticon()

