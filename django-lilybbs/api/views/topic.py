from api.views.base import BaseView


class TopicView(BaseView):
    GET_ACTION = 'fetch_topic'

    def to_json(self, data):
        return data.to_json()
