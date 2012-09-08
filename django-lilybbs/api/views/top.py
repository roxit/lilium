from api.views.base import BaseView


class TopView(BaseView):
    GET_ACTION = 'fetch_top'

    def to_json(self, data):
        # data is changed inplace
        for i, h in enumerate(data):
            data[i] = h.to_json()
        return data

