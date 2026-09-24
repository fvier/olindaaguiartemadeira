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
        from apps.pages.store_catalog import reset_catalog_to_defaults
        reset_catalog_to_defaults()

    def test_pedido_page_renders_ok(self):
        response = self.client.get('/pedido')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Linha do Tempo', response.data)
        self.assertIn(b'Elabora', response.data)
        self.assertIn(b'Sinal financeiro', response.data)

    def test_byll_tribute_page_renders_ok(self):
        response = self.client.get('/byll')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mestre Byll', response.data)
        self.assertIn(b'byll-e-olinda-aguiar.png', response.data)
        self.assertIn(b'byll-mestre-artesao.png', response.data)
        self.assertIn(b'administra', response.data)

    def test_loja_page_renders_catalog(self):
        response = self.client.get('/loja')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mesa Escultural', response.data)
        self.assertIn(b'Peroba Rosa', response.data)
        self.assertIn(b'store-product-grid', response.data)
        self.assertIn(b'storeProductModal', response.data)

    def test_api_loja_produtos(self):
        response = self.client.get('/api/loja/produtos')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertGreater(len(data['products']), 0)
        first_product = data['products'][0]
        self.assertIn('id', first_product)
        self.assertIn('wood_type', first_product)
        self.assertIn('price', first_product)

        # Verifica a nova bancada em prancha macica OLA-B15
        bancada = next((p for p in data['products'] if p['id'] == 'OLA-B15'), None)
        self.assertIsNotNone(bancada)
        self.assertEqual(len(bancada['images']), 2)
        self.assertIn('Verniz PU', bancada['name'])
        self.assertIn('Cada racha e marca', bancada['description'])

        # Verifica os armários em jatobá OLA-A16 com lambri de demolição
        armario = next((p for p in data['products'] if p['id'] == 'OLA-A16'), None)
        self.assertIsNotNone(armario)
        self.assertEqual(armario['wood_type'], 'jatoba')
        self.assertEqual(len(armario['images']), 3)
        self.assertIn('Jatobá', armario['name'])
        self.assertIn('lambri de demolição', armario['description'])

        # Verifica o bar em lambri de jatobá OLA-B17
        bar = next((p for p in data['products'] if p['id'] == 'OLA-B17'), None)
        self.assertIsNotNone(bar)
        self.assertEqual(bar['wood_type'], 'jatoba')
        self.assertIn('Lambri de Jatobá', bar['name'])
        self.assertIn('bar todo em lambri de jatobá', bar['description'].lower())

        # Verifica a cadeira com encosto empalhado à mão OLA-C18
        chair = next((p for p in data['products'] if p['id'] == 'OLA-C18'), None)
        self.assertIsNotNone(chair)
        self.assertEqual(chair['wood_type'], 'peroba-rosa')
        self.assertEqual(chair['category'], 'Bancos & Banquetas')
        self.assertIn('Encosto Empalhado', chair['name'])
        self.assertIn('encosto empalhado à mão', chair['description'].lower())

        # Verifica a cristaleira colonial OLA-C19
        cristaleira = next((p for p in data['products'] if p['id'] == 'OLA-C19'), None)
        self.assertIsNotNone(cristaleira)
        self.assertEqual(cristaleira['wood_type'], 'peroba-rosa')
        self.assertEqual(cristaleira['category'], 'Cristaleiras & Armários')
        self.assertIn('Cristaleira Colonial', cristaleira['name'])
        self.assertIn('divisões envidraçadas', cristaleira['description'].lower())

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

    def test_loja_page_renders_mar_de_tags(self):
        response = self.client.get('/loja')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'store-tag-sea-card', response.data)
        self.assertIn(b'Mar de Tags', response.data)
        self.assertIn(b'storeTagGroupsNav', response.data)
        self.assertIn(b'store-tag-pill', response.data)
        self.assertIn(b'store-card-tags', response.data)
        self.assertIn(b'modalTagsBlock', response.data)

    def test_api_loja_produtos_contains_tags(self):
        response = self.client.get('/api/loja/produtos')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('tags', data)
        self.assertGreaterEqual(len(data['tags']), 30)

        # Check tag structure
        sample_tag = data['tags'][0]
        self.assertIn('slug', sample_tag)
        self.assertIn('name', sample_tag)
        self.assertIn('icon', sample_tag)
        self.assertIn('group', sample_tag)
        self.assertIn('count', sample_tag)
        self.assertGreater(sample_tag['count'], 0)

        # Check tags on specific products
        bancada = next((p for p in data['products'] if p['id'] == 'OLA-B15'), None)
        self.assertIsNotNone(bancada)
        self.assertIn('tags', bancada)
        self.assertIn('verniz-pu', bancada['tags'])

        chair = next((p for p in data['products'] if p['id'] == 'OLA-C18'), None)
        self.assertIsNotNone(chair)
        self.assertIn('empalhado-a-mao', chair['tags'])

    def test_store_tags_module_functions(self):
        from apps.pages.store_catalog import get_store_tags, get_store_tag_groups
        tags = get_store_tags()
        groups = get_store_tag_groups()

        self.assertGreater(len(tags), 30)
        self.assertEqual(len(groups), 6)
        group_ids = [g['id'] for g in groups]
        self.assertIn('all', group_ids)
        self.assertIn('madeiras', group_ids)
        self.assertIn('tecnicas', group_ids)
        self.assertIn('ambientes', group_ids)

    def test_navbar_renders_entrar_button_and_login_flow(self):
        # 1. Usuário anônimo vê o botão 'Entrar' nas páginas públicas
        res_home = self.client.get('/')
        self.assertEqual(res_home.status_code, 200)
        self.assertIn(b'Entrar', res_home.data)
        self.assertIn(b'/login', res_home.data)

        res_loja = self.client.get('/loja')
        self.assertEqual(res_loja.status_code, 200)
        self.assertIn(b'Entrar', res_loja.data)

        # 2. Tela de login exibe identidade Olinda Aguiar
        res_login = self.client.get('/login', follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Olinda Aguiar', res_login.data)
        self.assertIn(b'Entrar no Painel', res_login.data)

        # 3. Usuário autenticado vê o botão 'Painel' e seu e-mail
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['user_email'] = 'admin@olindaaguiar.com'
            sess['user_role'] = 'admin'

        res_logged = self.client.get('/')
        self.assertEqual(res_logged.status_code, 200)
        self.assertIn(b'Painel', res_logged.data)
        self.assertIn(b'admin@olindaaguiar.com', res_logged.data)
        self.assertIn(b'/logout', res_logged.data)

    def test_loja_page_renders_admin_edit_controls_only_for_admin(self):
        # 1. Usuário anônimo não vê botões ou modal de edição admin na loja
        res_anon = self.client.get('/loja')
        self.assertEqual(res_anon.status_code, 200)
        self.assertNotIn(b'store-admin-banner', res_anon.data)
        self.assertNotIn(b'adminProductEditModal', res_anon.data)
        self.assertNotIn(b'store-admin-card-edit-btn', res_anon.data)

        # 2. Usuário comum (role 'usuario') não vê controles admin
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['user_email'] = 'cliente@exemplo.com'
            sess['user_role'] = 'usuario'

        res_user = self.client.get('/loja')
        self.assertEqual(res_user.status_code, 200)
        self.assertNotIn(b'store-admin-banner', res_user.data)
        self.assertNotIn(b'adminProductEditModal', res_user.data)

        # 3. Administrador autenticado vê os controles de edição
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['user_email'] = 'admin@olindaaguiar.com'
            sess['user_role'] = 'admin'

        res_admin = self.client.get('/loja')
        self.assertEqual(res_admin.status_code, 200)
        self.assertIn(b'store-admin-banner', res_admin.data)
        self.assertIn(b'adminProductEditModal', res_admin.data)
        self.assertIn(b'store-admin-card-edit-btn', res_admin.data)
        self.assertIn('Modo de Edição do Administrador Ativo'.encode('utf-8'), res_admin.data)

    def test_admin_card_edit_permissions_and_save(self):
        from apps.pages.store_catalog import get_product_by_id

        # 1. Tentativa anônima deve ser barrada com 403 Forbidden
        payload = {
            'id': 'OLA-B15',
            'name': 'Tentativa Hacker',
            'price': 999.00
        }
        res_anon = self.client.post('/api/loja/produto/salvar', json=payload)
        self.assertEqual(res_anon.status_code, 403)
        self.assertFalse(res_anon.get_json()['success'])

        # 2. Tentativa por usuário comum ('usuario') também deve receber 403
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['user_email'] = 'cliente@exemplo.com'
            sess['user_role'] = 'usuario'

        res_user = self.client.post('/api/loja/produto/salvar', json=payload)
        self.assertEqual(res_user.status_code, 403)

        # 3. Tentativa como admin com ID inválido retorna 404
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['user_email'] = 'admin@olindaaguiar.com'
            sess['user_role'] = 'admin'

        res_not_found = self.client.post('/api/loja/produto/salvar', json={'id': 'NAO-EXISTE', 'name': 'Teste'})
        self.assertEqual(res_not_found.status_code, 404)

        # 4. Edição válida com admin para a bancada OLA-B15
        valid_update = {
            'id': 'OLA-B15',
            'name': 'Bancada Rústica Nobre de Demolição em Verniz PU',
            'price': 4200.0,
            'old_price': 4800.0,
            'badge': 'Edição Especial de Ateliê',
            'tags': ['verniz-pu', 'demolicao', 'bancada', 'edicao-especial'],
            'sizes': ['2,20m x 0,60m x 0,90m', 'Sob medida'],
            'wood_type': 'peroba-rosa',
            'is_sold_out': False,
            'description': 'Bancada artesanal em prancha única de madeira de demolição, impermeabilizada com verniz PU marítimo.'
        }
        res_save = self.client.post('/api/loja/produto/salvar', json=valid_update)
        self.assertEqual(res_save.status_code, 200)
        data = res_save.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['product']['name'], 'Bancada Rústica Nobre de Demolição em Verniz PU')
        self.assertEqual(data['product']['price'], 4200.0)
        self.assertEqual(data['product']['old_price'], 4800.0)
        self.assertEqual(data['product']['badge'], 'Edição Especial de Ateliê')
        self.assertIn('edicao-especial', data['product']['tags'])

        # 5. Verifica se o catálogo reflete a alteração imediatamente
        prod = get_product_by_id('OLA-B15')
        self.assertIsNotNone(prod)
        self.assertEqual(prod['name'], 'Bancada Rústica Nobre de Demolição em Verniz PU')
        self.assertEqual(prod['price'], 4200.0)


if __name__ == '__main__':
    unittest.main()

