# -*- coding=utf-8 -*-
from .base import BaseAction
from ..models import Topic, Post
from ..exc import ContentError


class FetchTopicAction(BaseAction):
    ACTION = 'bbstcon'

    def __init__(self, client, board, pid, idx=None):
        super(FetchTopicAction, self).__init__(client)
        self.board = board
        self.pid = pid
        self.idx = int(idx) if idx else None

    def setup(self):
        self.params = {'board': self.board, 'file': self.pid2str(self.pid)}
        if self.idx:
            self.params['start'] = self.idx
        self.payload = {}

    def parse(self):
        ret = Topic(self.board, self.pid)
        items = self.soup.findAll('table', {'class': 'main'})
        if not items:
            raise ContentError()
        idx = 0 if not self.idx else self.idx
        for i in items:
            c = i.tr.td.a['href']
            p = Post(self.board, self.parse_pid(c), self.parse_num(c))
            c = i.findAll('tr')[1].td.textarea.text
            p.parse_post(c)
            p.idx = idx
            idx += 1
            ret.posts.append(p)
        for i in self.soup.body.center.findAll('a', recursive=False, limit=3):
            if i.text == u'本主题下30篇':
                ret.next_idx = int(self.parse_href(i['href'], 'start'))

        # remove topic head
        if self.idx:
            ret.idx = self.idx
            ret.prev_idx = self.idx - 30 or None
            ret.posts = ret.posts[1:]
        return ret
