import json
import urllib

from django.http import HttpResponse
from django.views.generic import View

from lilybbs import Client
from lilybbs.exc import NotLoggedIn


class BaseView(View):

    GET_ACTION = None
    POST_ACTION = None

    def __init__(self, **kwargs):
        super(BaseView, self).__init__(**kwargs)
        self.client = Client()

    def to_json(self, data):
        '''
        Override this method if `ret` cannot be processed
        by `json.dumps` directly
        '''
        return data

    def get_json_response(self, ret=None, exc=None):
        JSON_MIME = 'application/json'
        if ret and exc:
            raise ValueError('Both ret and exc are set to non-None values')

        if exc:
            ERROR_STATUS_CODE = 400
            data = {'success': False,
                    'error': exc.__class__.__name__,
                    'message': str(exc)}
            return HttpResponse(json.dumps(data),
                    status=ERROR_STATUS_CODE,
                    mimetype=JSON_MIME)

        data = {'success': True,
                'data': self.to_json(ret)}
        return HttpResponse(json.dumps(data),
                mimetype=JSON_MIME)

    def get_params(self):
        ret = {}
        for k, v in self.request.GET.items():
            ret[k] = urllib.unquote(v)
        for k, v in self.request.POST.items():
            ret[k] = urllib.unquote(v)
        return ret

    def get(self, request, *args, **kwargs):
        #import pdb; pdb.set_trace()
        meth = getattr(self.client, self.GET_ACTION, None)
        if not meth:
            raise ValueError('GET_ACTION must be set')

        kwargs.update(self.get_params())
        try:
            ret = meth(*args, **kwargs)
            return self.get_json_response(ret, None)
        except Exception as exc:
            return self.get_json_response(None, exc)

    def post(self, request, *args, **kwargs):
        #import pdb; pdb.set_trace()
        meth = getattr(self.client, self.POST_ACTION, None)
        if not meth:
            raise ValueError('POST_ACTION must be set')

        # TODO: multi-valued
        kwargs.update(self.get_params())
        try:
            ret = meth(*args, **kwargs)
            return self.get_json_response(ret, None)
        except Exception as exc:
            return self.get_json_response(None, exc)


class SessionView(BaseView):
    '''

    '''

    GET_ACTION = None

    def get_session(self):
        #import pdb; pdb.set_trace()
        self.session = self.request.GET.get('session', None) \
                or self.request.POST.get('session', None)
        if not self.session:
            return self.get_json_response(None, NotLoggedIn())
        self.session = urllib.unquote(self.session)
        self.client.load_session(self.session)

    def get(self, request, *args, **kwargs):
        ret = self.get_session()
        if ret:
            return ret
        return super(SessionView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ret = self.get_session()
        if ret:
            return ret
        return super(SessionView, self).post(request, *args, **kwargs)

