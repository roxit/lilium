# -*- coding: utf-8 -*-
from datetime import datetime
import inspect
import logging
import os
import re
from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring

from lilybbs.exc import LilyError
from lilybbs.utils import len_zh

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(__file__)


class Post:
    AUTHOR_RE = re.compile(ur'发信人: (\w+?) \(')
    TITLE_RE = re.compile(ur'标  题: (.+?)$')
    DATE_RE = re.compile(ur'\((.+)\)$')
    DATE_FMT = u'%a %b %d %H:%M:%S %Y'
    IP_RE = re.compile(ur'\[FROM: (.+)\]')

    COLOR_RE = re.compile(ur'\x1b\[\d*(;\d+)?m')
    IMG_RE = re.compile(ur'(http://(www\.)?[\w./-]+?\.(jpe?g|gif|png))', re.IGNORECASE)
    #URL_RE = re.compile(ur'http://(www\.)?[\w./-]+?$')

    MAXC = 78

    def __init__(self, board=None, pid=None, num=None):
        self.board = board
        self.pid = pid
        self.num = num

        self.idx = 0

    def __str__(self):
        t = filter(lambda x: not x[0].startswith('__'), inspect.getmembers(self))
        return '\n'.join('{0}: {1}'.format(i[0], i[1]) for i in t)

    def to_json(self):
        return {
                'author': self.author,
                'board': self.board,
                'body': self.body,
                'date': self.date.isoformat(),
                'idx': self.idx,
                'ip': self.ip,
                'num': self.num,
                'pid': self.pid,
                'title': self.title,
        }

    def parse_meta(self, txt):
        try:
            self.author = self.AUTHOR_RE.search(txt[0]).group(1)
        except AttributeError:
            self.author = u''
        try:
            self.title = self.TITLE_RE.search(txt[1]).group(1)
        except AttributeError:
            self.title = u''
        try:
            date_str = self.DATE_RE.search(txt[2]).group(1)
            self.date = datetime.strptime(date_str, self.DATE_FMT)
        except AttributeError:
            self.date = datetime.max
        try:
            self.ip = self.IP_RE.search(txt[-1]).group(1)
        except Exception:
            # archived posts have no IP.
            self.ip = '0.0.0.0'

    def cleanup(self):
        while len(self.body) > 0:
            if self.body[-1] == u'--':
                self.body.pop()
                continue
            found = False
            for p in [u'※ 来源:', u'※ 修改:']:
                if self.body[-1].startswith(p):
                    self.body.pop()
                    found = True
                    self.body.pop()
                    break
            if not found:
                break

    def parse_body(self, txt):
        try:
            lines = txt[4:-2]
        except Exception:
            lines = [u'Houston, we have a problem.']

        self.body = []
        prev_len = 0
        for i in lines:
            i = i.rstrip()
            if not i:
                prev_len = 0
                continue
            if prev_len > self.MAXC - 2:
                self.body[-1] += i
            else:
                self.body.append(i)
            prev_len = len_zh(i)
        self.cleanup()
        self.body = '\r\n'.join(self.body)

    def parse_post(self, txt):
        # TODO: what's the following 3 lines for?
        i = txt.find(u'发信站')
        if txt[i - 1] != u'\n':
            txt = txt.replace(u'发信站', u'\n发信站', 1)
        txt = self.COLOR_RE.sub("", txt)
        txt = txt.splitlines()
        self.parse_meta(txt)
        self.parse_body(txt)


class Topic:
    def __init__(self, board=None, pid=None, idx=None):
        self.board = board
        self.pid = pid
        self.idx = idx
        self.posts = []
        self.next_idx = None
        self.prev_idx = None

    def __unicode__(self):
        return '[%s]%d' % (self.board, self.pid)

    def to_json(self):
        return {
                'board': self.board,
                'idx': self.idx,
                'nextIdx': self.next_idx,
                'pid': self.pid,
                'posts': [i.to_json() for i in self.posts],
                #'prevIdx': self.prev_idx,
        }


class Header:
    def __init__(self):
        self.author = None
        self.board = None
        self.date = None
        self.num = None
        self.pid = None
        self.reply_count = None
        self.title = None
        self.view_count = None

    def __unicode__(self):
        return self.title

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return '<Header: {0} >'.format(self)

    def to_json(self):
        return {
                'author': self.author,
                'board': self.board,
                'date': self.date.isoformat() if self.date else None,
                'num': self.num,
                'pid': self.pid,
                'replyCount': self.reply_count,
                'title': self.title,
                'viewCount': self.view_count,
        }


class Page:
    '''
    represents a list of headers in board view.
    '''
    def __init__(self, board):
        self.board = board
        self.prev_idx = None
        #self.next_idx = None
        self.headers = []

    def to_json(self):
        return {
                'board': self.board,
                'headers': [i.to_json() for i in self.headers],
                #'nextIdx': self.next_idx,
                'prevIdx': self.prev_idx,
        }


class Board:
    def __init__(self, name=None, text=None):
        self.name = name    # id
        self.text = text    # chinese name

    def __unicode__(self):
        return u'{0}'.format(self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return '<Board: %s>' % str(self)


class Section(list):
    def __init__(self, sid, text):
        super(Section, self).__init__()
        self.sid = sid
        self.text = text

    def __unicode__(self):
        return u'%s' % (self.text)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return '<Section: {0}>'.format(self)


class BoardManager(list):

    def __init__(self, filename='assets/BoardManager.xml'):
        super(BoardManager, self).__init__()
        self.boards = {}
        if not filename:
            return
        self.load_xml(filename)

    def load_xml(self, filename):
        doc = ElementTree()
        doc.parse(os.path.join(ROOT_DIR, 'assets/BoardManager.xml'))
        root = doc.getroot()
        for i in root.getchildren():
            sec = Section(i.attrib['sid'], i.attrib['text'])
            self.append(sec)
            for j in i.getchildren():
                brd = Board(j.attrib['name'], j.attrib['text'])
                sec.append(brd)
                self.boards[brd.name] = brd

    def dump_xml(self, filename='assets/BoardManager.xml'):
        root = Element('BoardManager')
        for s in self:
            sec = SubElement(root, 'Section',
                    attrib={'sid': str(s.sid), 'text': s.text})
            for b in s:
                SubElement(sec, 'Board',
                        attrib={'name': b.name, 'text': b.text})
        with open(os.path.join(ROOT_DIR, filename), 'w') as f:
            f.write(tostring(root, encoding='UTF-8'))

    def board_text(self, name):
        return self.boards[name].text


class Session:

    @classmethod
    def create(cls, session_str=None):
        ret = cls()
        if session_str:
            try:
                ret.loads(session_str)
            except (AttributeError, ValueError):
                raise LilyError('Invalid session string')
        return ret

    def __str__(self):
        return '<Session: vd=%s key=%s num=%s uid=%s>' % (self.vd, self.key, self.num, self.uid)

    def __repr__(self):
        return str(self)

    def __init__(self):
        self.vd = None
        self.key = None
        self.num = None
        self.uid = None
        self.username = None
        self.password = None

    def to_json(self):
        return {'vd': self.vd,
                'key': self.key,
                'num': self.num,
                'uid': self.uid,
        }

    def dumps(self):
        return ','.join([self.vd, self.key, self.num, self.uid])

    def loads(self, s):
        self.vd, self.key, self.num, self.uid = s.split(',')
