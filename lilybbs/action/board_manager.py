# -*- coding=utf-8 -*-
import re
from time import sleep

from lilybbs.action.base import BaseAction
from lilybbs.exc import NetworkError
from lilybbs.models import BoardManager, Board, Section


class FetchBoardManagerAction(BaseAction):
    ACTION = 'bbsboa'

    def __init__(self, client, sec):
        super(FetchBoardManagerAction, self).__init__(client)
        self.sec = sec

    def setup(self):
        self.params = {'sec': self.sec}
        self.body = {}

    def parse(self):
        try:
            m = re.search(ur'\[(\w+?)区\]<hr', self.html, re.UNICODE)
            text = m.group(1)
        except AttributeError:
            raise NetworkError(u'请勿过快刷新页面')
        ret = Section(self.sec, text)
        items = self.soup.findAll('tr')[1:]
        for i in items:
            cells = i.findAll('td')
            s = cells[5].text[2:]
            # Some board may have a voting in progress
            if s.endswith(u'V'):
                s = s[:-1]
            board = Board(cells[2].text, s)
            ret.append(board)
        return ret

    @classmethod
    def run(cls, client):
        ret = BoardManager(filename=None)
        for i in range(12):
            sleep(0.5)
            act = cls(client, i)
            act.setup()
            act.fetch()
            sec = act.parse()
            ret.append(sec)
        return ret

