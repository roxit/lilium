from .base import BaseAction
from ..models import Header


class FetchHotAction(BaseAction):
    ACTION = 'bbstopall'

    def parse(self):
        items = self.soup.findAll('tr')
        ret = []
        grp = None
        for i in items:
            if i.img:
                grp = []
                continue
            cells = i.findAll('td')
            if not cells[0].text:
                ret.append(grp)
                continue
            for j in cells:
                h = Header()
                links = j.findAll('a')
                h.title = links[0].text.strip()
                h.board = links[1].text.strip()
                h.pid = self.parse_pid(links[0]['href'])
                grp.append(h)
        return ret
