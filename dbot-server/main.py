#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
It's main module for docker to start the dbot server.
Auto load private key from current directory
"""
from gevent import monkey
monkey.patch_all()
import os
import json
import logging
import logging.config

from app import create_app
from utils import get_private_key


logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.conf'))

app_environ = os.environ.get('APP_ENV', 'Production')
app = create_app(app_environ)
if app.config['DEBUG']:
    logging.getLogger('dbot').setLevel(logging.DEBUG)
else:
    logging.getLogger('dbot').setLevel(logging.INFO)

pk_file = './keystore/keyfile'
pw_file = './password/passwd'
private_key = get_private_key(pk_file, pw_file)

# import dbot module after logging config
import dbot
dbot_server = dbot.get_server()
logging.info('Start dbot server ...')
http_provider = os.environ.get('WEB3_PROVIDER', app.config['WEB3_PROVIDER_DEFAULT'])
dbot_server.init(app, private_key, http_provider)
logging.info('waiting for all dbot service sync info with block chain')

host = app.config['HOST']
port = os.environ.get('LISTEN_PORT', app.config['PORT'])
# save dbot backend info for dbot-service tool to operate dbot-service
with open(os.path.join(os.path.dirname(__file__), '.backend'), 'w') as fh:
    json.dump({
        'backend': 'http://{}:{}'.format(host, port),
        'pk_file': os.path.abspath(pk_file),
        'pw_file': os.path.abspath(pw_file),
        'http_provider': http_provider
    }, fh, indent=2)

if __name__ == "__main__":
    app.run(host=host, port=port, debug=app.config['DEBUG'], use_reloader=False)