import os
import sys

APP_ROOT = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(APP_ROOT, 'virtualenv.bundle.zip'))

import django.core.handlers.wsgi

import sae

os.environ['DJANGO_SETTINGS_MODULE'] = 'lilysvc.settings'

application = sae.create_wsgi_app(django.core.handlers.wsgi.WSGIHandler())