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

    def is_logged_in(self, **kwargs):
        return IsLoggedInAction.run(self)

    def login(self, username, password, **kwargs):
        return LogInAction.run(self, username, password)

    def logout(self, **kwargs):
        return LogOutAction.run(self)

    def compose(self, board, title, body, pid=None, gid=None, **kwargs):
        '''
        title can have as many as 49 ascii chars,
        which is 24.5 chinese chars
        '''
        return ComposeAction.run(self, board, title, body, pid, gid)

    def fetch_post(self, board, pid, num, **kwargs):
        return FetchPostAction.run(self, board, pid, num)

    def fetch_topic(self, board, pid, idx=None, **kwargs):
        return FetchTopicAction.run(self, board, pid, idx)

    def fetch_page(self, board, idx=None, **kwargs):
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
    #ret = client.fetch_top()
    #ret = client.fetch_hot()
    #client.fetch_all_board()
    #client.fetch_emoticon()

    #client.login('obash', 'changeme')
    #print client.is_logged_in()
    #ret = client.fetch_subscription()
    #client.logout()
    #print client.is_logged_in()
    #client.compose('test', u'鼠辈，竟敢伤我' * 7, '0123456789' * 10)
    #ret = client.fetch_page('D_Computer')
    #print ret.headers
    #ret = client.fetch_page('D_Computer', ret.prev_idx)
    #print ret.headers
    #ret = client.fetch_post('Pictures', 1346856094, 18428)
    import pdb
    pdb.set_trace()
    ret = client.fetch_topic('Pictures', 1346856094)

