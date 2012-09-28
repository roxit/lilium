from api.views.base import BaseView, SessionView


class LogInView(BaseView):

    POST_ACTION = 'login'

    def to_json(self, data):
        return data.dumps()


class LogOutView(SessionView):

    POST_ACTION = 'logout'


class CheckSessionView(SessionView):

    GET_ACTION = 'check_session'


class SubscriptionView(SessionView):

    GET_ACTION = 'fetch_subscription'
