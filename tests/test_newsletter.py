import unittest
from apps import create_app, db
from apps.pages.models import NewsletterSubscriber


class NewsletterTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app('apps.config.DebugConfig')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_newsletter_subscribe_success(self):
        response = self.client.post('/api/newsletter/subscribe', json={'email': 'cliente@exemplo.com'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        subscriber = NewsletterSubscriber.query.filter_by(email='cliente@exemplo.com').first()
        self.assertIsNotNone(subscriber)
        self.assertTrue(subscriber.active)

    def test_newsletter_subscribe_duplicate(self):
        self.client.post('/api/newsletter/subscribe', json={'email': 'duplicado@exemplo.com'})
        response = self.client.post('/api/newsletter/subscribe', json={'email': 'duplicado@exemplo.com'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('já está cadastrado', data['message'])

    def test_newsletter_subscribe_invalid_email(self):
        response = self.client.post('/api/newsletter/subscribe', json={'email': 'invalido'})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])


if __name__ == '__main__':
    unittest.main()
