from api.views.base import BaseView, SessionView


class LogInView(BaseView):

    POST_ACTION = 'login'

    def to_json(self, data):
        return data.dumps()


class LogOutView(SessionView):

    POST_ACTION = 'logout'


class IsLoggedInView(SessionView):
    GET_ACTION = 'is_logged_in'


class SubscriptionView(SessionView):
    GET_ACTION = 'fetch_subscription'

