# -*- coding=utf-8 -*-
from lilybbs.action.base import BaseAction


class LogOutAction(BaseAction):
    ACTION = 'bbslogout'

    def setup(self):
        self.params = {}
        self.body = {'Submit': u'注销登录'}

    def parse(self):
        self.client.conn.cj.clear()

