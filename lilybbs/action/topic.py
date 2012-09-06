# -*- coding=utf-8 -*-
from lilybbs.action.base import BaseAction
from lilybbs.models import Topic, Post
from lilybbs.exc import ContentError


class FetchTopicAction(BaseAction):
    ACTION = 'bbstcon'

    def __init__(self, client, board, pid, idx=None):
        super(FetchTopicAction, self).__init__(client)
        self.board = board
        self.pid = pid
        self.idx = idx

    def setup(self):
        self.params = {'board': self.board, 'file': self.pid2str(self.pid)}
        if self.idx:
            self.params['start'] = self.idx
        self.body = {}

    def parse(self):
        ret = Topic(self.board, self.pid)
        items = self.soup.findAll('table', {'class': 'main'})
        if not items:
            raise ContentError
        for i in items:
            c = i.tr.td.a['href']
            p = Post(self.board, self.parse_pid(c), self.parse_num(c))
            c = i.findAll('tr')[1].td.textarea.text
            p.parse_post(c)
            ret.posts.append(p)
        for i in self.soup.body.center.findAll('a', recursive=False, limit=3):
            if i.text == u'本主题下30篇':
                ret.next_start = int(self.parse_href(i['href'], 'start'))

        # remove topic head
        if self.idx:
            ret.posts = ret.posts[1:]
        return ret

