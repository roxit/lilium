# -*- coding=utf-8 -*-
from random import randint
import re

from lilybbs.action.base import BaseAction
from lilybbs.exc import InvalidLogin, NotLoggedIn
from lilybbs.models import Session


class LogInAction(BaseAction):
    ACTION = 'bbslogin'

    def __init__(self, client, username, password):
        super(LogInAction, self).__init__(client)
        self.username = username
        self.password = password

    def setup(self):
        self.session = Session.create()
        self.session.username = self.username
        self.session.password = self.password
        self.session.vd = str(randint(10000, 100000))
        self.client.conn.base_url = '{0}/vd{1}'.format(
                self.client.conn.BBS_URL, self.session.vd)

        self.params = {'type': 2}
        self.body = {'id': self.username,
                'pw': self.password}

    def parse(self):
        try:
            s = re.search(r"setCookie\('(.*)'\)", self.html).group(1)
        except AttributeError:
            raise InvalidLogin()
        s = s.split('+')
        self.session.key = str(int(s[-1]) - 2)
        s = s[0].split('N')
        self.session.uid = s[-1]
        self.session.num = str(int(s[0]) + 2)
        self.client.load_session(self.session)
        return self.session


class LogOutAction(BaseAction):
    ACTION = 'bbslogout'

    def setup(self):
        self.params = {}
        self.body = {'Submit': u'注销登录'}

    def parse(self):
        self.client.conn.cj.clear()
        return u'错误! 你没有登录! ' not in self.html


class CheckSessionAction(BaseAction):
    ACTION = 'bbsfoot'

    def parse(self):
        return 'bbsqry?userid=guest' not in self.html


class FetchSubscriptionAction(BaseAction):
    ACTION = 'bbsleft'

    def parse(self):
        div = self.soup.findAll('div', {'id': 'div0'})
        if not div:
            raise NotLoggedIn()
        items = div[0]
        items = items.findAll('a')[:-1]
        ret = [i.text for i in items]
        return ret

