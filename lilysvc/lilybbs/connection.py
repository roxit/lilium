# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from cookielib import CookieJar
from datetime import datetime
import re
import urllib2
from urllib2 import urlopen, URLError
from urllib import quote

from BeautifulSoup import BeautifulSoup

from error import Error, NetworkError, ContentError
from models import *
from utils import pid2str, parse_href, parse_num, parse_pid

class Connection:

    ENCODING = 'gb18030'
    USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:9.0.1) Gecko/20100101 Firefox/9.0.1'
    BBS_URL = 'http://bbs.nju.edu.cn/'
    DATE_FORMAT = '%b %d %H:%M'
    base_url = 'http://bbs.nju.edu.cn/'

    def __init__(self, session=None):
        self._cj = CookieJar()
        self._opener = urllib2.build_opener(
                urllib2.HTTPCookieProcessor(self._cj))
        self._opener.addheaders = [('User-Agent', self.USER_AGENT)]
        self._opener.addheaders = [('Referer', self.BBS_URL)]
        if session:
            self.load_session(session)

    def _do_action(self, action, params=None, data=None):
        args = []
        if params:
            for k, v in params.items():
                if isinstance(v, list):
                    args += ['{0}={1}'.format(k, i) for i in v]
                else:
                    args.append('{0}={1}'.format(k, v))
        url = self.base_url+action+('?' if args else '')+'&'.join(args)
        logger.debug(url)
        body = []
        if data:
            for k, v in data.items():
                body.append('{0}={1}'.format(quote(k.encode(self.ENCODING)), quote(str(v).encode(self.ENCODING))))
        try:
            response = self._opener.open(url, '&'.join(body) if data else None)
        except URLError as e:
            raise NetworkError()
        # decode() in py2.6 does not support `errors` kwarg.
        html = response.read().decode(self.ENCODING, 'ignore')
        # TODO: BeautifulSoup still needs this?
        html = html.replace(u'<nobr>', u'')     # damn it
        return html

    def load_session(self, session):
        from utils import make_cookie
        self.base_url = '{0}vd{1}/'.format(self.BBS_URL, session.vd)
        self._cj.set_cookie(make_cookie('_U_KEY', session.key))
        self._cj.set_cookie(make_cookie('_U_UID', session.uid))
        self._cj.set_cookie(make_cookie('_U_NUM', session.num))

    def is_logged_in(self):
        html = self._do_action('bbsfoot')
        return html.find('bbsqry?userid=guest') == -1
        
    def login(self, username, password):
        '''
        return Session if successful else None
        '''
        # TODO: logout existing session

        from random import randint
        session = Session()
        session.vd = str(randint(10000, 100000))
        self.base_url = '{0}vd{1}/'.format(self.BBS_URL, session.vd)

        params = {'type': 2}
        data = {u'id': username, u'pw': password}
        html = self._do_action('bbslogin', params, data)

        try:
            s = re.search(r"setCookie\('(.*)'\)", html).group(1)
        except AttributeError:
            return None

        s = s.split('+')
        session.key = str(int(s[-1])-2)
        s = s[0].split('N')
        session.uid = s[-1]
        session.num = str(int(s[0])+2)
        self.load_session(session)
        return session

    def logout(self, session=None):
        if session:
            self.load_session(session)
        data = {'Submit': u'注销登录'.encode(self.ENCODING)}
        ret = self._do_action('bbslogout', '', data)
        self._cj.clear()
        self.base_url = self.BBS_URL

    def send_topic(self, board, title, text, pid=None, gid=None, signature=0, autocr='on'):
        params = {'board': board}
        data = {'title': title,
                'text': text,
                'autocr': autocr,
                'signature': signature}
        if pid:
            data['reid'] = pid
            data['pid'] = gid
        html = self._do_action('bbssnd', params, data)
        if 'Refresh' in html:
            return True
        else:
            return False

    def fetch_post(self, pid, board, num):
        params = {'board': board,
                  'file': pid2str(pid),
                  'num': num}
        html = self._do_action('bbscon', params)
        soup = BeautifulSoup(html)
        txt = soup.find('textarea').text
        ret = Post(pid, board, num)
        ret.parse_post(txt)
        # TODO: works for 'x' post
        ret.gid = soup.findAll('a')[-1]['href']
        ret.gid = ret.gid[ret.gid.rfind('=')+1:]
        return ret

    def fetch_topic(self, board, pid, start=None):
        params = {'board': board, 'file': pid2str(pid)}
        if start:
            params['start'] = start
        html = self._do_action('bbstcon', params)
        soup = BeautifulSoup(html)
        ret = Topic(board, pid)
        items = soup.findAll('table', {'class': 'main'})
        if not items:
            raise ContentError()
        for i in items:
            c = i.tr.td.a['href']
            p = Post(board, parse_pid(c), parse_num(c))
            c = i.findAll('tr')[1].td.textarea.text
            p.parse_post(c)
            ret.post_list.append(p)
        for i in soup.body.center.findAll('a', recursive=False, limit=3):
            if i.text == u'本主题下30篇':
                ret.next_start = int(parse_href(i['href'], 'start'))
        return ret
    
    def fetch_page(self, board, start=None):
        params = {'board': board}
        if start:
            params['start'] = start
        html = self._do_action('bbstdoc', params)
        soup = BeautifulSoup(html)

        items = soup.findAll('tr')[1:]
        year = datetime.now().year
        ret = Page(board)
        for i in items:
            cells = i.findAll('td')
            h = Header()
            h.board = board
            try:
                h.num = int(cells[0].text)-1
            except ValueError:
                continue
            h.author = cells[2].text.strip()
            h.date = cells[3].text.strip()
            h.date = datetime.strptime(h.date, self.DATE_FORMAT)
            h.date = h.date.replace(year = year)
            h.title = cells[4].text.strip()[2:]
            h.pid = parse_pid(cells[4].a['href'])
            tmp = cells[5].text.strip()
            if tmp.find('/') != -1:
                tmp = tmp.split('/')
                h.reply_count = int(tmp[0])
                h.view_count = int(tmp[1])
            else:
                h.view_count = int(tmp)
            ret.header_list.append(h)
        # TODO
        for i in soup.body.center.findAll('a', recursive=False):
            if i.text == u'上一页':
                ret.prev_start = int(parse_href(i['href'], 'start'))-1
        return ret

    def fetch_top10(self):
        html = self._do_action('bbstop10')
        soup = BeautifulSoup(html)
        items = soup.findAll('tr')[1:]
        ret = Page('全站十大')
        for i in items:
            cells = i.findAll('td')
            h = Header()
            h.board = cells[1].text.strip()
            h.title = cells[2].text.strip()
            h.pid = parse_pid(cells[2].a['href'])
            h.author = cells[3].text.strip()
            h.reply_count = int(cells[4].text.strip())
            ret.header_list.append(h)
        return ret

    def fetch_hot(self):
        html = self._do_action('bbstopall')
        soup = BeautifulSoup(html)
        items = soup.findAll('tr')
        ret = []
        tmp = None
        for i in items:
            if i.img:
                tmp = []
                continue
            cells = i.findAll('td')
            if not cells[0].text:
                ret.append(tmp)
                continue
            for j in cells:
                h = Header()
                links = j.findAll('a')
                h.title = links[0].text.strip()
                h.board = links[1].text.strip()
                h.pid = parse_pid(links[0]['href'])
                tmp.append(h)
        return ret

    def fetch_favorites(self):
        html = self._do_action('bbsleft')
        soup = BeautifulSoup(html)
        div = soup.findAll('div', {'id': 'div0'})
        if not div:
            raise Error()
        items = div[0]
        items = items.findAll('a')[:-1]
        ret = [i.text for i in items]
        return ret

    def fetch_board_list(self):
        from time import sleep
        ret = BoardManager()
        for i in range(12):
            sleep(1)
            html = self._do_action('bbsboa', {'sec': i})
            soup = BeautifulSoup(html)
            try:
                text = re.search(ur'\[(\w+?)区\]<hr', html, re.UNICODE).group(1)
            except AttributeError as e:
                raise ContentError('请勿过快刷新页面')
            section = Section(i, text)
            items = soup.findAll('tr')[1:]
            for i in items:
                cells = i.findAll('td')
                s = cells[5].text[2:]
                # Some board may have a voting in progress
                if s.endswith(u'V'):
                    s = s[:-1]
                board = Board(cells[2].text, s)
                section.board_list.append(board)
            ret.add(section)
        return ret

    def fetch_face_list(self):
        html = self._do_action('editor/face.htm', {'ptext': 'text'})
        soup = BeautifulSoup(html)
        items = soup.findAll('img')
        ret = {}
        for i in items:
            ret[i['title']] = i['src']
        with open('FaceList.json', 'w') as f:
            json.dump(ret, f)

if __name__ == '__main__':
    lily = Connection()
#    lily.login(u'obash', u'changeme')
#    lily.send_topic(u'test', u'信春哥&', u'无&bug')
#    lily.fetch_post(1323838963, 'YanCheng', 7644)
#    lily.fetch_topic(1322808044, 'Python')
#    lily.fetch_topic(1326809504, 'YanCheng')
#    lily.fetch_page('D_Computer')
#    lily.fetch_top10()
#    lily.fetch_board_list()
    lily.fetch_face_list()
    #lily.logout()
#    print(lily.connection.is_logged_in())
        
