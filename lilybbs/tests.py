# -*- coding=utf-8 -*-
import unittest

from lilybbs import Client
from lilybbs.models import *


class LogInOutTestCase(unittest.TestCase):

    def test(self):
        self.client = Client()
        ret = self.client.login('obash', 'changeme')
        self.assertIsInstance(ret, Session)
        self.assertTrue(self.client.check_session())

        ret = self.client.logout()
        self.assertTrue(ret)
        self.assertFalse(self.client.check_session())


class ReadOnlyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()

    def test_fetch_hot(self):
        ret = self.client.fetch_hot()
        self.assertIsInstance(ret, list)
        g = ret[1]
        self.assertIsInstance(g, list)
        self.assertTrue(len(g) > 0)

    def test_fetch_top(self):
        ret = self.client.fetch_top()
        self.assertIsInstance(ret, list)
        self.assertTrue(len(ret) == 10)

    def test_fetch_page(self):
        brd = 'D_Computer'
        ret = self.client.fetch_page(brd)
        self.assertIsInstance(ret, Page)
        self.assertIsNotNone(ret.prev_idx)
        self.assertEqual(ret.board, brd)
        self.assertTrue(len(ret.headers) > 0)
        h = ret.headers[0]
        self.assertIsNotNone(h.num)
        self.assertIsNotNone(h.board)
        self.assertIsNotNone(h.pid)
        self.assertIsNotNone(h.reply_count)
        ret = self.client.fetch_page(brd, ret.prev_idx)
        self.assertIsInstance(ret, Page)

    def test_fetch_post(self):
        brd = 'D_Computer'
        pid = 1346910579
        num = 10443
        ret = self.client.fetch_post(brd, pid, num)
        self.assertIsInstance(ret, Post)
        self.assertIsNotNone(ret.author)
        self.assertIsNotNone(ret.title)
        self.assertIsNotNone(ret.body)
        self.assertIsNotNone(ret.gid)
        self.assertIsNotNone(ret.num)

    def test_fetch_topic(self):
        brd = 'D_Computer'
        pid = '1340356876'
        ret = self.client.fetch_topic(brd, pid)
        self.assertIsInstance(ret, Topic)
        self.assertIsNotNone(ret.next_idx)
        self.assertTrue(len(ret.posts) == 31)
        p = ret.posts[-1]
        self.assertIsNotNone(p.board)
        self.assertIsNotNone(p.pid)
        self.assertIsNotNone(p.num)
        ret = self.client.fetch_topic(brd, pid, ret.next_idx)
        self.assertIsInstance(ret, Topic)


class SessionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.client.login('obash', 'changeme')

    @classmethod
    def tearDownClass(cls):
        cls.client.logout()

    def test_fetch_subscription(self):
        ret = self.client.fetch_subscription()
        self.assertIsInstance(ret, list)
        self.assertTrue(len(ret) > 0)

    def test_compose(self):
        brd = 'test'
        title = u'我们的目标是没有蛀牙！' * 3
        body = u'鼠辈，竟敢伤我！' * 7
        body += u'\r\nhttp://bbs.nju.edu.cn/file/R/rox/snow_heart.gif'
        import pdb; pdb.set_trace()
        ret = self.client.compose(brd, title, body)
        self.assertTrue(ret)

    def test_reply(self):
        # TODO
        return
        brd = 'test'
        ret = self.fetch_page(brd)
        pid = ret.headers[-1].pid
        ret = self.fetch_topic(brd, pid)


if __name__ == '__main__':
    unittest.main()

