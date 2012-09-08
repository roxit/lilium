from api.views.base import BaseView


class PageView(BaseView):
    GET_ACTION = 'fetch_page'

    def to_json(self, data):
        return data.to_json()

