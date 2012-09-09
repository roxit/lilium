# -*- coding=utf-8 -*-
import json
import urllib

from django.test import TestCase
from django.test.client import Client


class ReadOnlyTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()

    def test_fetch_hot(self):
        url = '/api/hot/'
        resp = self.client.get(url)
        ret = json.loads(resp.content)['data']
        self.assertIsInstance(ret, list)

    def test_fetch_top(self):
        url = '/api/top/'
        resp = self.client.get(url)
        ret = json.loads(resp.content)['data']
        self.assertIsInstance(ret, list)

    def test_fetch_post(self):
        brd = 'D_Computer'
        pid = '1346910579'
        num = 10443
        url = '/api/post/{}/{}/?num={}'.format(brd, pid, num)
        resp = self.client.get(url)
        ret = json.loads(resp.content)['data']
        self.assertIsNotNone(ret['title'])

    def test_fetch_page(self):
        brd = 'D_Computer'
        url = '/api/board/{}/'.format(brd)
        resp = self.client.get(url)
        ret = json.loads(resp.content)['data']
        self.assertIsInstance(ret['headers'], list)
        url += '{}/'.format(ret['prevIdx'])
        ret = json.loads(resp.content)['data']
        self.assertIsInstance(ret['headers'], list)

    def test_fetch_topic(self):
        brd = 'D_Computer'
        pid = '1340356876'
        url = '/api/topic/{}/{}/'.format(brd, pid)
        resp = self.client.get(url)
        ret = json.loads(resp.content)['data']
        self.assertIsInstance(ret['posts'], list)
        url += '{}/'.format(ret['nextIdx'])
        resp = self.client.get(url)
        ret = json.loads(resp.content)['data']
        self.assertIsInstance(ret['posts'], list)


class SessionTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        resp = cls.client.post('/api/login/',
                {'username': 'obash', 'password': 'changeme'})
        cls.session = urllib.quote(json.loads(resp.content)['data'])

    @classmethod
    def tearDownClass(cls):
        cls.client.post('/api/logout/',
                {'session': cls.session})

    def test_fetch_subscription(self):
        url = '/api/subscription/?session={}'.format(self.session)
        resp = self.client.get(url)
        ret = json.loads(resp.content)
        self.assertIsInstance(ret['data'], list)
        self.assertTrue(len(ret['data']) > 0)

    def test_compose(self):
        brd = 'test'
        title = u'我们的目标是没有蛀牙！' * 3
        body = u'鼠辈，竟敢伤我！' * 7
        body += u'\r\nhttp://bbs.nju.edu.cn/file/R/rox/snow_heart.gif'
        url = '/api/post/{}/'.format(brd)
        ret = self.client.post(url, {
                'title': title,
                'body': body,
                'session': self.session})
        self.assertTrue(ret)

