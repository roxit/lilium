# -*- coding: utf-8 -*-
from datetime import datetime
import inspect
import json
import logging
import os
import re
from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring

logger = logging.getLogger(__name__)

DIR = os.path.dirname(__file__)

class Post:
    AUTHOR_RE = re.compile(ur'发信人: (\w+?) \(')
    TITLE_RE = re.compile(ur'标  题: (.+?)$')
    TIME_RE = re.compile(ur'\((.+)\)$')
    TIME_FMT = u'%a %b %d %H:%M:%S %Y'
    IP_RE = re.compile(ur'\[FROM: (.+)\]')
    COLOR_RE = re.compile(ur'\x1b\[\d*(;\d+)?m')
    IMG_RE = re.compile(ur'(http://(www\.)?[\w./-]+?\.(jpe?g|gif|png))')
    FACE_LIST = None

    def __init__(self, board=None, pid=None, num=None):
        self.board = board
        self.pid = pid
        self.num = num
        self._str = None
        if not self.FACE_LIST:
            with open(os.path.join(DIR, 'resources/face_list.json')) as f:
                self.FACE_LIST = json.load(f)
        self.body = None

    def __str__(self):
        t = filter(lambda x: not x[0].startswith('__'), inspect.getmembers(self))
        return '\n'.join('{0}: {1}'.format(i[0], i[1]) for i in t)

    def json(self):
        return {
                'author': self.author,
                'board': self.board,
                'body': self.body,
                'ip': self.ip,
                'num': self.num,
                'time': self.time.isoformat(),
                'title': self.title,
        }

    def parse_post(self, txt):
        # damn it
        i = txt.find(u'发信站')
        if txt[i-1] != u'\n':
            txt = txt.replace(u'发信站', u'\n发信站', 1)

        txt = txt.splitlines()
        self.author = self.AUTHOR_RE.search(txt[0]).group(1)
        self.title = self.TITLE_RE.search(txt[1]).group(1)
        time_str = self.TIME_RE.search(txt[2]).group(1)
        self.time = datetime.strptime(time_str, self.TIME_FMT)
        self.ip = self.IP_RE.search(txt[-1]).group(1)
        self._body = txt[4:-2]
        self.render()
    
    # TODO:
    def render(self):
        if self.body is not None:
            return
        p = re.compile(ur'[-]+')
        body = self._body[:]
        for i in range(len(body)):
            if not body[i].strip():
                body[i] = u'<br/>'
        self.body = u''.join(i.rstrip() for i in body)
        self.body = self.COLOR_RE.sub("", self.body)
        self.body = self.IMG_RE.sub(ur'<br><img src="/fetch?url=\1" alt="\1" /><br>', self.body)

        for i in self.FACE_LIST:
            self.body = self.body.replace(i,
                u'<img src="http://bbs.nju.edu.cn%s" alt="%s" />' % (self.FACE_LIST[i], i))
    '''
    # TODO:
    @property
    def body(self):
        #if self._str is None:
        self.render()
        return self._str
    '''

class Topic:
    def __init__(self, board=None, pid=None):
        self.board = board
        self.pid = pid
        self.next_start = None
        self.post_list = []
    
    def __unicode__(self):
        # t = filter(lambda x: not x[0].startswith('__'), inspect.getmembers(self))
        # return '\n'.join('{0}: {1}'.format(i[0], i[1]) for i in t)
        return '[%s]%d' % (self.board, self.pid)

    def json(self):
        return {
                'board': self.board,
                'pid': self.pid,
                'postList': [i.json() for i in self.post_list],
                'nextStart': self.next_start,
        }

class Header:
    def __init__(self):
        self.author = None
        self.board = None
        self.num = None
        self.pid = None
        self.reply_count = None
        self.title = None
        self.view_count = None
        
    def json(self):
        return {
                'author': self.author,
                'board': self.board,
                'num': self.num,
                'pid': self.pid,
                'replyCount': self.reply_count,
                'title': self.title,
                'viewCount': self.view_count,
        }

class Page:
    def __init__(self, board):
        self.board = board
        self.prev_start = None
        self.header_list = []

    def json(self):
        return {
                'board': self.board,
                'headerList': [i.json() for i in self.header_list],
                'prevStart': self.prev_start,
        }
    
class Session:

    @classmethod
    def create(cls, session_str=None):
        ret = cls()
        try:
            ret.loads(session_str)
        except (AttributeError, ValueError):
            logger.warning('Invalid session_str')
            return None
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

    def dumps(self):
        return '|'.join([self.vd, self.key, self.num, self.uid])

    def loads(self, s):
        self.vd, self.key, self.num, self.uid = s.split('|')

class Board:
    def __init__(self, name=None, text=None):
        self.name = name    # id
        self.text = text    # chinese name

    def __unicode__(self):
        return u'%s(%s)' % (self.text, self.name)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return '<Board: %s>' % str(self)

class Section:
    def __init__(self, sid, text):
        self.sid = sid
        self.text = text
        self.board_list = []

    def __getitem__(self, idx):
        return self.board_list[idx]

    def __unicode__(self):
        return u'%s' % (self.text)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return '<Section: %s>' % str(self)
        
class BoardManager:

    _section_list = []
    _boards = {}

    def add(self, section):
        self._section_list.append(section)

    @property
    def section_list(self):
        if not self._section_list:
            self._section_list = []
            self._boards = {}
            doc = ElementTree()
            doc.parse(os.path.join(DIR, 'resources/BoardManager.xml'))
            root = doc.getroot()
            for i in root.getchildren():
                sec = Section(i.attrib['sid'], i.attrib['text'])
                self._section_list.append(sec)
                for j in i.getchildren():
                    brd = Board(j.attrib['name'], j.attrib['text'])
                    sec.board_list.append(brd)
                    self._boards[brd.name] = brd
        return self._section_list

    @property
    def boards(self):
        self.section_list
        return self._boards

    def __getitem__(self, idx):
        return self.section_list[idx]

    def section_text(self, sid):
        return self.section_list[sid].text

    def board_text(self, name):
        self.section_list
        return self.boards[name].text
    
    class Encoder(json.JSONEncoder):
        def default(self, o):
            if not isinstance(o, BoardManager):
                raise TypeError("%r is not JSON serializable" % o)
            # json still dumps the 'repr' of strings
            return [{'sid': i.sid,
                     'text': i.text,
                     'board_list': [[j.name, j.text] for j in i.board_list]
                     } for i in o.section_list]
    
    class Decoder(json.JSONDecoder):
        def decode(self, json_str):
            o = json.loads(json_str)
            ret = BoardManager()
            for i in o:
                section = Section(i['sid'], i['text'])
                for j in i['board_list']:
                    section.board_list.append(j)
                ret.add(section)
            return ret

    def dump(self, filename):
        with open(filename, 'w') as f:
            json.dump(self, f, encoding='utf-8', cls=self.Encoder)

    def load(self, filename):
        with open(filename) as f:
            json.load(f, encoding='utf-8', cls=self.Decoder)

    def toxml(self, filename):
        root = Element('BoardManager')
        for i in self.section_list:
            sec = SubElement(root, 'Section', attrib={'sid': str(i.sid), 'text': i.text})
            for j in i.board_list:
                brd = SubElement(sec, 'Board', attrib={'name': j.name, 'text': j.text})
        with open(filename, 'w') as f:
            f.write(tostring(root, encoding='UTF-8'))
