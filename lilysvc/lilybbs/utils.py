# -*- coding: utf-8 -*-
import re
from urlparse import urlparse, parse_qs

class LilyError(Exception): pass

def pid2str(pid):
    return u'M.{0}.A'.format(pid)
    
def parse_href(s, k):
    return parse_qs(urlparse(s).query)[k][0]

def parse_pid(s):
    return int(parse_href(s, 'file')[2:-2])
    
def parse_num(s):
    return int(parse_href(s, 'num'))

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
