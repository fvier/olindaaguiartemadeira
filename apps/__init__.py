import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from importlib import import_module
from sqlalchemy import text

db = SQLAlchemy()
migrate = Migrate(compare_type=True)
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=[])

def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

apps = ('pages',)

def register_blueprints(app):
    for module_name in apps:
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)

def configure_database(app):
    with app.app_context():
        if app.config.get('AUTO_CREATE_SCHEMA'):
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if app.config.get('REQUIRE_SECRET_KEY') and not app.config.get('SECRET_KEY'):
        raise RuntimeError('SECRET_KEY is required in production.')
    if app.config.get('REQUIRE_DATABASE_URL') and not ConfiguredDatabase.is_explicit(app.config):
        raise RuntimeError('DATABASE_URL is required in production.')
    if app.config.get('REQUIRE_POSTGRES') and not database_url.startswith('postgresql'):
        raise RuntimeError('PostgreSQL is required in production.')

    @app.route('/health')
    def health_check():
        try:
            db.session.execute(text('SELECT 1'))
            return {'status': 'ok', 'database': 'available'}, 200
        except Exception:
            return {'status': 'error', 'database': 'offline'}, 503

    register_extensions(app)
    register_blueprints(app)
    configure_database(app)

    @app.after_request
    def security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        if not app.debug:
            response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        return response
    return app


class ConfiguredDatabase:
    @staticmethod
    def is_explicit(config):
        return bool(os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL') or
                    (os.getenv('DB_ENGINE') and os.getenv('DB_NAME') and os.getenv('DB_USERNAME')))
