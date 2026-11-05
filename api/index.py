import sys
import os

# Add root directory to sys.path so app and its packages can be imported
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

# WSGI Middleware to restore original request URL when Vercel rewrites to /api/index
class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # Vercel puts the original requested path in HTTP_X_MATCHED_PATH or HTTP_X_NOW_ROUTE
        matched_path = environ.get('HTTP_X_MATCHED_PATH', '')
        path_info = environ.get('PATH_INFO', '')

        # 1. If Vercel passed the original path in X-Matched-Path header
        if matched_path and matched_path not in ('/api/index', '/api', '/api/index.py'):
            environ['PATH_INFO'] = matched_path
        # 2. If PATH_INFO is literally the rewrite target (/api/index or /api)
        elif path_info in ('/api/index', '/api', '/api/index.py', ''):
            environ['PATH_INFO'] = '/'
        # 3. If PATH_INFO is prefixed by /api/index/ (e.g. /api/index/login)
        elif path_info.startswith('/api/index/'):
            environ['PATH_INFO'] = path_info[len('/api/index'):]
        # 4. If PATH_INFO is prefixed by /api/ (e.g. /api/login)
        elif path_info.startswith('/api/'):
            environ['PATH_INFO'] = path_info[len('/api'):]

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
