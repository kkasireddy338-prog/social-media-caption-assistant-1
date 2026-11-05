import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app
from werkzeug.middleware.proxy_fix import ProxyFix

# WSGI Middleware to restore original request URL when Vercel rewrites to /api/index
class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # Check all headers where Vercel might pass the original client path
        orig_uri = (
            environ.get('HTTP_X_MATCHED_PATH') or
            environ.get('HTTP_X_FORWARDED_URI') or
            environ.get('HTTP_X_ORIGINAL_URI') or
            environ.get('HTTP_X_REWRITE_URL') or
            environ.get('RAW_URI') or
            ''
        )
        if '?' in orig_uri:
            orig_uri = orig_uri.split('?', 1)[0]

        path_info = environ.get('PATH_INFO', '')

        # If a valid original client path was found and it's not the rewrite endpoint
        if orig_uri and orig_uri not in ('/api/index', '/api', '/api/index.py'):
            environ['PATH_INFO'] = orig_uri
        elif path_info in ('/api/index', '/api', '/api/index.py', ''):
            environ['PATH_INFO'] = '/'
        elif path_info.startswith('/api/index/'):
            environ['PATH_INFO'] = path_info[len('/api/index'):]
        elif path_info.startswith('/api/'):
            environ['PATH_INFO'] = path_info[len('/api'):]

        return self.wsgi_app(environ, start_response)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
