from api.views.base import BaseView, SessionView


class PostView(SessionView):
    GET_ACTION = 'fetch_post'
    POST_ACTION = 'compose'

    def to_json(self, data):
        if self.request.method == 'POST':
            return data
        return data.to_json()

    def get(self, request, *args, **kwargs):
        return BaseView.get(self, request, *args, **kwargs)

