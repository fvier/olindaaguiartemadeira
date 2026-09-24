import os
import re
import unittest

os.environ.setdefault('API_INTEGRATION_KEY', 'test-integration-key')

from apps import create_app, db
from apps.pages.models import User


class TestConfig:
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTO_CREATE_SCHEMA = True
    REQUIRE_DATABASE_URL = False
    REQUIRE_POSTGRES = False
    REQUIRE_SECRET_KEY = False
    WTF_CSRF_ENABLED = True
    RATELIMIT_ENABLED = False


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            user = User(username='manager', email='manager@example.com', role='gerente', active=True)
            user.set_password('a-secure-password')
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def csrf_token(self, path='/auth-signin.html'):
        response = self.client.get(path)
        match = re.search(rb'name="csrf-token" content="([^"]+)"', response.data)
        self.assertIsNotNone(match)
        return match.group(1).decode()

    def login(self):
        return self.client.post('/login', data={
            'email': 'manager@example.com', 'password': 'a-secure-password',
            'csrf_token': self.csrf_token(),
        })

    def test_csrf_rejects_unprotected_post(self):
        response = self.client.post('/login', data={'email': 'manager@example.com', 'password': 'a-secure-password'})
        self.assertEqual(response.status_code, 400)

    def test_external_next_url_is_rejected(self):
        token = self.csrf_token('/auth-signin.html?next=https://evil.example')
        response = self.client.post('/login?next=https://evil.example', data={
            'email': 'manager@example.com', 'password': 'a-secure-password', 'csrf_token': token,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/index')

    def test_integration_requires_api_key_even_with_session(self):
        self.login()
        response = self.client.get('/api/v1/integracoes/vendas')
        self.assertEqual(response.status_code, 401)

    def test_integration_accepts_configured_api_key(self):
        response = self.client.get('/api/v1/integracoes/vendas', headers={'X-API-Key': 'test-integration-key'})
        self.assertEqual(response.status_code, 200)

    def test_integration_persists_sale_in_database(self):
        response = self.client.post('/api/v1/integracoes/vendas', headers={'X-API-Key': 'test-integration-key'}, json={
            'client_name': 'Cliente Teste', 'contact': '999999999', 'monthly_fee': '79.90',
        })
        self.assertEqual(response.status_code, 201)
        listing = self.client.get('/api/v1/integracoes/vendas', headers={'X-API-Key': 'test-integration-key'})
        self.assertEqual(listing.json['total_retornado'], 1)
        self.assertEqual(listing.json['vendas'][0]['client_name'], 'Cliente Teste')

    def test_regular_user_cannot_manage_commercial_content(self):
        with self.app.app_context():
            user = User(username='regular', email='regular@example.com', role='usuario', active=True)
            user.set_password('a-secure-password')
            db.session.add(user)
            db.session.commit()
        token = self.csrf_token()
        self.client.post('/login', data={'email': 'regular@example.com', 'password': 'a-secure-password', 'csrf_token': token})
        token = self.csrf_token('/planos')
        response = self.client.post('/api/linktree', json={'links': []}, headers={'X-CSRFToken': token})
        self.assertEqual(response.status_code, 403)

    def test_healthcheck_reports_database(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['database'], 'available')


if __name__ == '__main__':
    unittest.main()
