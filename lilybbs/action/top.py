# -*- coding=utf-8 -*-
from .base import BaseAction
from ..models import Header


class FetchTopAction(BaseAction):
    ACTION = 'bbstop10'

    def parse(self):
        items = self.soup.findAll('tr')[1:]
        ret = []
        for i in items:
            cells = i.findAll('td')
            h = Header()
            h.board = cells[1].text.strip()
            h.title = cells[2].text.strip()
            h.pid = self.parse_pid(cells[2].a['href'])
            h.author = cells[3].text.strip()
            h.reply_count = int(cells[4].text.strip())
            ret.append(h)
        return ret
