#!/bin/bash

if [ -z "$VIRTUAL_ENV" ]; then
    echo 'Please activate your virtualenv first!'
    exit -1
fi

python setup.py sdist
pip install -U --no-deps dist/lily*.tar.gz
rm -rf lilybbs.egg-info
../sae/saepythondevguide/dev_server/bundle_local.py -r requirements.txt
rm django-lilybbs/venv.bundle.zip
cd virtualenv.bundle
zip -r ../django-lilybbs/venv.bundle.zip .
cd ..
rm -rf virtualenv.bundle
cd django-lilybbs

if [ "$1" = "sae" ]; then
    saecloud deploy
fi
