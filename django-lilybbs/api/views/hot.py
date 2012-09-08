from api.views.base import BaseView


class HotView(BaseView):
    GET_ACTION = 'fetch_hot'

    def to_json(self, data):
        # data is changed inplace
        for i in data:
            for j, h in enumerate(i):
                i[j] = h.to_json()
        return data

