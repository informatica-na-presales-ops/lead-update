from flask import request
from lead_update.lead import app
from notch import make_log
from os import getenv
from signal import signal, SIGTERM
from sys import exit
from waitress import serve
from werkzeug.middleware.proxy_fix import ProxyFix

log = make_log('lead-update-launcher')

def handle_sigterm(_signal, _frame):
    exit()

signal(SIGTERM, handle_sigterm)

app.wsgi_app = ProxyFix(app.wsgi_app, x_port=1)
app.config['PREFERRED_URL_SCHEME'] = getenv('PREFERRED_URL_SCHEME', 'https')
app.config['SERVER_NAME'] = getenv('SERVER_NAME')


@app.before_request
def log_request():
    app.logger.info(f'{request.method} {request.path}')


web_server_threads = int(getenv('WEB_SERVER_THREADS', 4))
serve(app, ident=None, threads=web_server_threads)
