"""Regression coverage for public catalog content and article navigation."""
import unittest
from html.parser import HTMLParser
from apps import create_app, db


class Config:
    TESTING = True
    SECRET_KEY = 'public-catalog-test'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTO_CREATE_SCHEMA = True
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    ASSETS_ROOT = '/static'


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


class PublicCatalogTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Config)
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_blog_lists_each_article_once_and_links_to_readable_pages(self):
        response = self.client.get('/blog')
        self.assertEqual(response.status_code, 200)
        elements = Elements(response.text).elements
        cards = [attrs for _, attrs in elements if 'blog-article-item' in attrs.get('class', '').split()]
        from apps.pages.routes import get_blog_articles
        with self.app.app_context():
            articles = get_blog_articles()
        self.assertCountEqual([card['data-id'] for card in cards], [str(a['id']) for a in articles])
        categories = {attrs['data-category'] for tag, attrs in elements if tag == 'button' and 'data-category' in attrs}
        self.assertTrue({a['category'] for a in articles}.issubset(categories))
        for article in articles:
            self.assertEqual(self.client.get('/blog/' + str(article['id'])).status_code, 200)
        self.assertNotIn('abrirDetalhesArtigo', response.text)

    def test_metadata_describes_each_page_and_article(self):
        descriptions = []
        for path in ['/blog', '/loja', '/blog/6']:
            response = self.client.get(path)
            elements = Elements(response.text).elements
            meta = {a.get('name', a.get('property')): a.get('content') for tag, a in elements if tag == 'meta'}
            self.assertEqual(meta['description'], meta['og:description'])
            self.assertTrue(meta['og:image'].startswith('http://localhost/static/'))
            descriptions.append(meta['description'])
        self.assertEqual(len(set(descriptions)), 3)

    def test_store_actions_are_keyboard_controls_and_dialogs_are_named(self):
        response = self.client.get('/loja')
        self.assertEqual(response.status_code, 200)
        elements = Elements(response.text).elements
        ids = {a['id'] for _, a in elements if 'id' in a}
        for _, attrs in elements:
            if attrs.get('role') == 'dialog':
                self.assertIn(attrs.get('aria-labelledby'), ids)
        metric = [(tag, a) for tag, a in elements if a.get('id') == 'openWishlistMetric']
        self.assertEqual(metric[0][0], 'button')
        titles = [(tag, a) for tag, a in elements if 'card-title-clickable' in a.get('class', '').split()]
        self.assertTrue(titles)
        self.assertTrue(all(tag == 'button' for tag, _ in titles))
        self.assertNotIn('store-add-btn', response.text)

    def test_landing_faq_is_compact_and_collapsed_initially(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        elements = Elements(response.text).elements
        faq_buttons = [attrs for tag, attrs in elements
                       if tag == 'button' and attrs.get('data-bs-parent') is None
                       and attrs.get('data-bs-target', '').startswith('#collapse')]
        self.assertEqual(len(faq_buttons), 5)
        self.assertTrue(all(button.get('aria-expanded') == 'false' for button in faq_buttons))
        self.assertTrue(all('collapsed' in button.get('class', '').split() for button in faq_buttons))
        self.assertIn('faq-compact', response.text)

    def test_default_landing_reviews_use_consistent_female_profiles(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        for name, avatar in [
            ('Mariana Albuquerque', 'avatar-3.jpg'),
            ('Helena Vasconcelos', 'avatar-6.jpg'),
            ('Dra. Cecília Meireles', 'avatar-9.jpg'),
        ]:
            self.assertIn(name, response.text)
            self.assertIn('/images/users/' + avatar, response.text)
        self.assertNotIn('Rodrigo Vasconcelos', response.text)
