import os
import sys

ROOT_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(ROOT_DIR, 'venv.bundle.zip'))

import sae
from lilysvc import wsgi

application = sae.create_wsgi_app(wsgi.application)

