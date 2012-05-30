import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT_DIR, 'virtualenv.bundle.zip'))

import sae
from lilysvc import wsgi

application = sae.create_wsgi_app(wsgi.application)

