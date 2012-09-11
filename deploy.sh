#!/bin/bash

python setup.py sdist
pip install dist/lily*.tar.gz
rm -rf lilybbs.egg-info
../sae/saepythondevguide/dev_server/bundle_local.py -r requirements.txt
cd virtualenv.bundle
zip -r ../django-lilybbs/venv.bundle.zip .
cd ..
rm -rf virtualenv.bundle
cd django-lilybbs
saecloud deploy
