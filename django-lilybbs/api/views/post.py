from api.views.base import BaseView, SessionView


class PostView(SessionView):
    GET_ACTION = 'fetch_post'
    POST_ACTION = 'compose'

    def to_json(self, data):
        import pdb; pdb.set_trace()
        if self.request.method == 'POST':
            return data
        return data.to_json()

