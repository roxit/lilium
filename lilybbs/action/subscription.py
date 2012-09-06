from lilybbs.action.base import BaseAction
from lilybbs.exc import NotLoggedIn


class FetchSubscriptionAction(BaseAction):
    ACTION = 'bbsleft'

    def parse(self):
        div = self.soup.findAll('div', {'id': 'div0'})
        if not div:
            raise NotLoggedIn()
        items = div[0]
        items = items.findAll('a')[:-1]
        ret = [i.text for i in items]
        return ret

