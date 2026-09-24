"""Behavior and persistence tests for the blog publishing editor."""
import io
import json
import shutil
import tempfile
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
    PNG_BYTES = b'\x89PNG\r\n\x1a\n' + (b'\x00' * 32)

    def setUp(self):
        self.app = create_app(Config)
        self.upload_root = tempfile.mkdtemp(prefix='olinda-blog-test-')
        self.app.static_folder = self.upload_root
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
        shutil.rmtree(self.upload_root)

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
            'cover_image': '',
            'cover_image_file': (io.BytesIO(BlogEditorTests.PNG_BYTES), 'capa-artigo.png'),
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
        self.assertIn(b'name="cover_image_file"', response.data)
        self.assertIn(b'contenteditable="true"', response.data)
        self.assertIn(b'id="insertImageButton"', response.data)
        self.assertIn(b'id="insertVideoButton"', response.data)
        self.assertIn(b'id="mediaResizeOverlay"', response.data)
        self.assertIn(b'id="mediaWidthInput"', response.data)
        self.assertIn(b'id="removeMediaButton"', response.data)
        self.assertIn(b'id="draftButton"', response.data)
        self.assertIn(b'id="discardButton"', response.data)
        self.assertNotIn(b'<select id="articleCover"', response.data)

    def test_invalid_submission_preserves_values_and_writes_nothing(self):
        self.authenticate_admin()
        payload = self.valid_article()
        payload['title'] = 'Curto'
        payload['content'] = 'Pouco texto.'
        response = self.client.post('/blog/novo', data=payload, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'value="Curto"', response.data)
        self.assertIn('pelo menos 10 caracteres'.encode(), response.data)
        with self.app.app_context():
            self.assertEqual(BlogArticle.query.count(), 0)

    def test_published_article_is_persistent_and_readable(self):
        self.authenticate_admin()
        response = self.client.post('/blog/novo', data=self.valid_article(), content_type='multipart/form-data')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/blog/7'))

        with self.app.app_context():
            article = db.session.get(BlogArticle, 7)
            self.assertIsNotNone(article)
            self.assertEqual(article.slug, 'cafe-e-marcenaria-criacao-em-madeira-de-demolicao')
            self.assertEqual(len(json.loads(article.content_json)), 2)
            self.assertEqual(json.loads(article.gallery_json), ['cadeiras-encosto-empalhado-madeira-demolicao.png'])
            self.assertTrue(article.cover_image.startswith('blog/uploads/'))

        detail = self.client.get('/blog/7')
        self.assertEqual(detail.status_code, 200)
        self.assertIn('Café e marcenaria'.encode(), detail.data)
        listing = self.client.get('/blog')
        self.assertIn('Café e marcenaria'.encode(), listing.data)

    def test_new_article_requires_a_real_cover_upload(self):
        self.authenticate_admin()
        payload = self.valid_article()
        payload.pop('cover_image_file')
        payload['cover_image'] = 'hero-fachada-luz-dourada.png'
        response = self.client.post('/blog/novo', data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Carregue uma imagem de capa'.encode(), response.data)

    def test_inline_media_upload_requires_admin_and_valid_image(self):
        anonymous = self.client.post(
            '/api/blog/media',
            data={'media': (io.BytesIO(self.PNG_BYTES), 'imagem.png')},
            content_type='multipart/form-data',
        )
        self.assertEqual(anonymous.status_code, 403)

        self.authenticate_admin()
        missing = self.client.post('/api/blog/media', data={})
        self.assertEqual(missing.status_code, 400)
        self.assertIn('Selecione uma imagem'.encode(), missing.data)

        invalid = self.client.post(
            '/api/blog/media',
            data={'media': (io.BytesIO(b'isto nao e uma imagem'), 'arquivo.png')},
            content_type='multipart/form-data',
        )
        self.assertEqual(invalid.status_code, 400)

        valid = self.client.post(
            '/api/blog/media',
            data={'media': (io.BytesIO(self.PNG_BYTES), 'imagem.png')},
            content_type='multipart/form-data',
        )
        self.assertEqual(valid.status_code, 200)
        self.assertTrue(valid.get_json()['url'].startswith('/static/images/blog/uploads/'))

    def test_rich_html_is_sanitized_but_keeps_supported_media(self):
        self.authenticate_admin()
        payload = self.valid_article()
        repeated = 'Conteúdo editorial seguro e detalhado para explicar o trabalho artesanal. ' * 3
        payload['content_html'] = (
            f'<h2 class="text-center" onclick="alert(1)">Processo</h2><p>{repeated}</p>'
            '<script>alert("x")</script>'
            '<figure class="media-right ruim"><img src="javascript:alert(1)" onerror="alert(1)"></figure>'
            '<div class="video-wrapper" style="width:62.5%"><iframe src="https://www.youtube-nocookie.com/embed/abc123" '
            'onload="alert(1)"></iframe></div><strong>Feito à mão</strong>'
        )
        response = self.client.post('/blog/novo', data=payload, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            html = db.session.get(BlogArticle, 7).content_html
            self.assertNotIn('<script', html)
            self.assertNotIn('onclick', html)
            self.assertNotIn('onerror', html)
            self.assertNotIn('javascript:', html)
            self.assertIn('class="text-center"', html)
            self.assertIn('style="width:62.5%"', html)
            self.assertIn('https://www.youtube-nocookie.com/embed/abc123', html)
            self.assertIn('<strong>Feito à mão</strong>', html)

    def test_incomplete_draft_is_saved_hidden_and_can_be_resumed(self):
        self.authenticate_admin()
        response = self.client.post('/blog/novo', data={
            'title': 'Ideia inicial',
            'category': 'Projetos Autorais',
            'author_name': 'Olinda Aguiar',
            'content': 'Algumas anotações.',
            'submit_action': 'draft',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/blog/7/editar'))

        with self.app.app_context():
            draft = db.session.get(BlogArticle, 7)
            self.assertEqual(draft.status, 'draft')
            self.assertFalse(draft.active)
            self.assertEqual(draft.title, 'Ideia inicial')

        editor = self.client.get('/blog/7/editar')
        self.assertEqual(editor.status_code, 200)
        self.assertIn('Rascunho salvo'.encode(), editor.data)
        admin_listing = self.client.get('/blog')
        self.assertIn('Rascunhos (1)'.encode(), admin_listing.data)
        self.assertIn(b'/blog/7/editar', admin_listing.data)

        with self.client.session_transaction() as session:
            session.clear()
        self.assertEqual(self.client.get('/blog/7').status_code, 404)
        self.assertNotIn('Ideia inicial'.encode(), self.client.get('/blog').data)

    def test_draft_can_be_completed_and_published(self):
        self.authenticate_admin()
        created = self.client.post('/blog/novo', data={
            'title': '',
            'submit_action': 'draft',
        })
        self.assertEqual(created.status_code, 302)

        payload = self.valid_article()
        payload.update({'published_date': '2026-09-24', 'submit_action': 'publish'})
        published = self.client.post(
            '/blog/7/editar', data=payload, content_type='multipart/form-data')
        self.assertEqual(published.status_code, 302)
        self.assertTrue(published.headers['Location'].endswith('/blog/7'))
        with self.app.app_context():
            article = db.session.get(BlogArticle, 7)
            self.assertEqual(article.status, 'published')
            self.assertTrue(article.active)
        self.assertEqual(self.client.get('/blog/7').status_code, 200)

    def test_saved_draft_can_be_discarded(self):
        self.authenticate_admin()
        self.client.post('/blog/novo', data={
            'title': 'Rascunho descartável',
            'submit_action': 'draft',
        })
        response = self.client.post('/blog/7/editar', data={'submit_action': 'discard'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/blog'))
        with self.app.app_context():
            self.assertIsNone(db.session.get(BlogArticle, 7))

    def test_builtin_article_can_be_edited_and_shows_edit_date(self):
        anonymous = self.client.get('/blog/1/editar')
        self.assertEqual(anonymous.status_code, 302)
        self.assertIn('/login', anonymous.headers['Location'])

        self.authenticate_admin()
        editor = self.client.get('/blog/1/editar')
        self.assertEqual(editor.status_code, 200)
        self.assertIn('Editar artigo'.encode(), editor.data)
        self.assertIn(b'name="published_date"', editor.data)

        payload = self.valid_article()
        payload.pop('cover_image_file')
        payload.update({
            'title': 'O resgate das madeiras centenárias atualizado',
            'cover_image': 'hero-fachada-luz-dourada.png',
            'published_date': '2026-09-24',
        })
        saved = self.client.post('/blog/1/editar', data=payload)
        self.assertEqual(saved.status_code, 302)
        self.assertTrue(saved.headers['Location'].endswith('/blog/1'))

        detail = self.client.get('/blog/1')
        self.assertIn('Editado em'.encode(), detail.data)
        self.assertIn('Editar artigo'.encode(), detail.data)
        with self.app.app_context():
            article = db.session.get(BlogArticle, 1)
            self.assertIsNotNone(article.edited_at)

        with self.client.session_transaction() as session:
            session.clear()
        public_detail = self.client.get('/blog/1')
        self.assertNotIn('Editar artigo'.encode(), public_detail.data)

    def test_detail_sidebar_is_in_portuguese_and_uses_official_instagram(self):
        response = self.client.get('/blog/1')
        self.assertEqual(response.status_code, 200)
        for old_heading in (b'>Search<', b'>Upcoming Post<', b'>Popular Post<', b'>Email Newsletter<',
                            b'>Categories<', b'>Date<', b'>Post by<'):
            self.assertNotIn(old_heading, response.data)
        self.assertIn('Buscar no blog'.encode(), response.data)
        self.assertIn('Artigos recentes'.encode(), response.data)
        self.assertIn('Novidades por e-mail'.encode(), response.data)
        self.assertIn(b'https://www.instagram.com/olindaaguiartemadeira/', response.data)
        self.assertNotIn(b'blog-sidebar-insta-grid', response.data)


if __name__ == '__main__':
    unittest.main()
