import sys
import os
import urllib.parse

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
        query = environ.get('QUERY_STRING', '')
        path_info = environ.get('PATH_INFO', '')

        # 1. If Vercel passed the path via query parameter __vercel_path
        if '__vercel_path' in query:
            parsed = urllib.parse.parse_qs(query, keep_blank_values=True)
            if '__vercel_path' in parsed:
                raw_path = parsed['__vercel_path'][0] if parsed['__vercel_path'] else ''
                del parsed['__vercel_path']
                environ['QUERY_STRING'] = urllib.parse.urlencode(parsed, doseq=True)

                if not raw_path or raw_path == '/':
                    target = '/'
                else:
                    target = raw_path if raw_path.startswith('/') else '/' + raw_path

                environ['PATH_INFO'] = target

        # 2. Check headers where Vercel might pass the original client path
        elif environ.get('HTTP_X_MATCHED_PATH') and environ.get('HTTP_X_MATCHED_PATH') not in ('/api/index', '/api', '/api/index.py'):
            environ['PATH_INFO'] = environ['HTTP_X_MATCHED_PATH']
        elif environ.get('HTTP_X_FORWARDED_URI') and environ.get('HTTP_X_FORWARDED_URI') not in ('/api/index', '/api', '/api/index.py'):
            environ['PATH_INFO'] = environ['HTTP_X_FORWARDED_URI'].split('?')[0]

        # 3. Fallback for bare /api/index
        elif path_info in ('/api/index', '/api', '/api/index.py', ''):
            environ['PATH_INFO'] = '/'
        elif path_info.startswith('/api/index/'):
            environ['PATH_INFO'] = path_info[len('/api/index'):]
        elif path_info.startswith('/api/'):
            environ['PATH_INFO'] = path_info[len('/api'):]

        return self.wsgi_app(environ, start_response)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
