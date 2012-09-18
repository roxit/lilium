from urlparse import urlparse, parse_qs
from BeautifulSoup import BeautifulSoup


class BaseAction(object):

    def __init__(self, client, *args, **kwargs):
        self.client = client

    def setup(self):
        self.params = {}
        self.payload = {}

    def fetch(self):
        self.html = self.client.conn.send(
                self.ACTION,
                self.params,
                self.payload)
        self.html = self.html.replace(u'<nobr>', u'')
        self.soup = BeautifulSoup(self.html,
            convertEntities=BeautifulSoup.ALL_ENTITIES)

    def parse(self):
        raise NotImplementedError

    @classmethod
    def run(cls, client, *args, **kwargs):
        act = cls(client, *args, **kwargs)
        act.setup()
        act.fetch()
        return act.parse()

    @staticmethod
    def pid2str(pid):
        return u'M.{0}.A'.format(pid)

    @staticmethod
    def parse_href(s, k):
        return parse_qs(urlparse(s).query)[k][0]

    @staticmethod
    def parse_pid(s):
        return int(BaseAction.parse_href(s, 'file')[2:-2])

    @staticmethod
    def parse_num(s):
        return int(BaseAction.parse_href(s, 'num'))
