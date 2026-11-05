import os
from flask import Flask, render_template, session
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from database.db import init_db
from routes.auth import auth_bp
from routes.captions import captions_bp
from routes.dashboard import dashboard_bp

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static'),
        static_url_path='/static'
    )
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(captions_bp)
    app.register_blueprint(dashboard_bp)

    # Landing page route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Initialize database on startup safely
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            print(f"[Warning] DB initialization failed: {e}")

    # Context processor to inject user info into all templates
    @app.context_processor
    def inject_user():
        if 'user_id' in session:
            return {
                'current_user': {
                    'id': session.get('user_id'),
                    'username': session.get('username'),
                    'email': session.get('email')
                }
            }
        return {'current_user': None}

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
