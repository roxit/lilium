from lilybbs.action.base import BaseAction


class FetchEmoticonAction(BaseAction):
    ACTION = 'editor/face.htm'

    def setup(self):
        self.params = {'ptext': 'text'}
        self.payload = {}

    def parse(self):
        items = self.soup.findAll('img')
        ret = {}
        for i in items:
            ret[i['title']] = i['src']
        return ret

