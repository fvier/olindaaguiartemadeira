"""Behavior and persistence tests for the blog publishing editor."""
import json
import unittest

from apps import create_app, db
from apps.pages.models import BlogArticle


class Config:
    TESTING = True
    SECRET_KEY = 'blog-editor-test'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTO_CREATE_SCHEMA = True
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    ASSETS_ROOT = '/static'


class BlogEditorTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Config)
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def authenticate_admin(self):
        with self.client.session_transaction() as session:
            session['logged_in'] = True
            session['user_role'] = 'admin'
            session['user_email'] = 'admin@example.com'

    @staticmethod
    def valid_article():
        return {
            'title': 'Café e marcenaria: criação em madeira de demolição',
            'category': 'Projetos Autorais',
            'author_name': 'Olinda Aguiar',
            'cover_image': 'hero-fachada-luz-dourada.png',
            'excerpt': 'Uma história sobre desenho autoral, memória e o reaproveitamento cuidadoso de madeiras antigas.',
            'quote': 'Cada veio preservado acrescenta memória à peça contemporânea.',
            'content': ('O processo começa com a escolha consciente de vigas antigas, observando os veios, '
                        'as marcas do tempo e as possibilidades de cada peça de madeira.\n\n'
                        'Depois do desenho, a equipe estabiliza a matéria-prima e trabalha os encaixes à mão, '
                        'mantendo sinais da história original no acabamento final.'),
            'gallery_image_1': 'cadeiras-encosto-empalhado-madeira-demolicao.png',
            'gallery_image_2': '',
        }

    def test_editor_requires_admin_session(self):
        response = self.client.get('/blog/novo')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    def test_editor_renders_live_preview_and_automatic_read_time(self):
        self.authenticate_admin()
        response = self.client.get('/blog/novo')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="previewTitle"', response.data)
        self.assertIn(b'id="wordCount"', response.data)
        self.assertNotIn(b'name="read_time"', response.data)
        self.assertIn('Salvo permanentemente'.encode(), response.data)

    def test_invalid_submission_preserves_values_and_writes_nothing(self):
        self.authenticate_admin()
        payload = self.valid_article()
        payload['title'] = 'Curto'
        payload['content'] = 'Pouco texto.'
        response = self.client.post('/blog/novo', data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'value="Curto"', response.data)
        self.assertIn('pelo menos 10 caracteres'.encode(), response.data)
        with self.app.app_context():
            self.assertEqual(BlogArticle.query.count(), 0)

    def test_published_article_is_persistent_and_readable(self):
        self.authenticate_admin()
        response = self.client.post('/blog/novo', data=self.valid_article())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/blog/7'))

        with self.app.app_context():
            article = db.session.get(BlogArticle, 7)
            self.assertIsNotNone(article)
            self.assertEqual(article.slug, 'cafe-e-marcenaria-criacao-em-madeira-de-demolicao')
            self.assertEqual(len(json.loads(article.content_json)), 2)
            self.assertEqual(json.loads(article.gallery_json), ['cadeiras-encosto-empalhado-madeira-demolicao.png'])

        detail = self.client.get('/blog/7')
        self.assertEqual(detail.status_code, 200)
        self.assertIn('Café e marcenaria'.encode(), detail.data)
        listing = self.client.get('/blog')
        self.assertIn('Café e marcenaria'.encode(), listing.data)


if __name__ == '__main__':
    unittest.main()
