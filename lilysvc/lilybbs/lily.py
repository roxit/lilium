# -*- coding: utf-8 -*-
import logging
logging.getLogger().setLevel(logging.DEBUG)

from .connection import Connection
from .models import BoardManager, SessionInfo

class Lily:

    def __init__(self):
        self._connection = None
        self.session = None
        self.board_manager = BoardManager()

    @property
    def connection(self):
        if not self.session:
            self._connection = Connection()
        else:
            if not self._connection.is_active_login():
                self.session = self._connection.login(self.session.uid, self.session.password)
        return self._connection

    def load_session(self, session_str):
        session = SessionInfo()
        session.loads(session_str)
        self.connection.load_session(session)
        self.session = session

    def login(self, username, password):
        self.session = self.connection.login(username, password)
        return self.session

    def logout(self):
        self.connection.logout()

    def send_topic(self, board, title, body):
        ret = self.connection.send_topic(board, title, body)

    def fetch_post(board, pid, num):
        ret = self.connection.fetch_post(board, pid, num)
        return ret 

    def fetch_topic(self, board, pid, start=None):
        topic = self.connection.fetch_topic(board, pid, start)
        # remove duplicate post
        if start:
            topic.post_list = topic.post_list[1:]
        return topic

    def fetch_page(self, board, start=None):
        page = self.connection.fetch_page(board, start)
        page.header_list.reverse()
        return page

    def fetch_top10(self):
        page = self.connection.fetch_top10()
        return page

    def fetch_hot(self):
        hot = self.connection.fetch_hot()
        hot[0] = []
        return hot

    def fetch_favorites(self):
        fav = self.connection.fetch_favorites()
        return fav

