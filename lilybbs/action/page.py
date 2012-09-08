# -*- coding=utf-8 -*-
from datetime import datetime

from lilybbs.action.base import BaseAction
from lilybbs.models import Header, Page


class FetchPageAction(BaseAction):
    '''
    '''
    ACTION = 'bbstdoc'
    DATE_FORMAT = r'%b %d %H:%M'

    def __init__(self, client, board, idx=None):
        super(FetchPageAction, self).__init__(client)
        self.board = board
        self.idx = int(idx) if idx else None

    def setup(self):
        self.params = {'board': self.board}
        if self.idx:
            self.params['start'] = self.idx
        self.body = {}

    def parse(self):
        items = self.soup.findAll('tr')[1:]
        ret = Page(self.board)
        for i in items:
            h = self.make_header(i)
            if not h.num:
                continue
            ret.headers.append(h)
        # TODO
        for i in self.soup.body.center.findAll('a', recursive=False):
            if i.text == u'上一页':
                ret.prev_idx = int(self.parse_href(i['href'], 'start')) - 1
#            if i.text == u'下一页':
#                ret.next_idx = int(self.parse_href(i['href'], 'start')) - 1

        ret.headers.reverse()
        return ret

    def make_header(self, item):
        year = datetime.now().year
        cells = item.findAll('td')
        ret = Header()
        ret.board = self.board
        # topped headers do not have num
        try:
            ret.num = int(cells[0].text) - 1
        except ValueError:
            ret.num = None
        ret.author = cells[2].text.strip()
        ret.date = cells[3].text.strip()
        ret.date = datetime.strptime(ret.date, self.DATE_FORMAT)
        # FIXME
        ret.date = ret.date.replace(year=year)
        ret.title = cells[4].text.strip()[2:]
        ret.pid = self.parse_pid(cells[4].a['href'])
        tmp = cells[5].text.strip()
        if tmp.find('/') != -1:
            tmp = tmp.split('/')
            ret.reply_count = int(tmp[0])
            ret.view_count = int(tmp[1])
        else:
            ret.view_count = int(tmp)
        return ret

