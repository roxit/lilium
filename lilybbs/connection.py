# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from cookielib import CookieJar
import urllib
import urllib2
from urllib2 import URLError

from lilybbs.exc import NetworkError


class Connection:

    ENCODING = 'gb18030'
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1'
    BBS_URL = 'http://bbs.nju.edu.cn'

    def __init__(self):
        self.cj = CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders = [('User-Agent', self.USER_AGENT)]
        #self.opener.addheaders = [('Referer', self.BBS_URL)]
        self.base_url = self.BBS_URL

    def load_session(self, session):
        self.base_url = '{0}/vd{1}'.format(self.BBS_URL, session.vd)
        self.cj.set_cookie(make_cookie('_U_KEY', session.key))
        self.cj.set_cookie(make_cookie('_U_UID', session.uid))
        self.cj.set_cookie(make_cookie('_U_NUM', session.num))

    def send(self, action, params=None, body=None):
        params = encode_params(params, self.ENCODING)
        url = '{0}/{1}{2}{3}'.format(
                self.base_url,
                action,
                '?' if params else '',      # no prefixing '/'
                params or '')       # str(None) == 'None'
        logger.debug(url)
        # body should be None instead of ''
        # otherwise fetch_emoticon may not work
        body = encode_params(body, self.ENCODING) or None

        try:
            resp = self.opener.open(url, body)
        except URLError:
            raise NetworkError()
        # decode() in py2.6 does not support `errors` kwarg.
        html = resp.read().decode(self.ENCODING, 'ignore')
        return html


def make_cookie(name, value, version=0,
        port=None, port_specified=False,
        domain=u'bbs.nju.edu.cn', domain_specified=False, domain_initial_dot=False,
        path=u'', path_specified=False,
        secure=False, expires=None, discard=True,
        comment=None, comment_url=None,
        rest={}, rfc2109=False):
    from cookielib import Cookie
    return Cookie(version, name, str(value),
            port, port_specified,
            domain, domain_specified, domain_initial_dot,
            path, path_specified,
            secure, expires, discard, comment, comment_url,
            rest, rfc2109)


def quote(x, encoding):
    x = x.encode(encoding) if isinstance(x, unicode) else str(x)
    return urllib.quote(x)


def encode_params(params, enc):
    ret = []
    for k, v in params.items():
        if isinstance(v, list):
            ret += ['{0}={1}'.format(quote(k, enc), quote(i, enc)) for i in v]
        else:
            ret.append('{0}={1}'.format(quote(k, enc), quote(v, enc)))
    return '&'.join(ret) if ret else ''

