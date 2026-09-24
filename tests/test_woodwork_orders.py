import os
import unittest

from apps import create_app, db
from apps.pages.models import WoodworkOrder
from apps.pages.routes import ensure_woodwork_orders


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


class WoodworkOrderTimelineTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            ensure_woodwork_orders()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_pedido_page_renders_ok(self):
        response = self.client.get('/pedido')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Linha do Tempo', response.data)
        self.assertIn(b'Elabora', response.data)
        self.assertIn(b'Sinal financeiro', response.data)

    def test_consultar_order_by_formatted_cpf(self):
        response = self.client.get('/api/pedido/consultar?cpf=123.456.789-00')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        order = data['order']
        self.assertEqual(order['order_number'], 'OLA-1048')
        self.assertEqual(order['client_name'], 'Mariana Albuquerque')
        self.assertEqual(order['current_step'], 3)

        expected_steps = [
            'Pedido',
            'Sinal financeiro',
            'Elaboração da peça',
            'Pagamento',
            'Entrega',
        ]
        actual_steps = [s['name'] for s in order['steps']]
        self.assertEqual(actual_steps, expected_steps)
        self.assertEqual(order['steps'][0]['status'], 'completed')
        self.assertEqual(order['steps'][1]['status'], 'completed')
        self.assertEqual(order['steps'][2]['status'], 'active')
        self.assertEqual(order['steps'][3]['status'], 'pending')
        self.assertEqual(order['steps'][4]['status'], 'pending')

    def test_consultar_order_by_clean_cpf(self):
        response = self.client.get('/api/pedido/consultar?cpf=12345678900')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['order']['order_number'], 'OLA-1048')

    def test_consultar_order_by_order_number(self):
        response = self.client.get('/api/pedido/consultar?cpf=OLA-1052')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['order']['client_name'], 'Rodrigo Vasconcelos')
        self.assertEqual(data['order']['current_step'], 4)

    def test_consultar_non_existent_cpf(self):
        response = self.client.get('/api/pedido/consultar?cpf=999.999.999-99')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data['success'])


if __name__ == '__main__':
    unittest.main()
