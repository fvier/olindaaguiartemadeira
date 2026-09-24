from apps.pages import blueprint
from apps.pages.models import (User, CarouselImage, CommercialPlan, PlanVersion, LinktreeLink,
                               LandingCard, FinancialCategory, FinancialEntry, AuditLog, FinancialCompany,
                               IntegratedSale, ClientReview, WoodworkOrder, BlogArticle, NewsletterSubscriber)
from apps.pages.store_catalog import (get_woodwork_products, get_store_categories,
                                      get_store_wood_types, get_store_tags,
                                      get_store_tag_groups, update_woodwork_product,
                                      get_product_by_id)
from apps import db, csrf, limiter
from flask import abort, render_template, request, redirect, url_for, session, flash, current_app, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from uuid import uuid4
import os
import json
import math
import re
import secrets
import unicodedata
from collections import Counter
from datetime import datetime, timezone, date, timedelta
from decimal import Decimal, InvalidOperation
from html import escape
from html.parser import HTMLParser
from urllib.parse import quote, urljoin, urlparse
from jinja2 import TemplateNotFound

# Public pages that do not require authentication
PUBLIC_PAGES = [
    'landing', 'landing.html',
    'loja', 'loja.html',
    'pedido', 'pedido.html',
    'blog', 'blog.html',
    'byll', 'byll.html',
    'byll/historia', 'byll/historia.html',
    'historia', 'historia.html',
    'index', 'index.html',
    'links', 'links.html',
    'auth-signin', 'auth-signin.html',
    'auth-signup', 'auth-signup.html',
    'auth-password', 'auth-password.html',
    'auth-logout', 'auth-logout.html',
    'api/newsletter/subscribe',
    'favicon.ico', 'apple-touch-icon.png', 'apple-touch-icon-precomposed.png'
]

MAX_PRIVILEGE_EMAILS = {email.strip().lower() for email in os.getenv('MAX_PRIVILEGE_EMAILS', '').split(',') if email.strip()}
INITIAL_USER_PASSWORD = 'bemvindo'
VALID_ROLES = {'admin', 'gerente', 'usuario'}
VALID_CATEGORIES = {'Orange', 'Blue', 'Green', 'Gold', 'Platinum', 'Diamond', 'Black'}

CAROUSEL_IMAGE_TITLES = {
    'hero-fachada-coral-entardecer.png': 'Fachada Coral ao Entardecer — Olinda Aguiar',
    'hero-fachada-noite-azul.png': 'Fachada Noturna com Iluminação Cênica Quente',
    'hero-fachada-luz-dourada.png': 'Casarão Histórico sob Luz Dourada',
    'hero-set-hatches-v2.png': 'Conjunto 1 — Carros hatch populares',
    'hero-conjunto-2-v2.png': 'Conjunto 2 — Motos populares',
    'hero-conjunto-3-v2.png': 'Conjunto 3 — Pick-ups leves e utilitários',
    'hero-conjunto-4-v2.png': 'Conjunto 4 — Camionetes e SUVs grandes',
    'hero-conjunto-5-v2.png': 'Conjunto 5 — Motos premium e aventureiras',
    'rastrek_hero_vehicle.png': 'Range Rover — imagem original',
}
DEFAULT_ACTIVE_CAROUSEL = [
    'hero-fachada-coral-entardecer.png',
    'hero-fachada-noite-azul.png',
    'hero-fachada-luz-dourada.png',
]
CAROUSEL_SET_TYPES = {
    'conjunto_1': 'Conjunto 1 — Carros Hatch',
    'conjunto_2': 'Conjunto 2 — Motos Populares',
    'conjunto_3': 'Conjunto 3 — Pick-ups e Utilitários',
    'conjunto_4': 'Conjunto 4 — Camionetes e SUVs',
    'conjunto_5': 'Conjunto 5 — Motos Premium',
    'outros': 'Outros / Testes',
}

DEFAULT_PLAN_BENEFITS = [
    'Madeira de demolição 100% nobre, recuperada e imunizada',
    'Acabamento artesanal fino com ceras e óleos naturais atóxicos',
    'Peça autoral única assinada pelo ateliê de Olinda Aguiar',
    'Embalagem estruturada e envio protegido para todo o Brasil',
    'Curadoria e consultoria sob medida para arquitetos e clientes',
]

DEFAULT_PLANS = [
    ('Esculturas & Obras de Autor', 'Arte em Madeira', 'Peça Autoral Única', 380, 'Esculturas entalhadas à mão valorizando os veios históricos e nós da madeira.', 'ESCULTURAS', False),
    ('Mesas & Mobiliário Orgânico', 'Mobiliário Nobre', 'Demolição Maciça', 1850, 'Mesas de centro, jantar e aparadores com borda orgânica e acabamento acetinado.', 'MÓVEIS', False),
    ('Painéis & Revestimentos', 'Design de Parede', 'Composição Rústica', 950, 'Painéis arquitetônicos em relevo feitos com madeira de demolição restaurada.', 'PAINÉIS', False),
    ('Utilitários & Linha Gourmet', 'Arte Culinária', 'Madeira Tratada', 190, 'Tábuas nobres de corte, gamelas e travessas com cura mineral atóxica.', 'UTILITÁRIOS', False),
    ('Projetos Sob Medida & Arquitetura', 'Alta Marcenaria', 'Design Exclusivo', 2800, 'Mobiliário e obras customizadas sob liderança e consultoria de Olinda Aguiar.', 'SOB MEDIDA', True),
]

DEFAULT_LINKS = [
    ('Fale conosco pelo WhatsApp', '(81) 9 9452-2504 · Atendimento e encomendas', 'https://api.whatsapp.com/send?phone=5581994522504&text=Ol%C3%A1!%20Gostaria%20de%20informa%C3%A7%C3%B5es%20sobre%20as%20pe%C3%A7as%20em%20madeira.', 'ri-whatsapp-line', '#22c55e'),
    ('Ligar agora', '(81) 9 9452-2504 · Atendimento direto', 'tel:+5581994522504', 'ri-phone-line', '#0ea5e9'),
    ('Instagram do Ateliê', '@olindaaguiartemadeira · Galeria e peças autorais', 'https://www.instagram.com/olindaaguiartemadeira/', 'ri-instagram-line', '#e1306c'),
    ('Facebook', 'Página Oficial no Facebook', 'https://www.facebook.com/BylleOlinda', 'ri-facebook-circle-line', '#1877f2'),
    ('Localização do Ateliê', '478 R. Cel. Joaquim Cavalcante, Carmo, Olinda - PE', 'https://www.google.com/maps?q=-8.0122,-34.8543&z=17&hl=pt-BR', 'ri-map-pin-2-line', '#ef4444'),
]

PERMISSION_MODULES = [
    {'name': 'Landing page', 'route': '/', 'icon': 'ri-global-line', 'color': 'primary', 'login': False, 'usuario': 'total', 'gerente': 'total', 'admin': 'total'},
    {'name': 'Painel público da TV', 'route': '/index', 'icon': 'ri-tv-2-line', 'color': 'info', 'login': False, 'usuario': 'total', 'gerente': 'total', 'admin': 'total'},
    {'name': 'Dashboard de vendas', 'route': '/dashboard-sales', 'icon': 'ri-line-chart-line', 'color': 'success', 'login': True, 'usuario': 'total', 'gerente': 'total', 'admin': 'total'},
    {'name': 'Comissionamento', 'route': '/comissionamento', 'icon': 'ri-table-line', 'color': 'info', 'login': True, 'usuario': 'limited', 'gerente': 'total', 'admin': 'total'},
    {'name': 'Vendas', 'route': '/vendas', 'icon': 'ri-shopping-cart-2-line', 'color': 'primary', 'login': True, 'usuario': 'limited', 'gerente': 'total', 'admin': 'total'},
    {'name': 'Validação de vendas', 'route': '/validacao-vendas', 'icon': 'ri-checkbox-circle-line', 'color': 'warning', 'login': True, 'usuario': 'none', 'gerente': 'total', 'admin': 'total'},
    {'name': 'Planos', 'route': '/planos', 'icon': 'ri-price-tag-3-line', 'color': 'success', 'login': True, 'usuario': 'limited', 'gerente': 'total', 'admin': 'total'},
    {'name': 'Ranking', 'route': '/ranking', 'icon': 'ri-trophy-line', 'color': 'warning', 'login': True, 'usuario': 'total', 'gerente': 'total', 'admin': 'total'},
    {'name': 'Financeiro', 'route': '/financeiro', 'icon': 'ri-wallet-3-line', 'color': 'success', 'login': True, 'usuario': 'total', 'gerente': 'total', 'admin': 'total'},
    {'name': 'Usuários e colaboradores', 'route': '/admin-cadastrar', 'icon': 'ri-team-line', 'color': 'danger', 'login': True, 'usuario': 'none', 'gerente': 'none', 'admin': 'total'},
    {'name': 'Privilégios', 'route': '/admin-privilegios', 'icon': 'ri-shield-keyhole-line', 'color': 'danger', 'login': True, 'usuario': 'none', 'gerente': 'none', 'admin': 'total'},
    {'name': 'Gerenciar carrossel', 'route': '/admin-carrossel', 'icon': 'ri-gallery-line', 'color': 'primary', 'login': True, 'usuario': 'none', 'gerente': 'none', 'admin': 'total'},
    {'name': 'Gerenciar depoimentos', 'route': '/admin-depoimentos', 'icon': 'ri-chat-smile-line', 'color': 'primary', 'login': True, 'usuario': 'none', 'gerente': 'none', 'admin': 'total'},
]


def carousel_set_type_from_filename(filename):
    lowered = filename.lower()
    if 'conjunto-2' in lowered or ('motos' in lowered and 'premium' not in lowered):
        return 'conjunto_2'
    if 'conjunto-3' in lowered or 'utilitarios' in lowered:
        return 'conjunto_3'
    if 'conjunto-4' in lowered or 'set-premium' in lowered or 'suv' in lowered:
        return 'conjunto_4'
    if 'conjunto-5' in lowered or 'motos-premium' in lowered:
        return 'conjunto_5'
    if 'hatches' in lowered:
        return 'conjunto_1'
    return 'outros'


def carousel_title_from_filename(filename):
    if filename in CAROUSEL_IMAGE_TITLES:
        return CAROUSEL_IMAGE_TITLES[filename]
    clean_name = os.path.splitext(filename)[0].replace('hero-', '').replace('rastrek-', '')
    return clean_name.replace('-', ' ').replace('_', ' ').title()


def ensure_carousel_images():
    """Register project carousel artwork without changing saved selections."""
    image_dir = os.path.join(current_app.static_folder, 'images')
    if not os.path.isdir(image_dir):
        return
    filenames = sorted(
        filename for filename in os.listdir(image_dir)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
        and (filename.startswith('hero-') or filename == 'rastrek_hero_vehicle.png')
    )
    existing = {image.filename for image in CarouselImage.query.all()}
    database_was_empty = not existing
    next_order = (db.session.query(db.func.max(CarouselImage.sort_order)).scalar() or 0) + 10
    changed = False
    for filename in filenames:
        if filename in existing:
            continue
        is_default = database_was_empty and filename in DEFAULT_ACTIVE_CAROUSEL
        default_index = DEFAULT_ACTIVE_CAROUSEL.index(filename) if is_default else None
        db.session.add(CarouselImage(
            filename=filename,
            title=carousel_title_from_filename(filename),
            set_type=carousel_set_type_from_filename(filename),
            active=is_default,
            sort_order=(default_index + 1) * 10 if is_default else next_order,
        ))
        if not is_default:
            next_order += 10
        changed = True
    for image in CarouselImage.query.all():
        inferred_type = carousel_set_type_from_filename(image.filename)
        if (not image.set_type or image.set_type == 'outros') and inferred_type != 'outros':
            image.set_type = inferred_type
            changed = True
    if changed:
        db.session.commit()


def carousel_image_view(image):
    path = os.path.join(current_app.static_folder, 'images', os.path.basename(image.filename))
    version = int(os.path.getmtime(path)) if os.path.isfile(path) else 1
    return {
        'id': image.id,
        'filename': image.filename,
        'title': image.title,
        'set_type': image.set_type if image.set_type in CAROUSEL_SET_TYPES else 'outros',
        'set_type_label': CAROUSEL_SET_TYPES.get(image.set_type, CAROUSEL_SET_TYPES['outros']),
        'active': image.active,
        'sort_order': image.sort_order,
        'version': version,
    }


def active_carousel_images():
    ensure_carousel_images()
    images = CarouselImage.query.filter_by(active=True).all()
    image_views = [carousel_image_view(image) for image in images]
    return sorted(image_views, key=lambda image: (-image['version'], -image['id']))


def ensure_commercial_content():
    """Seed editable public content once for new and existing installations."""
    changed = False
    has_old_plans = any(p.vehicle_type in ['Qualquer veículo', 'Moto', 'Carro'] or 'FIPE' in (p.coverage or '') for p in CommercialPlan.query.all())
    if CommercialPlan.query.count() == 0 or has_old_plans:
        LandingCard.query.delete()
        CommercialPlan.query.delete()
        db.session.flush()
        benefits = '\n'.join(DEFAULT_PLAN_BENEFITS)
        for position, item in enumerate(DEFAULT_PLANS, start=1):
            name, vehicle_type, coverage, price, description, badge, featured = item
            db.session.add(CommercialPlan(
                name=name, vehicle_type=vehicle_type, coverage=coverage,
                monthly_price=price, installation_price=0, description=description,
                benefits=benefits, badge=badge, featured=featured,
                whatsapp_url=f'https://api.whatsapp.com/send?phone=5581994522504&text=Olá! Gostaria de encomendar ou saber mais sobre a linha {name} da Olinda Arte em Madeira.',
                active=True, sort_order=position * 10,
            ))
        changed = True
    if changed:
        db.session.flush()
    if LandingCard.query.count() == 0:
        plans = CommercialPlan.query.order_by(CommercialPlan.sort_order.asc(), CommercialPlan.id.asc()).limit(5).all()
        for slot, plan in enumerate(plans, start=1):
            db.session.add(LandingCard(slot=slot, plan_id=plan.id, benefits=plan.benefits))
        changed = True
    has_old_links = any('5583991386279' in (l.url or '') for l in LinktreeLink.query.all())
    if LinktreeLink.query.count() == 0 or has_old_links:
        LinktreeLink.query.delete()
        for position, item in enumerate(DEFAULT_LINKS, start=1):
            title, subtitle, url, icon, color = item
            db.session.add(LinktreeLink(title=title, subtitle=subtitle, url=url, icon=icon,
                                         color=color, active=True, sort_order=position * 10))
        changed = True
    default_reviews = [
        ("Mariana Albuquerque", "Arquiteta e designer de interiores", "avatar-3.jpg", 5, "A mesa em madeira maciça de demolição que a Olinda e sua equipe produziram para o meu projeto ficou espetacular. O cuidado com cada detalhe e a condução sensível de todo o processo tornaram o resultado ainda mais especial.", 10),
        ("Helena Vasconcelos", "Colecionadora de arte contemporânea", "avatar-6.jpg", 5, "Visitei o casarão colonial no Carmo e fiquei encantada com a curadoria. Minha escultura chegou impecável, cuidadosamente embalada e preservando toda a beleza dos veios históricos da madeira.", 20),
        ("Dra. Cecília Meireles", "Apreciadora de arte popular", "avatar-9.jpg", 5, "O ateliê da Olinda Aguiar une o charme da nossa história, sustentabilidade e acabamento primoroso. São peças únicas, com presença e alma, que transformam o ambiente.", 30),
    ]
    has_old_reviews = any('veicular' in (r.review_text or '').lower() or 'rastreamento' in (r.review_text or '').lower() or 'paraíba' in (r.review_text or '').lower() for r in ClientReview.query.all())
    if ClientReview.query.count() == 0 or has_old_reviews:
        ClientReview.query.delete()
        for name, role, avatar, rating, text, order in default_reviews:
            db.session.add(ClientReview(
                client_name=name,
                client_role=role,
                avatar_filename=avatar,
                rating=rating,
                review_text=text,
                sort_order=order,
                active=True
            ))
        changed = True
    else:
        # Corrige somente o conjunto demonstrativo antigo. Depoimentos criados ou
        # personalizados pelo painel administrativo permanecem intactos.
        legacy_default_reviews = {
            ("Mariana Albuquerque", "avatar-2.jpg"): default_reviews[0],
            ("Rodrigo Vasconcelos", "avatar-1.jpg"): default_reviews[1],
            ("Dra. Cecília Meireles", "avatar-4.jpg"): default_reviews[2],
        }
        for review in ClientReview.query.all():
            replacement = legacy_default_reviews.get((review.client_name, review.avatar_filename))
            if not replacement:
                continue
            name, role, avatar, rating, text, order = replacement
            review.client_name = name
            review.client_role = role
            review.avatar_filename = avatar
            review.rating = rating
            review.review_text = text
            review.sort_order = order
            changed = True
    if changed:
        db.session.commit()


def plan_view(plan):
    whatsapp_message = quote(f'Olá! Gostaria de encomendar ou saber mais sobre a linha {plan.name} da Olinda Arte em Madeira.')
    return {
        'id': plan.id, 'nome': plan.name, 'tipoVeiculo': plan.vehicle_type,
        'cobertura': plan.coverage, 'mensalidade': float(plan.monthly_price or 0),
        'instalacao': float(plan.installation_price or 0), 'descricao': plan.description,
        'beneficios': [line.strip() for line in (plan.benefits or '').splitlines() if line.strip()],
        'badge': plan.badge,
        'whatsappUrl': f'https://api.whatsapp.com/send?phone=5581994522504&text={whatsapp_message}',
        'ativo': plan.active,
        'destaque': plan.featured, 'ordem': plan.sort_order,
        'atualizadoEm': plan.updated_at.isoformat() if plan.updated_at else None,
        'ultimaVersao': plan.last_version_code,
    }


def link_view(link):
    return {'id': link.id, 'titulo': link.title, 'subtitulo': link.subtitle, 'url': link.url,
            'icone': link.icon, 'cor': link.color, 'ativo': link.active, 'ordem': link.sort_order}


def card_view(card):
    view = plan_view(card.plan)
    view.update({'cardId': card.id, 'slot': card.slot, 'planId': card.plan_id,
                 'beneficios': [line.strip() for line in (card.benefits or '').splitlines() if line.strip()]})
    return view


def active_plans():
    ensure_commercial_content()
    cards = LandingCard.query.join(CommercialPlan).filter(CommercialPlan.active.is_(True))\
        .order_by(LandingCard.slot.asc()).all()
    return [card_view(card) for card in cards]


def active_linktree_links():
    ensure_commercial_content()
    return [link_view(link) for link in LinktreeLink.query.filter_by(active=True)
            .order_by(LinktreeLink.sort_order.asc(), LinktreeLink.id.asc()).all()]


def normalize_user_role(email='', username='', forced_role=None):
    if forced_role:
        return forced_role.lower()
    if email.strip().lower() in MAX_PRIVILEGE_EMAILS:
        return 'admin'
    identity = f"{email} {username}".lower()
    if 'admin' in identity:
        return 'admin'
    if 'gerente' in identity:
        return 'gerente'
    return 'usuario'


def ensure_default_user():
    """Create or verify initial admin users for system access."""
    try:
        admin_email = os.getenv('INITIAL_ADMIN_EMAIL', 'admin@olindaaguiar.com').strip().lower()
        admin_password = os.getenv('INITIAL_ADMIN_PASSWORD', 'olinda2026admin')
        if admin_email and admin_password:
            default_user = User.query.filter((User.email == admin_email) | (User.username == 'admin')).first()
            if not default_user:
                default_user = User(
                    username='admin',
                    full_name='Administrador Olinda Aguiar',
                    email=admin_email,
                    role='admin',
                    category='Black',
                    active=True,
                    must_change_password=False
                )
                default_user.set_password(admin_password)
                db.session.add(default_user)
                db.session.commit()
                current_app.logger.info('Initial administrator created for %s', admin_email)
            elif not default_user.check_password(admin_password) and (not default_user.password_hash or os.getenv('RESET_DEFAULT_ADMIN', 'True') == 'True'):
                default_user.set_password(admin_password)
                default_user.full_name = 'Administrador Olinda Aguiar'
                default_user.role = 'admin'
                default_user.active = True
                db.session.commit()

        # Garantir criação/atualização do usuário 'olinda'
        olinda_user = User.query.filter((User.username == 'olinda') | (User.email == 'olinda@olindaaguiar.com')).first()
        if not olinda_user:
            olinda_user = User(
                username='olinda',
                full_name='Olinda Aguiar',
                email='olinda@olindaaguiar.com',
                role='admin',
                category='Black',
                active=True,
                must_change_password=False
            )
            olinda_user.set_password('12345Ij@!')
            db.session.add(olinda_user)
            db.session.commit()
            current_app.logger.info('User olinda created successfully.')
        else:
            olinda_user.set_password('12345Ij@!')
            olinda_user.username = 'olinda'
            olinda_user.full_name = 'Olinda Aguiar'
            olinda_user.role = 'admin'
            olinda_user.active = True
            olinda_user.must_change_password = False
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("> Error ensuring default user: " + str(e))


@blueprint.route('/favicon.ico')
@blueprint.route('/apple-touch-icon.png')
@blueprint.route('/apple-touch-icon-precomposed.png')
def serve_favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static', 'images'), 'logo_fundo_preto.png')


@blueprint.route('/')
def home():
    """Render the public landing page for Olinda Arte em Madeira."""
    ensure_default_user()
    ensure_commercial_content()
    config_data = load_reviews_config()
    max_reviews = config_data.get('max_reviews', 3)
    reviews = ClientReview.query.filter_by(active=True).order_by(ClientReview.sort_order.asc(), ClientReview.id.asc()).limit(max_reviews).all()
    return render_template('pages/landing.html', segment='landing', carousel_images=active_carousel_images(),
                           landing_plans=active_plans(), reviews=reviews)


@blueprint.route('/loja')
@blueprint.route('/loja.html')
def loja():
    """Render dedicated store and woodwork catalog page."""
    ensure_default_user()
    ensure_commercial_content()
    products = get_woodwork_products()
    store_categories = get_store_categories()
    store_wood_types = get_store_wood_types()
    store_tags = get_store_tags()
    store_tag_groups = get_store_tag_groups()
    return render_template(
        'pages/loja.html',
        segment='loja',
        products=products,
        store_categories=store_categories,
        store_wood_types=store_wood_types,
        store_tags=store_tags,
        store_tag_groups=store_tag_groups
    )


@blueprint.route('/api/loja/produtos')
def api_loja_produtos():
    """Return JSON list of woodwork catalog products."""
    products = get_woodwork_products()
    store_tags = get_store_tags()
    return jsonify({'success': True, 'products': products, 'tags': store_tags})


@blueprint.route('/api/loja/produto/salvar', methods=['POST'])
@csrf.exempt
def api_loja_produto_salvar():
    """Save/update woodwork product details (admin only)."""
    if not (session.get('logged_in') and session.get('user_role') in {'admin', 'gerente'}):
        return jsonify({
            'success': False,
            'message': 'Acesso negado. Apenas administradores autenticados podem editar os cards da loja.'
        }), 403

    payload = request.get_json(silent=True) or request.form.to_dict()
    if not payload:
        return jsonify({'success': False, 'message': 'Dados de atualização não fornecidos.'}), 400

    product_id = str(payload.get('id', '')).strip()
    if not product_id:
        return jsonify({'success': False, 'message': 'O código/ID da peça é obrigatório.'}), 400

    updates = {}
    if 'name' in payload and str(payload['name']).strip():
        updates['name'] = str(payload['name']).strip()

    if 'category' in payload and str(payload['category']).strip():
        updates['category'] = str(payload['category']).strip()

    if 'wood_type' in payload and str(payload['wood_type']).strip():
        updates['wood_type'] = str(payload['wood_type']).strip()

    if 'badge' in payload:
        updates['badge'] = str(payload['badge']).strip()

    if 'description' in payload:
        updates['description'] = str(payload['description']).strip()

    def _parse_num(val):
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).replace('R$', '').strip()
        if not s or s.lower() in ('none', 'null', '0', '0.0'):
            return None
        if ',' in s:
            s = s.replace('.', '').replace(',', '.')
        return float(s)

    if 'price' in payload:
        try:
            parsed_price = _parse_num(payload['price'])
            if parsed_price is None or parsed_price < 0:
                return jsonify({'success': False, 'message': 'Valor de preço inválido.'}), 400
            updates['price'] = parsed_price
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Valor de preço inválido.'}), 400

    if 'old_price' in payload:
        try:
            updates['old_price'] = _parse_num(payload['old_price'])
        except (ValueError, TypeError):
            pass

    if 'sizes' in payload:
        raw_sizes = payload['sizes']
        if isinstance(raw_sizes, list):
            updates['sizes'] = [str(s).strip() for s in raw_sizes if str(s).strip()]
        elif isinstance(raw_sizes, str):
            updates['sizes'] = [s.strip() for s in raw_sizes.replace('\n', ',').split(',') if s.strip()]

    if 'tags' in payload:
        raw_tags = payload['tags']
        if isinstance(raw_tags, list):
            updates['tags'] = [str(t).strip().lstrip('#') for t in raw_tags if str(t).strip()]
        elif isinstance(raw_tags, str):
            updates['tags'] = [t.strip().lstrip('#') for t in raw_tags.replace('\n', ',').split(',') if t.strip()]

    if 'is_sold_out' in payload:
        val = payload['is_sold_out']
        updates['is_sold_out'] = val is True or str(val).lower() in ('true', '1', 'on', 'sim')

    updated = update_woodwork_product(product_id, updates)
    if not updated:
        return jsonify({'success': False, 'message': f"Peça com código '{product_id}' não encontrada no catálogo."}), 404

    # Registrar no log de auditoria
    try:
        user_email = session.get('user_email', 'admin@olindaaguiar.com')
        log = AuditLog(
            user_email=user_email,
            user_name=session.get('user_name', 'Administrador'),
            action='Edição de Card de Produto',
            details=f"Card '{updated.get('name')}' ({product_id}) atualizado com sucesso. Preço: R$ {updated.get('price'):.2f}",
            ip_address=request.remote_addr or ''
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        pass

    return jsonify({
        'success': True,
        'message': f"Card '{updated.get('name')}' ({product_id}) atualizado com sucesso!",
        'product': updated
    })


def ensure_woodwork_orders():
    """Seed initial realistic custom orders if none exist."""
    db.create_all()
    if WoodworkOrder.query.first():
        return

    sample_orders = [
        WoodworkOrder(
            order_number='OLA-1048',
            cpf='123.456.789-00',
            client_name='Mariana Albuquerque',
            client_phone='(81) 99876-5432',
            item_title='Mesa Orgânica em Peroba Rosa Centenária',
            wood_type='Peroba Rosa de Casarão Colonial do Século XIX',
            dimensions='2,40m x 1,10m x 0,78m',
            current_step=3,
            step_description='Tampo em prancha maciça nivelado no cavalete do ateliê. Em fase de entalhe manual nas bordas orgânicas e polimento com ceras naturais.',
            estimated_delivery='10/10/2026',
            total_amount=Decimal('4800.00'),
            deposit_amount=Decimal('2400.00'),
            balance_amount=Decimal('2400.00'),
            notes='Acabamento fosco acetinado em cera de carnaúba e óleo botânico atóxico.'
        ),
        WoodworkOrder(
            order_number='OLA-1052',
            cpf='987.654.321-00',
            client_name='Rodrigo Vasconcelos',
            client_phone='(11) 98765-1234',
            item_title='Escultura Pássaro Solar em Jacarandá da Bahia',
            wood_type='Jacarandá de Demolição Histórica',
            dimensions='0,85m x 0,45m (Peça de Acervo)',
            current_step=4,
            step_description='Escultura finalizada e inspecionada pessoalmente por Olinda Aguiar. Aguardando quitação do saldo restante para expedição.',
            estimated_delivery='Envio em até 48h após confirmação',
            total_amount=Decimal('2200.00'),
            deposit_amount=Decimal('1100.00'),
            balance_amount=Decimal('1100.00'),
            notes='Envio para São Paulo - SP com engradado de madeira estruturado e seguro total.'
        ),
        WoodworkOrder(
            order_number='OLA-1060',
            cpf='111.222.333-44',
            client_name='Dra. Cecília Meireles',
            client_phone='(81) 99123-4567',
            item_title='Painel Escultural de Parede em Vigas de Ipê Colonial',
            wood_type='Ipê Amarelo de Demolição Centenária',
            dimensions='2,60m x 1,30m',
            current_step=2,
            step_description='Sinal de 50% registrado com sucesso. Seleção e triagem das vigas coloniais iniciada no pátio do ateliê de Olinda.',
            estimated_delivery='25/10/2026',
            total_amount=Decimal('3600.00'),
            deposit_amount=Decimal('1800.00'),
            balance_amount=Decimal('1800.00'),
            notes='Instalação inclusa para a Região Metropolitana de Recife/Olinda.'
        ),
        WoodworkOrder(
            order_number='OLA-1035',
            cpf='555.666.777-88',
            client_name='Carlos Eduardo Guimarães',
            client_phone='(21) 98888-7777',
            item_title='Bancada Gourmet em Madeira Rústica com Borda Natural',
            wood_type='Angico Preto de Demolição',
            dimensions='1,80m x 0,65m',
            current_step=5,
            step_description='Obra concluída e entregue com sucesso! Certificado de autenticidade da madeira de demolição emitido.',
            estimated_delivery='Entregue com sucesso',
            total_amount=Decimal('3100.00'),
            deposit_amount=Decimal('1550.00'),
            balance_amount=Decimal('0.00'),
            notes='Cliente satisfeito e avaliou o ateliê com nota máxima no Google.'
        ),
        WoodworkOrder(
            order_number='OLA-1068',
            cpf='000.111.222-33',
            client_name='Beatriz Fontes',
            client_phone='(81) 97777-6666',
            item_title='Aparador Suspenso em Carvalho de Demolição',
            wood_type='Carvalho Colonial Reutilizado',
            dimensions='1,50m x 0,40m x 0,35m',
            current_step=1,
            step_description='Pedido cadastrado no ateliê. Aguardando confirmação do sinal financeiro (50%) para reservar os dormentes e iniciar o corte.',
            estimated_delivery='30 dias úteis após o sinal',
            total_amount=Decimal('2800.00'),
            deposit_amount=Decimal('0.00'),
            balance_amount=Decimal('2800.00'),
            notes='Proposta comercial enviada diretamente à cliente.'
        )
    ]

    for order in sample_orders:
        db.session.add(order)
    db.session.commit()


@blueprint.route('/pedido')
@blueprint.route('/pedido.html')
def pedido():
    """Render dedicated order consultation and custom commission page with timeline."""
    ensure_default_user()
    ensure_woodwork_orders()
    cpf_query = request.args.get('cpf', '').strip()
    order_data = None
    if cpf_query:
        import re
        clean = re.sub(r'\D', '', cpf_query)
        order = WoodworkOrder.query.filter(
            (WoodworkOrder.cpf == cpf_query) |
            (WoodworkOrder.cpf == clean) |
            (WoodworkOrder.order_number.ilike(cpf_query))
        ).first()
        if not order and len(clean) == 11:
            formatted = f"{clean[:3]}.{clean[3:6]}.{clean[6:9]}-{clean[9:]}"
            order = WoodworkOrder.query.filter_by(cpf=formatted).first()
        if order:
            order_data = order.to_dict()

    return render_template('pages/pedido.html', segment='pedido', initial_order=order_data, search_cpf=cpf_query)


@blueprint.route('/api/pedido/consultar', methods=['GET', 'POST'])
@csrf.exempt
def api_consultar_pedido():
    """JSON API to search order by CPF or order number and return timeline."""
    ensure_woodwork_orders()
    data = request.get_json(silent=True) or {}
    cpf_query = (request.args.get('cpf') or data.get('cpf') or request.form.get('cpf') or '').strip()
    if not cpf_query:
        return jsonify({'success': False, 'message': 'Por favor, informe o CPF para consultar o pedido.'}), 400

    import re
    clean = re.sub(r'\D', '', cpf_query)
    order = None

    if clean:
        formatted = f"{clean[:3]}.{clean[3:6]}.{clean[6:9]}-{clean[9:]}" if len(clean) == 11 else ''
        order = WoodworkOrder.query.filter(
            (WoodworkOrder.cpf == cpf_query) |
            (WoodworkOrder.cpf == clean) |
            (WoodworkOrder.cpf == formatted) |
            (WoodworkOrder.order_number.ilike(cpf_query))
        ).first()

    if not order:
        order = WoodworkOrder.query.filter(WoodworkOrder.order_number.ilike(cpf_query)).first()

    if not order:
        return jsonify({
            'success': False,
            'message': f'Nenhum pedido encontrado para o documento "{cpf_query}". Verifique os números digitados ou entre em contato com o ateliê.'
        }), 404

    return jsonify({
        'success': True,
        'order': order.to_dict()
    })


BLOG_CATEGORIES = (
    'Sustentabilidade',
    'Técnicas Artesanais',
    'Projetos Autorais',
    'Marcenaria Colonial',
    'Liderança & Propósito',
    'Acabamentos & Ceras',
)

BLOG_AUTHORS = {
    'Olinda Aguiar': {
        'role': 'Fundadora e Curadora',
        'avatar': 'byll-e-olinda-aguiar.png',
    },
    'Mestre Byll': {
        'role': 'Mestre Artesão Entalhador',
        'avatar': 'byll-mestre-artesao.png',
    },
}

BLOG_COVER_IMAGES = (
    ('hero-fachada-luz-dourada.png', 'Fachada sob luz dourada'),
    ('cadeiras-encosto-empalhado-madeira-demolicao.png', 'Cadeiras empalhadas'),
    ('bar-resort-lambri-jatoba.png', 'Bar em lambri de Jatobá'),
    ('cristaleira-colonial-portas-vidro-peroba.png', 'Cristaleira colonial'),
    ('hero-fachada-coral-entardecer.png', 'Fachada coral ao entardecer'),
    ('comoda-balcao-gaveteiro-demolicao.png', 'Cômoda e balcão gaveteiro'),
    ('mesa-base-escultural-vidro-1.png', 'Mesa de jantar em Peroba Rosa'),
)


def blog_slug(value):
    normalized = unicodedata.normalize('NFKD', value or '').encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]+', '-', normalized.lower()).strip('-')


def blog_paragraphs(content):
    return [paragraph.strip() for paragraph in re.split(r'\n\s*\n', content or '') if paragraph.strip()]


def blog_read_time(content):
    word_count = len(re.findall(r'\b\w+\b', content or '', flags=re.UNICODE))
    minutes = max(1, math.ceil(word_count / 180))
    return f'{minutes} min de leitura'


BLOG_FORM_FIELDS = (
    'title', 'category', 'author_name', 'cover_image', 'excerpt', 'quote',
    'content', 'content_html', 'gallery_image_1', 'gallery_image_2', 'published_date',
)

BLOG_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
BLOG_RICH_TAGS = {
    'p', 'br', 'h2', 'h3', 'strong', 'b', 'em', 'i', 'u', 's', 'blockquote',
    'ul', 'ol', 'li', 'a', 'img', 'figure', 'figcaption', 'div', 'iframe',
}
BLOG_RICH_CLASSES = {
    'media-wide', 'media-left', 'media-right', 'video-wrapper',
    'text-start', 'text-center', 'text-end',
}


class BlogHTMLSanitizer(HTMLParser):
    """Small allow-list sanitizer for HTML produced by the article editor."""
    void_tags = {'br', 'img'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    @staticmethod
    def safe_url(value, media=False, iframe=False):
        value = (value or '').strip()
        parsed = urlparse(value)
        if iframe:
            allowed_hosts = {'www.youtube.com', 'www.youtube-nocookie.com', 'player.vimeo.com'}
            if parsed.scheme == 'https' and parsed.hostname in allowed_hosts:
                return value
            return ''
        if media:
            return value if value.startswith('/static/images/blog/uploads/') else ''
        if value.startswith(('/', '#')) or parsed.scheme in {'http', 'https', 'mailto'}:
            return value
        return ''

    def clean_attrs(self, tag, attrs):
        source = dict(attrs)
        clean = []
        class_names = [name for name in source.get('class', '').split() if name in BLOG_RICH_CLASSES]
        if class_names:
            clean.append(('class', ' '.join(class_names)))
        if tag in {'figure', 'div'}:
            width_match = re.fullmatch(r'\s*width\s*:\s*(\d{1,3}(?:\.\d+)?)%\s*;?\s*',
                                       source.get('style', ''), re.IGNORECASE)
            if width_match:
                width = max(20, min(100, float(width_match.group(1))))
                clean.append(('style', f'width:{width:g}%'))
        if tag == 'a':
            href = self.safe_url(source.get('href'))
            if href:
                clean.extend([('href', href), ('rel', 'noopener noreferrer')])
                if source.get('target') == '_blank':
                    clean.append(('target', '_blank'))
        elif tag == 'img':
            src = self.safe_url(source.get('src'), media=True)
            if not src:
                return []
            clean.extend([('src', src), ('alt', source.get('alt', '')[:200]), ('loading', 'lazy')])
        elif tag == 'iframe':
            src = self.safe_url(source.get('src'), iframe=True)
            if not src:
                return []
            clean.extend([
                ('src', src), ('title', source.get('title', 'Vídeo incorporado')[:200]),
                ('loading', 'lazy'), ('allowfullscreen', ''),
            ])
        return clean

    def handle_starttag(self, tag, attrs):
        if tag not in BLOG_RICH_TAGS:
            return
        clean_attrs = self.clean_attrs(tag, attrs)
        if tag in {'img', 'iframe'} and not any(name == 'src' for name, _ in clean_attrs):
            return
        rendered = ''.join(f' {name}="{escape(value, quote=True)}"' if value else f' {name}'
                           for name, value in clean_attrs)
        self.parts.append(f'<{tag}{rendered}>')

    def handle_endtag(self, tag):
        if tag in BLOG_RICH_TAGS and tag not in self.void_tags:
            self.parts.append(f'</{tag}>')

    def handle_data(self, data):
        self.parts.append(escape(data))


class BlogPlainTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        if data.strip():
            self.parts.append(data.strip())


def clean_blog_html(value):
    sanitizer = BlogHTMLSanitizer()
    sanitizer.feed(value or '')
    return ''.join(sanitizer.parts).strip()


def blog_html_text(value):
    parser = BlogPlainTextParser()
    parser.feed(value or '')
    return ' '.join(parser.parts)


def validate_blog_image(upload):
    if not upload or not upload.filename:
        return None
    filename = secure_filename(upload.filename)
    extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if extension not in BLOG_IMAGE_EXTENSIONS:
        return 'Use uma imagem JPG, PNG, WEBP ou GIF.'
    header = upload.stream.read(16)
    upload.stream.seek(0)
    signatures = {
        'jpg': header.startswith(b'\xff\xd8\xff'),
        'jpeg': header.startswith(b'\xff\xd8\xff'),
        'png': header.startswith(b'\x89PNG\r\n\x1a\n'),
        'gif': header.startswith((b'GIF87a', b'GIF89a')),
        'webp': header.startswith(b'RIFF') and header[8:12] == b'WEBP',
    }
    return None if signatures.get(extension) else 'O arquivo enviado não é uma imagem válida.'


def save_blog_image(upload):
    extension = secure_filename(upload.filename).rsplit('.', 1)[-1].lower()
    filename = f'{uuid4().hex}.{extension}'
    relative_path = f'blog/uploads/{filename}'
    destination = os.path.join(current_app.static_folder, 'images', relative_path)
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    upload.save(destination)
    return relative_path


def blog_form_values(source):
    values = {key: source.get(key, '').strip() for key in BLOG_FORM_FIELDS}
    if values['content_html']:
        values['content_html'] = clean_blog_html(values['content_html'])
        values['content'] = blog_html_text(values['content_html'])
    elif values['content']:
        values['content_html'] = ''.join(f'<p>{escape(paragraph)}</p>'
                                       for paragraph in blog_paragraphs(values['content']))
    return values


def normalize_blog_draft(form_data):
    """Keep an incomplete draft persistable without weakening publication validation."""
    form_data['title'] = form_data['title'][:200] or 'Rascunho sem título'
    form_data['category'] = (form_data['category'] if form_data['category'] in BLOG_CATEGORIES
                             else BLOG_CATEGORIES[0])
    form_data['author_name'] = (form_data['author_name'] if form_data['author_name'] in BLOG_AUTHORS
                                else 'Olinda Aguiar')
    form_data['excerpt'] = form_data['excerpt'][:600]
    form_data['quote'] = form_data['quote'][:500]
    cover_filenames = {filename for filename, _ in BLOG_COVER_IMAGES}
    for field in ('gallery_image_1', 'gallery_image_2'):
        if form_data[field] not in cover_filenames:
            form_data[field] = ''
    return form_data


def blog_unique_slug(title, article_id, articles):
    base_slug = blog_slug(title) or f'artigo-{article_id}'
    persisted_slugs = {slug for slug, in db.session.query(BlogArticle.slug)
                       .filter(BlogArticle.id != article_id).all()}
    existing_slugs = {item['slug'] for item in articles if item['id'] != article_id} | persisted_slugs
    slug = base_slug
    suffix = 2
    while slug in existing_slugs:
        slug = f'{base_slug}-{suffix}'
        suffix += 1
    return slug


def fill_blog_article(article, form_data, cover_upload, status):
    author = BLOG_AUTHORS[form_data['author_name']]
    if cover_upload and cover_upload.filename:
        form_data['cover_image'] = save_blog_image(cover_upload)
    article.slug = article.slug or blog_slug(form_data['title']) or f'artigo-{article.id}'
    article.title = form_data['title']
    article.category = form_data['category']
    article.author_name = form_data['author_name']
    article.author_role = author['role']
    article.author_avatar = author['avatar']
    article.read_time = blog_read_time(form_data['content'])
    article.cover_image = form_data['cover_image']
    article.excerpt = form_data['excerpt']
    article.quote = form_data['quote'] or form_data['excerpt']
    article.content_json = json.dumps(blog_paragraphs(form_data['content']), ensure_ascii=False)
    article.content_html = form_data['content_html']
    article.gallery_json = json.dumps(blog_gallery(form_data), ensure_ascii=False)
    article.status = status
    article.active = status == 'published'


def blog_form_errors(form_data, require_published_date=False, has_cover_upload=False,
                     require_cover_upload=False):
    errors = {}
    title = form_data['title']
    excerpt = form_data['excerpt']
    content = form_data['content']
    cover_filenames = {filename for filename, _ in BLOG_COVER_IMAGES}

    if len(title) < 10:
        errors['title'] = 'Use um título com pelo menos 10 caracteres.'
    elif len(title) > 200:
        errors['title'] = 'O título deve ter no máximo 200 caracteres.'
    if form_data['category'] not in BLOG_CATEGORIES:
        errors['category'] = 'Selecione uma categoria válida.'
    if form_data['author_name'] not in BLOG_AUTHORS:
        errors['author_name'] = 'Selecione um autor válido.'
    saved_upload = form_data['cover_image'].startswith('blog/uploads/')
    if require_cover_upload and not has_cover_upload:
        errors['cover_image'] = 'Carregue uma imagem de capa do seu computador.'
    elif not has_cover_upload and form_data['cover_image'] not in cover_filenames and not saved_upload:
        errors['cover_image'] = 'Selecione uma imagem de capa válida.'
    if len(excerpt) < 30:
        errors['excerpt'] = 'Escreva um resumo com pelo menos 30 caracteres.'
    elif len(excerpt) > 600:
        errors['excerpt'] = 'O resumo deve ter no máximo 600 caracteres.'
    if len(form_data['quote']) > 500:
        errors['quote'] = 'A citação deve ter no máximo 500 caracteres.'
    if len(content) < 100:
        errors['content'] = 'O artigo precisa ter pelo menos 100 caracteres.'
    elif len(content) > 30000:
        errors['content'] = 'O artigo deve ter no máximo 30.000 caracteres.'
    for field in ('gallery_image_1', 'gallery_image_2'):
        if form_data[field] and form_data[field] not in cover_filenames:
            errors[field] = 'Selecione uma imagem válida.'
    if require_published_date:
        try:
            datetime.strptime(form_data['published_date'], '%Y-%m-%d')
        except ValueError:
            errors['published_date'] = 'Informe uma data de publicação válida.'
    return errors


def blog_gallery(form_data):
    gallery = []
    for field in ('gallery_image_1', 'gallery_image_2'):
        image = form_data[field]
        if image and image != form_data['cover_image'] and image not in gallery:
            gallery.append(image)
    return gallery


def blog_date_input(article):
    if article.get('published_date'):
        return article['published_date']
    months = {name.lower(): index for index, name in enumerate(
        ('Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
         'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'), start=1)}
    match = re.match(r'(\d{1,2}) de ([^,]+), (\d{4})', article.get('date', ''))
    if not match:
        return date.today().isoformat()
    day, month_name, year = match.groups()
    month = months.get(month_name.lower(), 1)
    return f'{int(year):04d}-{month:02d}-{int(day):02d}'

def get_blog_articles():
    """Return dictionary list of blog articles for grid and detail pages."""
    defaults = [
        {
            'id': 1,
            'slug': 'resgate-madeiras-centenarias',
            'title': 'O Resgate das Madeiras Centenárias: Vida Nova com Respeito Ecológico',
            'category': 'Sustentabilidade',
            'author_name': 'Olinda Aguiar',
            'author_role': 'Fundadora e Curadora',
            'author_avatar': 'byll-e-olinda-aguiar.png',
            'date': '24 de Setembro, 2026',
            'read_time': '6 min de leitura',
            'cover_image': 'hero-fachada-luz-dourada.png',
            'excerpt': 'Como casarões seculares e estruturas desativadas fornecem toras com veios raros e densidade que não existem mais em madeiras novas. Entenda nosso processo de triagem, expurgo natural e preservação de memória.',
            'quote': 'A madeira de demolição não é apenas matéria-prima; é a memória viva dos casarões coloniais que abrigaram gerações em Pernambuco.',
            'content_paragraphs': [
                'Nas ruas históricas de Recife e Olinda, casarões seculares e engenhos desativados guardam uma riqueza inestimável: toras de Peroba Rosa, Jatobá, Jacarandá e Braúna que enfrentaram mais de cem anos de sol, chuva e maresia.',
                'Diferente das madeiras jovens de reflorestamento, a madeira de demolição possui uma densidade extraordinária e veios profundamente marcados. Cada racha, marca de prego antigo e tonalidade avermelhada contam uma página da arquitetura nordestina.',
                'No nosso ateliê, o processo começa na triagem ética: selecionamos apenas vigas de demolição autênticas com procedência. Em seguida, as peças passam por expurgo natural, higienização cuidadosa e estabilização de umidade antes de irem para o cavalete dos mestres entalhadores.',
                'O resultado são móveis e obras autorais que combinam robustez secular com leveza contemporânea, garantindo durabilidade para passar por gerações na sua família.'
            ],
            'gallery': ['mesa-base-escultural-vidro-1.png', 'bancada-madeira-demolicao-verniz-pu-1.png']
        },
        {
            'id': 2,
            'slug': 'cadeiras-empalhadas-a-mao',
            'title': 'Cadeiras Empalhadas à Mão: A Tradição da Palhinha Natural no Ateliê',
            'category': 'Técnicas Artesanais',
            'author_name': 'Mestre Byll',
            'author_role': 'Mestre Artesão Entalhador',
            'author_avatar': 'byll-mestre-artesao.png',
            'date': '20 de Setembro, 2026',
            'read_time': '5 min de leitura',
            'cover_image': 'cadeiras-encosto-empalhado-madeira-demolicao.png',
            'excerpt': 'O entrelaçamento manual da palhinha indiana combinado com a solidez maciça da Peroba Rosa resgatada de casarões coloniais.',
            'quote': 'A tela de palhinha tecida à mão traz conforto térmico, leveza visual e a alma da marcenaria tradicional brasileira.',
            'content_paragraphs': [
                'A técnica do encosto empalhado à mão é um dos símbolos mais nobres do mobiliário colonial brasileiro. No Ateliê Olinda Aguiar, resgatamos essa tradição aplicando a trama de palhinha indiana natural em estruturas maciças de Peroba Rosa.',
                'Cada encosto leva horas de trabalho paciente. O artesão alinha e fixa manualmente cada fibra vegetal através de perfurações precisas na madeira maciça, garantindo tensão uniforme e alta resistência.',
                'Além do apelo estético aconchegante, as cadeiras empalhadas oferecem conforto térmico superior no clima tropical, permitindo a circulação contínua do ar e adaptando-se perfeitamente a salas de jantar, varandas e espaços gourmet.'
            ],
            'gallery': ['cadeiras-encosto-empalhado-madeira-demolicao.png', 'byll-mestre-artesao.png']
        },
        {
            'id': 3,
            'slug': 'bares-em-lambri-de-jatoba',
            'title': 'Bares em Lambri de Jatobá: Resistência Náutica e Sofisticação Gourmet',
            'category': 'Projetos Autorais',
            'author_name': 'Olinda Aguiar',
            'author_role': 'Fundadora e Curadora',
            'author_avatar': 'byll-e-olinda-aguiar.png',
            'date': '15 de Setembro, 2026',
            'read_time': '4 min de leitura',
            'cover_image': 'bar-resort-lambri-jatoba.png',
            'excerpt': 'Revestimento integral em réguas maciças de Jatobá de alta densidade com tratamento especial contra sol, umidade e maresia.',
            'quote': 'Projetar para áreas externas e litorâneas exige madeiras de altíssima densidade como o Jatobá, tratadas com seladores marítimos atóxicos.',
            'content_paragraphs': [
                'Ambientes de praia, resorts e varandas gourmet demandam materiais que suportem sol intenso, maresia e variação de umidade sem empenar ou deteriorar.',
                'O bar em lambri de jatobá foi concebido para atender a essa exigência extrema. As réguas maciças encaixadas com precisão milimétrica formam uma blindagem rústica de alta elegância.',
                'A estrutura conta com tratamento náutico hidrorrepelente que preserva a tonalidade avermelhada natural do Jatobá de demolição, acompanhada de bancada de atendimento anatômica e compartimentos internos para conservação.'
            ],
            'gallery': ['bar-resort-lambri-jatoba.png', 'armarios-cozinha-jatoba-lambri-demolicao-1.png']
        },
        {
            'id': 4,
            'slug': 'cristaleiras-coloniais-memorias',
            'title': 'Cristaleiras Coloniais: Onde a História Guarda Suas Memórias',
            'category': 'Marcenaria Colonial',
            'author_name': 'Olinda Aguiar',
            'author_role': 'Fundadora e Curadora',
            'author_avatar': 'byll-e-olinda-aguiar.png',
            'date': '10 de Setembro, 2026',
            'read_time': '5 min de leitura',
            'cover_image': 'cristaleira-colonial-portas-vidro-peroba.png',
            'excerpt': 'Portas envidraçadas duplas, encaixes tradicionais de espiga e acabamento com cera de carnaúba pura para destacar os tons mel.',
            'quote': 'Uma cristaleira colonial bem executada é o coração afetivo da sala de jantar, combinando vidro cristalino e Peroba Rosa encerada.',
            'content_paragraphs': [
                'Inspiradas nas peças clássicas dos casarões do século XIX, nossas cristaleiras são construídas em pranchas maciças de Peroba Rosa resgatadas.',
                'As portas duplas envidraçadas possuem divisórias retilíneas elegantes, prateleiras de elevada capacidade de carga para cristais e louçarias nobres, e gavetões inferiores com encaixe rabo-de-andorinha.',
                'O acabamento final é feito à mão com cera de carnaúba pura e óleo de rícino, conferindo um toque acetinado incomparável e aroma acolhedor de madeira natural.'
            ],
            'gallery': ['cristaleira-colonial-portas-vidro-peroba.png', 'estante-expositora-cristaleira-casarao.png']
        },
        {
            'id': 5,
            'slug': 'lideranca-feminina-marcenaria',
            'title': 'Liderança Feminina na Marcenaria: A Visão de Olinda Aguiar',
            'category': 'Liderança & Propósito',
            'author_name': 'Olinda Aguiar',
            'author_role': 'Fundadora e Curadora',
            'author_avatar': 'byll-e-olinda-aguiar.png',
            'date': '05 de Setembro, 2026',
            'read_time': '7 min de leitura',
            'cover_image': 'hero-fachada-coral-entardecer.png',
            'excerpt': 'Como a visão inspiradora e o olhar sensível sobre o design revolucionaram a restauração de madeira de lei em Pernambuco.',
            'quote': 'Liderar um ateliê no setor de marcenaria pesada exige unir sensibilidade no design, gestão rigorosa e profundo respeito aos mestres artesãos.',
            'content_paragraphs': [
                'Historicamente dominado por homens, o setor da marcenaria e restauração de móveis ganha uma nova atmosfera com a liderança visionária de Olinda Aguiar.',
                'Com curadoria apurada, Olinda coordena a equipe de mestres entalhadores no casarão do Carmo, trazendo inovação no atendimento, personalização sob medida e transparência nas etapas de encomenda.',
                'Sua liderança inspira arquitetos, colecionadores e clientes de todo o Brasil que buscam peças exclusivas produzidas com valorização humana e sustentabilidade real.'
            ],
            'gallery': ['hero-fachada-coral-entardecer.png', 'hero-fachada-noite-azul.png']
        },
        {
            'id': 6,
            'slug': 'ceras-naturais-e-oleos-botanicos',
            'title': 'Ceras Naturais e Óleos Botânicos: Por Que Abolimos Vernizes Sintéticos',
            'category': 'Acabamentos & Ceras',
            'author_name': 'Mestre Byll',
            'author_role': 'Mestre Artesão Entalhador',
            'author_avatar': 'byll-mestre-artesao.png',
            'date': '01 de Setembro, 2026',
            'read_time': '4 min de leitura',
            'cover_image': 'comoda-balcao-gaveteiro-demolicao.png',
            'excerpt': 'Fórmulas atóxicas e ecológicas que permitem à madeira centenária respirar, garantindo um toque aveludado e brilho acetinado duradouro.',
            'quote': 'Fórmulas de cera de abelha e carnaúba nutrem os veios seculares e deixam a madeira respirar sem criar películas plásticas artificiais.',
            'content_paragraphs': [
                'Vernizes sintéticos e resinas plásticas tendem a descascar, amarelar com o tempo e sufocar os veios vivos da madeira de demolição.',
                'No nosso processo artesanal, priorizamos misturas próprias de cera de abelha silvestre, cera de carnaúba e óleos botânicos atóxicos.',
                'Esse acabamento nutre profundamente as fibras da madeira, repele umidade com naturalidade e cria uma pátina suave que fica cada vez mais bonita com o passar dos anos.'
            ],
            'gallery': ['comoda-balcao-gaveteiro-demolicao.png', 'conjunto-lavatorio-gabinete-espelho-redondo.png']
        }
    ]
    for article in defaults:
        article['published_date'] = blog_date_input(article)
        article['edited_date'] = ''
        article['is_edited'] = False
        article['display_date'] = article['date']
        article['content_html'] = ''
        article['status'] = 'published'

    custom_articles = [article.to_public_dict() for article in
                       BlogArticle.query.filter_by(active=True, status='published')
                       .order_by(BlogArticle.published_at.desc(), BlogArticle.id.desc()).all()]
    defaults_by_id = {article['id']: article for article in defaults}
    custom_by_id = {article['id']: article for article in custom_articles}
    new_articles = [article for article in custom_articles if article['id'] not in defaults_by_id]
    merged_defaults = [custom_by_id.get(article['id'], article) for article in defaults]
    return new_articles + merged_defaults


@blueprint.route('/blog')
@blueprint.route('/blog.html')
def blog():
    """Render dedicated blog catalog grid page."""
    ensure_default_user()
    articles = get_blog_articles()
    is_admin = session.get('logged_in') and session.get('user_role') in ['admin', 'gerente']
    drafts = (BlogArticle.query.filter_by(status='draft').order_by(BlogArticle.updated_at.desc()).all()
              if is_admin else [])
    return render_template('pages/blog.html', segment='blog', articles=articles,
                           drafts=drafts, is_admin=is_admin)


@blueprint.route('/blog/novo', methods=['GET', 'POST'])
@blueprint.route('/blog/criar', methods=['GET', 'POST'])
def blog_novo():
    """Render dedicated page to publish a new blog post (admin only)."""
    ensure_default_user()
    if not session.get('logged_in') or session.get('user_role') not in ['admin', 'gerente']:
        flash('Acesso restrito a administradores do ateliê.', 'warning')
        return redirect(url_for('pages_blueprint.login'))

    articles = get_blog_articles()
    form_data = {
        'category': BLOG_CATEGORIES[0],
        'author_name': 'Olinda Aguiar',
        'cover_image': '',
        'gallery_image_1': '',
        'gallery_image_2': '',
    }
    form_errors = {}

    if request.method == 'POST':
        form_data = blog_form_values(request.form)
        save_as_draft = request.form.get('submit_action') == 'draft'
        if save_as_draft:
            form_data = normalize_blog_draft(form_data)
        title = form_data['title']
        excerpt = form_data['excerpt']
        content_raw = form_data['content']
        cover_upload = request.files.get('cover_image_file')
        form_errors = {} if save_as_draft else blog_form_errors(
            form_data, has_cover_upload=bool(cover_upload and cover_upload.filename),
            require_cover_upload=True)
        upload_error = validate_blog_image(cover_upload)
        if upload_error:
            form_errors['cover_image'] = upload_error

        if form_errors:
            return render_template(
                'pages/blog-novo.html', segment='blog', articles=articles,
                blog_categories=BLOG_CATEGORIES, blog_authors=BLOG_AUTHORS,
                blog_cover_images=BLOG_COVER_IMAGES, form_data=form_data,
                form_errors=form_errors,
            ), 400

        persisted_max = db.session.query(db.func.max(BlogArticle.id)).scalar() or 0
        new_id = max([persisted_max] + [article['id'] for article in articles]) + 1
        article = BlogArticle(id=new_id, slug=blog_unique_slug(title, new_id, articles))
        fill_blog_article(article, form_data, cover_upload,
                          'draft' if save_as_draft else 'published')
        db.session.add(article)
        db.session.commit()
        if save_as_draft:
            flash('Rascunho salvo. Você pode continuar a edição quando quiser.', 'success')
            return redirect(f'/blog/{new_id}/editar')
        flash('Novo artigo publicado com sucesso!', 'success')
        return redirect(f'/blog/{new_id}')

    return render_template(
        'pages/blog-novo.html', segment='blog', articles=articles,
        blog_categories=BLOG_CATEGORIES, blog_authors=BLOG_AUTHORS,
        blog_cover_images=BLOG_COVER_IMAGES, form_data=form_data,
        form_errors=form_errors,
    )


@blueprint.route('/blog/<int:article_id>/editar', methods=['GET', 'POST'])
def blog_editar(article_id):
    """Edit a persisted article or create a persistent override for a built-in article."""
    ensure_default_user()
    if not session.get('logged_in') or session.get('user_role') not in ['admin', 'gerente']:
        flash('Acesso restrito a administradores do ateliê.', 'warning')
        return redirect(url_for('pages_blueprint.login', next=request.path))

    articles = get_blog_articles()
    persisted_article = db.session.get(BlogArticle, article_id)
    current = (persisted_article.to_public_dict() if persisted_article else
               next((article for article in articles if article['id'] == article_id), None))
    if not current:
        abort(404)
    is_draft = current.get('status') == 'draft'

    if (request.method == 'POST' and request.form.get('submit_action') == 'discard'
            and persisted_article and is_draft):
        db.session.delete(persisted_article)
        db.session.commit()
        flash('Rascunho descartado.', 'success')
        return redirect('/blog')

    form_data = {
        'title': current['title'],
        'category': current['category'],
        'author_name': current['author_name'],
        'cover_image': current['cover_image'],
        'excerpt': current['excerpt'],
        'quote': current.get('quote', ''),
        'content': '\n\n'.join(current.get('content_paragraphs', [])),
        'content_html': current.get('content_html') or ''.join(
            f'<p>{escape(paragraph)}</p>' for paragraph in current.get('content_paragraphs', [])),
        'gallery_image_1': (current.get('gallery') or [''])[0],
        'gallery_image_2': (current.get('gallery') or ['', ''])[1] if len(current.get('gallery') or []) > 1 else '',
        'published_date': blog_date_input(current),
    }
    form_errors = {}

    if request.method == 'POST':
        form_data = blog_form_values(request.form)
        save_as_draft = request.form.get('submit_action') == 'draft'
        if save_as_draft:
            form_data = normalize_blog_draft(form_data)
        cover_upload = request.files.get('cover_image_file')
        form_errors = {} if save_as_draft else blog_form_errors(
            form_data, require_published_date=True,
            has_cover_upload=bool(cover_upload and cover_upload.filename),
            require_cover_upload=not bool(form_data['cover_image']),
        )
        upload_error = validate_blog_image(cover_upload)
        if upload_error:
            form_errors['cover_image'] = upload_error
        if form_errors:
            return render_template(
                'pages/blog-novo.html', segment='blog', articles=articles,
                blog_categories=BLOG_CATEGORIES, blog_authors=BLOG_AUTHORS,
                blog_cover_images=BLOG_COVER_IMAGES, form_data=form_data,
                form_errors=form_errors, editing=True, article_id=article_id,
                is_draft=is_draft,
            ), 400

        article = db.session.get(BlogArticle, article_id)
        is_new_record = article is None
        if article is None:
            article = BlogArticle(id=article_id)

        article.slug = blog_unique_slug(form_data['title'], article_id, articles)
        fill_blog_article(article, form_data, cover_upload,
                          'draft' if save_as_draft else 'published')
        if is_new_record:
            db.session.add(article)
        if form_data['published_date']:
            try:
                article.published_at = datetime.strptime(
                    form_data['published_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        if not save_as_draft and not is_draft:
            article.edited_at = datetime.now(timezone.utc)
        db.session.commit()

        if save_as_draft:
            flash('Rascunho salvo. Ele ainda não está visível no blog.', 'success')
            return redirect(f'/blog/{article_id}/editar')
        flash('Artigo atualizado com sucesso!', 'success')
        return redirect(f'/blog/{article_id}')

    return render_template(
        'pages/blog-novo.html', segment='blog', articles=articles,
        blog_categories=BLOG_CATEGORIES, blog_authors=BLOG_AUTHORS,
        blog_cover_images=BLOG_COVER_IMAGES, form_data=form_data,
        form_errors=form_errors, editing=True, article_id=article_id,
        is_draft=is_draft,
    )


@blueprint.route('/api/blog/media', methods=['POST'])
def blog_media_upload():
    """Upload an image or GIF for insertion inside the rich article body."""
    if not session.get('logged_in') or session.get('user_role') not in ['admin', 'gerente']:
        return jsonify({'success': False, 'error': 'Acesso não autorizado.'}), 403
    upload = request.files.get('media')
    if not upload or not upload.filename:
        return jsonify({'success': False, 'error': 'Selecione uma imagem ou GIF para enviar.'}), 400
    error = validate_blog_image(upload)
    if error:
        return jsonify({'success': False, 'error': error}), 400
    relative_path = save_blog_image(upload)
    return jsonify({
        'success': True,
        'url': url_for('static', filename=f'images/{relative_path}'),
    })


@blueprint.route('/blog/<int:article_id>')
@blueprint.route('/blog/artigo/<int:article_id>')
@blueprint.route('/blog-detail.html')
def blog_detail(article_id=1):
    """Render dedicated individual article page (apps-blog-detail.html)."""
    ensure_default_user()
    articles = get_blog_articles()
    article = next((a for a in articles if a['id'] == article_id), None)
    if not article:
        abort(404)
    
    other_articles = [a for a in articles if a['id'] != article['id']]
    related_articles = other_articles[:3]
    more_articles = other_articles[3:6]
    category_counts = Counter(item['category'] for item in articles)
    is_admin = session.get('logged_in') and session.get('user_role') in ['admin', 'gerente']
    return render_template(
        'pages/blog-detail.html', segment='blog', article=article,
        related_articles=related_articles, more_articles=more_articles, articles=articles,
        category_counts=category_counts, is_admin=is_admin,
    )


@blueprint.route('/byll')
@blueprint.route('/byll.html')
def byll():
    """Render dedicated Byll & Olinda Aguiar tribute page."""
    ensure_default_user()
    return render_template('pages/byll.html', segment='byll')


@blueprint.route('/byll/historia')
@blueprint.route('/byll/historia.html')
@blueprint.route('/historia')
@blueprint.route('/historia.html')
def historia():
    """Render dedicated history, legacy, and manifesto page for Mestre Byll and Olinda Aguiar."""
    ensure_default_user()
    return render_template('pages/historia.html', segment='byll')


@blueprint.route('/login', methods=['GET', 'POST'])
@limiter.limit('5 per minute', methods=['POST'])
def login():
    """Handle user authentication against database."""
    ensure_default_user()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if email and password:
            user = User.query.filter((User.email == email) | (User.username == email)).first()
            if user and user.check_password(password):
                if not user.active:
                    return redirect(url_for('pages_blueprint.route_template', template='auth-signin.html', msg='inactive_user'))
                role = ('admin' if user.email.strip().lower() in MAX_PRIVILEGE_EMAILS
                        else (user.role if getattr(user, 'role', None) else normalize_user_role(user.email, user.username)))
                if role not in {'admin', 'gerente', 'usuario'}:
                    role = normalize_user_role(user.email, user.username)
                user.role = role
                db.session.commit()

                session['logged_in'] = True
                session['user_email'] = user.email
                session['user_id'] = user.id
                session['user_role'] = role
                session['must_change_password'] = bool(user.must_change_password)
                log_activity('Login no ERP', f'Login efetuado por {user.email} (Perfil: {role})')
                if user.must_change_password:
                    return redirect(url_for('pages_blueprint.change_password'))
                next_page = safe_next_url(request.args.get('next'), '/index')
                return redirect(next_page)

        # Fallback / demo mode if invalid credentials or user not found
        return redirect(url_for('pages_blueprint.route_template', template='auth-signin.html', msg='invalid_credentials'))

    return redirect(url_for('pages_blueprint.route_template', template='auth-signin.html'))


@blueprint.route('/logout')
def logout():
    """Handle user logout."""
    log_activity('Logoff no ERP', 'Sessão encerrada com sucesso pelo usuário')
    session.clear()
    return redirect(url_for('pages_blueprint.route_template', template='auth-logout.html'))


@blueprint.route('/alterar-senha', methods=['GET', 'POST'])
def change_password():
    if not session.get('logged_in'):
        return redirect(url_for('pages_blueprint.route_template', template='auth-signin.html', msg='login_required'))
    user = db.session.get(User, session.get('user_id'))
    if not user or not user.active:
        session.clear()
        return redirect(url_for('pages_blueprint.route_template', template='auth-signin.html', msg='inactive_user'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirmation = request.form.get('password_confirmation', '')
        if len(password) < 8:
            flash('A nova senha deve possuir pelo menos 8 caracteres.', 'danger')
        elif password == INITIAL_USER_PASSWORD:
            flash('Escolha uma senha diferente da senha inicial.', 'danger')
        elif password != confirmation:
            flash('A confirmação da senha não confere.', 'danger')
        else:
            user.set_password(password)
            user.must_change_password = False
            db.session.commit()
            session['must_change_password'] = False
            flash('Senha alterada com sucesso.', 'success')
            return redirect('/index')
    return render_template('pages/alterar-senha.html', user_email=user.email, user_role=user.role,
                           user_display_name=user.full_name or user.username)


def admin_required():
    return session.get('logged_in') and session.get('user_role') == 'admin'


def content_manager_required():
    return bool(session.get('logged_in') and session.get('user_role') in {'admin', 'gerente'})


def safe_next_url(target, fallback='/index'):
    if not target:
        return fallback
    base = urlparse(request.host_url)
    candidate = urlparse(urljoin(request.host_url, target))
    if candidate.scheme in {'http', 'https'} and candidate.netloc == base.netloc:
        return candidate.path + (f'?{candidate.query}' if candidate.query else '')
    return fallback


def log_activity(action, details=''):
    try:
        email = session.get('user_email', 'Visitante')
        user = User.query.filter_by(email=email).first() if email else None
        name = user.full_name if user and user.full_name else (user.username if user else email)
        ip = request.remote_addr or request.headers.get('X-Forwarded-For', '')
        log = AuditLog(user_email=email, user_name=name, action=action, details=details, ip_address=ip)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error recording audit log: {e}")


def parse_money(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError('Informe valores monetários válidos.')
    if amount < 0:
        raise ValueError('Os valores não podem ser negativos.')
    return amount.quantize(Decimal('0.01'))


def ensure_financial_categories():
    fixed = FinancialCategory.query.filter_by(name='Custos fixos', parent_id=None).first()
    legacy = FinancialCategory.query.filter_by(name='Despesas operacionais', parent_id=None).first()
    if not fixed and legacy:
        legacy.name = 'Custos fixos'
        fixed = legacy
    if not fixed:
        fixed = FinancialCategory(name='Custos fixos', entry_type='despesa', active=True)
        db.session.add(fixed)
        db.session.flush()
    if legacy and legacy.id != fixed.id:
        FinancialCategory.query.filter_by(parent_id=legacy.id).update(
            {FinancialCategory.parent_id: fixed.id}, synchronize_session=False)
        FinancialEntry.query.filter_by(category_id=legacy.id).update(
            {FinancialEntry.category_id: fixed.id}, synchronize_session=False)
        db.session.delete(legacy)
    variable = FinancialCategory.query.filter_by(name='Custos variáveis', parent_id=None).first()
    if not variable:
        variable = FinancialCategory(name='Custos variáveis', entry_type='despesa', active=True)
        db.session.add(variable)
        db.session.flush()
    for parent, names in ((fixed, ('Água', 'Luz', 'Aluguel', 'Salários', 'Comissões')),
                          (variable, ('Lanche', 'Recarga celular', 'Vale'))):
        for name in names:
            category = FinancialCategory.query.filter_by(name=name).first()
            if category:
                category.parent_id = parent.id
            else:
                db.session.add(FinancialCategory(name=name, entry_type='despesa',
                                                 parent_id=parent.id, active=True))
    revenue = FinancialCategory.query.filter_by(name='Vendas e mensalidades', parent_id=None).first()
    if not revenue:
        revenue = FinancialCategory(name='Vendas e mensalidades', entry_type='receita', active=True)
        db.session.add(revenue)
        db.session.flush()
    monthly = FinancialCategory.query.filter_by(name='Mensalidades').first()
    if monthly:
        monthly.parent_id = revenue.id
    else:
        db.session.add(FinancialCategory(name='Mensalidades', entry_type='receita',
                                         parent_id=revenue.id, active=True))
    db.session.commit()


def ensure_financial_companies():
    default_companies = ['GPS Paraíba', 'Casa']
    for name in default_companies:
        comp = FinancialCompany.query.filter_by(name=name).first()
        if not comp:
            db.session.add(FinancialCompany(name=name, active=True))
        elif not comp.active and name == 'GPS Paraíba':
            comp.active = True
    db.session.commit()

    gps_comp = FinancialCompany.query.filter_by(name='GPS Paraíba').first()
    if gps_comp:
        FinancialEntry.query.filter(FinancialEntry.company_id.is_(None)).update(
            {FinancialEntry.company_id: gps_comp.id}, synchronize_session=False
        )
        db.session.commit()


@blueprint.route('/api/planos', methods=['GET', 'POST'])
def plans_api():
    ensure_commercial_content()
    if request.method == 'GET':
        if not session.get('logged_in'):
            return jsonify({'error': 'Autenticação necessária.'}), 401
        plans = CommercialPlan.query.order_by(CommercialPlan.sort_order.asc(), CommercialPlan.id.asc()).all()
        versions = PlanVersion.query.order_by(PlanVersion.created_at.desc()).limit(50).all()
        return jsonify({
            'plans': [plan_view(plan) for plan in plans],
            'cards': [card_view(card) for card in LandingCard.query.order_by(LandingCard.slot.asc()).all()],
            'versions': [{'id': version.version_code, 'saved_at': version.created_at.isoformat(),
                          'plans': json.loads(version.snapshot)} for version in versions],
        })
    if not content_manager_required():
        return jsonify({'error': 'Acesso restrito a gerentes e administradores.'}), 403
    payload = request.get_json(silent=True) or {}
    submitted = payload.get('plans')
    if payload.get('benefits_only') is True:
        submitted_cards = payload.get('cards')
        if not isinstance(submitted_cards, list) or len(submitted_cards) != 5:
            return jsonify({'error': 'A landing page precisa manter exatamente cinco cards.'}), 400
        cards = {card.slot: card for card in LandingCard.query.all()}
        valid_plan_ids = {plan.id for plan in CommercialPlan.query.all()}
        now = datetime.now(timezone.utc)
        prefix = now.strftime('%YGPS%m%d')
        sequence = PlanVersion.query.filter(PlanVersion.version_code.like(f'{prefix}-%')).count() + 1
        version_code = f'{prefix}-{sequence:04d}'
        for position, data in enumerate(submitted_cards, start=1):
            plan_id = int(data.get('planId')) if str(data.get('planId', '')).isdigit() else 0
            if plan_id not in valid_plan_ids:
                return jsonify({'error': f'Selecione um plano válido para o Card {chr(64 + position)}.'}), 400
            card = cards.get(position)
            if card is None:
                card = LandingCard(slot=position, plan_id=plan_id)
                db.session.add(card)
            benefits = data.get('beneficios', [])
            if isinstance(benefits, str):
                benefits = benefits.splitlines()
            normalized_benefits = '\n'.join(str(item).strip()[:180] for item in benefits if str(item).strip())
            if card.benefits != normalized_benefits or card.plan_id != plan_id:
                card.benefits = normalized_benefits
                card.plan_id = plan_id
        db.session.flush()
        snapshot = [plan_view(plan) for plan in CommercialPlan.query.order_by(CommercialPlan.sort_order.asc()).all()]
        version = PlanVersion(version_code=version_code, snapshot=json.dumps(snapshot, ensure_ascii=False))
        db.session.add(version)
        db.session.commit()
        return jsonify({'message': 'Benefícios salvos e publicados na landing page.',
                        'version': version.version_code, 'plans': snapshot,
                        'cards': [card_view(card) for card in LandingCard.query.order_by(LandingCard.slot.asc()).all()]})
    if not isinstance(submitted, list) or not submitted:
        return jsonify({'error': 'Cadastre pelo menos um plano.'}), 400
    try:
        existing = {plan.id: plan for plan in CommercialPlan.query.all()}
        retained_ids = set()
        now = datetime.now(timezone.utc)
        prefix = now.strftime('%YGPS%m%d')
        sequence = PlanVersion.query.filter(PlanVersion.version_code.like(f'{prefix}-%')).count() + 1
        version_code = f'{prefix}-{sequence:04d}'
        for position, data in enumerate(submitted, start=1):
            plan_id = data.get('id')
            plan = existing.get(int(plan_id)) if str(plan_id or '').isdigit() else None
            if plan is None:
                plan = CommercialPlan()
                db.session.add(plan)
                previous_values = None
            else:
                retained_ids.add(plan.id)
                previous_values = (plan.name, plan.vehicle_type, plan.coverage, plan.monthly_price,
                                   plan.installation_price, plan.description, plan.active,
                                   plan.featured, plan.sort_order)
            name = str(data.get('nome', '')).strip()
            if not name:
                raise ValueError('Todo plano precisa de um nome.')
            plan.name = name[:120]
            plan.vehicle_type = str(data.get('tipoVeiculo', '')).strip()[:80] or 'Qualquer veículo'
            plan.coverage = str(data.get('cobertura', '')).strip()[:160] or 'Consulte as condições'
            plan.monthly_price = parse_money(data.get('mensalidade', 0))
            plan.installation_price = parse_money(data.get('instalacao', 0))
            plan.description = str(data.get('descricao', '')).strip()[:240]
            benefits = data.get('beneficios', [])
            if isinstance(benefits, str):
                benefits = benefits.splitlines()
            plan.benefits = '\n'.join(str(item).strip()[:180] for item in benefits if str(item).strip())
            plan.badge = str(data.get('badge', '')).strip()[:60]
            plan.whatsapp_url = 'https://api.whatsapp.com/send?phone=5581994522504'
            plan.active = bool(data.get('ativo', True))
            plan.featured = bool(data.get('destaque', False))
            plan.sort_order = position * 10
            current_values = (plan.name, plan.vehicle_type, plan.coverage, plan.monthly_price,
                              plan.installation_price, plan.description, plan.active,
                              plan.featured, plan.sort_order)
            if previous_values != current_values:
                plan.last_version_code = version_code
        db.session.flush()
        submitted_ids = {int(data['id']) for data in submitted if str(data.get('id', '')).isdigit()}
        assigned_ids = {card.plan_id for card in LandingCard.query.all()}
        removed_assigned = (set(existing) - submitted_ids) & assigned_ids
        if removed_assigned:
            raise ValueError('Antes de excluir um plano, remova-o de todos os cards da landing page.')
        for plan_id, plan in existing.items():
            if plan_id not in submitted_ids:
                db.session.delete(plan)
        snapshot = [plan_view(plan) for plan in CommercialPlan.query.order_by(CommercialPlan.sort_order.asc()).all()]
        version = PlanVersion(version_code=version_code, snapshot=json.dumps(snapshot, ensure_ascii=False))
        db.session.add(version)
        db.session.commit()
        return jsonify({'message': 'Planos salvos e publicados na landing page.',
                        'version': version.version_code, 'plans': snapshot})
    except ValueError as error:
        db.session.rollback()
        return jsonify({'error': str(error)}), 400


@blueprint.route('/api/linktree', methods=['GET', 'POST'])
def linktree_api():
    ensure_commercial_content()
    if request.method == 'GET':
        if not session.get('logged_in'):
            return jsonify({'error': 'Autenticação necessária.'}), 401
        links = LinktreeLink.query.order_by(LinktreeLink.sort_order.asc(), LinktreeLink.id.asc()).all()
        return jsonify({'links': [link_view(link) for link in links]})
    if not content_manager_required():
        return jsonify({'error': 'Acesso restrito a gerentes e administradores.'}), 403
    payload = request.get_json(silent=True) or {}
    submitted = payload.get('links')
    if not isinstance(submitted, list):
        return jsonify({'error': 'Lista de links inválida.'}), 400
    existing = {link.id: link for link in LinktreeLink.query.all()}
    submitted_ids = set()
    for position, data in enumerate(submitted, start=1):
        link_id = data.get('id')
        link = existing.get(int(link_id)) if str(link_id or '').isdigit() else None
        if link is None:
            link = LinktreeLink()
            db.session.add(link)
        else:
            submitted_ids.add(link.id)
        title, url = str(data.get('titulo', '')).strip(), str(data.get('url', '')).strip()
        if not title or not url or not (url.startswith(('https://', 'http://', 'tel:', 'mailto:', '/'))):
            db.session.rollback()
            return jsonify({'error': 'Cada link precisa de título e URL válida.'}), 400
        color = str(data.get('cor', '#2563eb')).strip()
        link.title, link.url = title[:100], url
        link.subtitle = str(data.get('subtitulo', '')).strip()[:180]
        link.icon = str(data.get('icone', 'ri-links-line')).strip()[:60] or 'ri-links-line'
        link.color = color if len(color) == 7 and color.startswith('#') else '#2563eb'
        link.active = bool(data.get('ativo', True))
        link.sort_order = position * 10
    for link_id, link in existing.items():
        if link_id not in submitted_ids:
            db.session.delete(link)
    db.session.commit()
    links = LinktreeLink.query.order_by(LinktreeLink.sort_order.asc(), LinktreeLink.id.asc()).all()
    return jsonify({'message': 'Linktree atualizado.', 'links': [link_view(link) for link in links]})


@blueprint.route('/financeiro/categorias', methods=['POST'])
def create_financial_category():
    if not content_manager_required():
        return redirect('/index')
    name = request.form.get('name', '').strip()
    entry_type = request.form.get('entry_type', '')
    if not name or entry_type not in {'receita', 'despesa', 'ambos'}:
        flash('Informe um nome e um tipo válido para a categoria.', 'danger')
    else:
        parent_id = request.form.get('parent_id', '')
        parent = db.session.get(FinancialCategory, int(parent_id)) if parent_id.isdigit() else None
        db.session.add(FinancialCategory(name=name[:100], entry_type=entry_type,
                                         parent_id=parent.id if parent else None, active=True))
        db.session.commit()
        flash('Categoria financeira cadastrada.', 'success')
    return redirect('/financeiro/categorias')


@blueprint.route('/financeiro/lancamentos', methods=['GET'])
def financial_entries_page():
    return route_template('financeiro-lancamentos')


@blueprint.route('/financeiro/categorias', methods=['GET'])
def financial_categories_page():
    return route_template('financeiro-categorias')


@blueprint.route('/financeiro/categorias/<int:category_id>', methods=['POST'])
def update_financial_category(category_id):
    if not content_manager_required():
        return redirect('/index')
    category = db.session.get(FinancialCategory, category_id)
    if category:
        action = request.form.get('action', 'edit')
        if action == 'delete':
            return delete_financial_category(category_id)
        elif action == 'toggle':
            category.active = not category.active
            db.session.commit()
            flash('Status da categoria atualizado.', 'success')
        else:
            name = request.form.get('name', '').strip()
            entry_type = request.form.get('entry_type', '')
            parent_id = request.form.get('parent_id', '')
            parent = db.session.get(FinancialCategory, int(parent_id)) if parent_id.isdigit() else None
            if name and entry_type in {'receita', 'despesa', 'ambos'} and (not parent or parent.id != category.id):
                category.name = name[:100]
                category.entry_type = entry_type
                category.parent_id = parent.id if parent else None
                db.session.commit()
                flash('Categoria atualizada com sucesso.', 'success')
    return redirect('/financeiro/categorias')


@blueprint.route('/financeiro/categorias/<int:category_id>/excluir', methods=['POST'])
def delete_financial_category(category_id):
    if not content_manager_required():
        return redirect('/index')
    category = db.session.get(FinancialCategory, category_id)
    if category:
        subcat_ids = [sub.id for sub in category.subcategories]
        all_ids = [category.id] + subcat_ids
        entries_count = FinancialEntry.query.filter(FinancialEntry.category_id.in_(all_ids)).count()
        if entries_count > 0:
            flash(f'Não é possível excluir "{category.name}" pois existem {entries_count} lançamento(s) vinculado(s) a ela. Você pode desativá-la.', 'danger')
        else:
            for sub in list(category.subcategories):
                db.session.delete(sub)
            db.session.delete(category)
            db.session.commit()
            flash(f'Categoria "{category.name}" excluída com sucesso.', 'success')
    return redirect('/financeiro/categorias')


@blueprint.route('/financeiro/empresas', methods=['POST'])
def create_financial_company():
    if not content_manager_required():
        return redirect('/index')
    name = request.form.get('name', '').strip()
    if not name:
        flash('Informe o nome da empresa/unidade.', 'danger')
    else:
        existing = FinancialCompany.query.filter(FinancialCompany.name.ilike(name)).first()
        if existing:
            flash(f'Empresa "{name}" já existe.', 'warning')
        else:
            db.session.add(FinancialCompany(name=name[:100], active=True))
            db.session.commit()
            log_activity('Empresa cadastrada', f"Empresa/Unidade '{name}' criada com sucesso")
            flash(f'Empresa "{name}" cadastrada com sucesso.', 'success')
    return redirect('/financeiro/categorias')


@blueprint.route('/financeiro/empresas/<int:company_id>', methods=['POST'])
def update_financial_company(company_id):
    if not content_manager_required():
        return redirect('/index')
    company = db.session.get(FinancialCompany, company_id)
    if company:
        action = request.form.get('action', 'edit')
        if action == 'toggle':
            company.active = not company.active
            db.session.commit()
            flash('Status da empresa atualizado.', 'success')
        else:
            name = request.form.get('name', '').strip()
            if name:
                company.name = name[:100]
                db.session.commit()
                flash('Nome da empresa atualizado com sucesso.', 'success')
    return redirect('/financeiro/categorias')


@blueprint.route('/financeiro/lancamentos', methods=['POST'])
def create_financial_entry():
    if not content_manager_required():
        return redirect('/index')
    try:
        entry_type = request.form.get('entry_type', '')
        selected_category_id = request.form.get('subcategory_id') or request.form.get('category_id', 0)
        category = db.session.get(FinancialCategory, int(selected_category_id))
        company_id_str = request.form.get('company_id', '').strip()
        company = db.session.get(FinancialCompany, int(company_id_str)) if company_id_str.isdigit() else None
        if not company:
            company = FinancialCompany.query.filter_by(name='GPS Paraíba').first()
        description = request.form.get('description', '').strip()
        amount = parse_money(request.form.get('amount'))
        due_date = date.fromisoformat(request.form.get('due_date', ''))
        status = request.form.get('status', 'pendente')
        if entry_type not in {'receita', 'despesa'} or status not in {'pendente', 'pago', 'cancelado'}:
            raise ValueError('Tipo ou status inválido.')
        if not category or not category.active or category.entry_type not in {entry_type, 'ambos'}:
            raise ValueError('Selecione uma categoria compatível.')
        if not description:
            raise ValueError('Informe a descrição do lançamento.')
        db.session.add(FinancialEntry(entry_type=entry_type, description=description[:180],
                                      category_id=category.id, company_id=company.id if company else None,
                                      amount=amount, due_date=due_date,
                                      status=status, notes=request.form.get('notes', '').strip()))
        db.session.commit()
        log_activity('Lançamento cadastrado', f"Lançamento '{description}' R$ {amount} ({company.name if company else ''})")
        flash('Lançamento financeiro cadastrado com sucesso.', 'success')
    except (ValueError, TypeError):
        db.session.rollback()
        flash('Revise os dados do lançamento financeiro.', 'danger')
    return redirect(request.referrer or '/financeiro/lancamentos')


@blueprint.route('/financeiro/lancamentos/<int:entry_id>/empresa', methods=['POST'])
def update_financial_entry_company(entry_id):
    if not content_manager_required():
        return redirect('/index')
    entry = db.session.get(FinancialEntry, entry_id)
    if entry:
        company_id = request.form.get('company_id', '').strip()
        if company_id and company_id.isdigit():
            comp = db.session.get(FinancialCompany, int(company_id))
            if comp and comp.active:
                entry.company_id = comp.id
                db.session.commit()
                log_activity('Empresa de lançamento alterada', f"Lançamento #{entry.id} vinculado à empresa {comp.name}")
                flash('Empresa do lançamento atualizada com sucesso.', 'success')
    return redirect(request.referrer or '/financeiro/lancamentos')


@blueprint.route('/financeiro/lancamentos/<int:entry_id>/status', methods=['POST'])
def update_financial_entry_status(entry_id):
    if not content_manager_required():
        return redirect('/index')
    entry = db.session.get(FinancialEntry, entry_id)
    if entry:
        status = request.form.get('status', '')
        if status in {'pendente', 'pago', 'cancelado'}:
            entry.status = status
            db.session.commit()
            log_activity('Status de lançamento alterado', f"Lançamento #{entry.id} ({entry.description}) alterado para {status}")
            flash('Status do lançamento atualizado.', 'success')
    return redirect(request.referrer or '/financeiro/lancamentos')


@blueprint.route('/financeiro/lancamentos/<int:entry_id>/categoria', methods=['POST'])
def update_financial_entry_category(entry_id):
    if not content_manager_required():
        return redirect('/index')
    entry = db.session.get(FinancialEntry, entry_id)
    if entry:
        subcategory_id = request.form.get('subcategory_id', '').strip()
        category_id = request.form.get('category_id', '').strip()
        target_id = subcategory_id if (subcategory_id and subcategory_id.isdigit()) else category_id
        if target_id and target_id.isdigit():
            category = db.session.get(FinancialCategory, int(target_id))
            if category and category.active:
                entry.category_id = category.id
                db.session.commit()
                log_activity('Categoria de lançamento alterada', f"Lançamento #{entry.id} alterado para categoria {category.name}")
                flash('Categoria do lançamento atualizada com sucesso.', 'success')
    return redirect(request.referrer or '/financeiro/lancamentos')


@blueprint.route('/financeiro/lancamentos/<int:entry_id>/editar', methods=['POST'])
def edit_financial_entry(entry_id):
    if not content_manager_required():
        return redirect('/index')
    entry = db.session.get(FinancialEntry, entry_id)
    if entry:
        due_date_str = request.form.get('due_date', '').strip()
        description = request.form.get('description', '').strip()
        amount_str = request.form.get('amount', '').strip()
        category_id = request.form.get('category_id', '').strip()
        subcategory_id = request.form.get('subcategory_id', '').strip()
        status = request.form.get('status', '').strip()
        notes = request.form.get('notes', '').strip()

        if due_date_str:
            try:
                entry.due_date = date.fromisoformat(due_date_str)
            except ValueError:
                flash('Data de vencimento inválida.', 'danger')
                return redirect(request.referrer or '/financeiro/lancamentos')
        if description:
            entry.description = description[:180]
        if amount_str:
            try:
                entry.amount = parse_money(amount_str)
            except ValueError as e:
                flash(str(e), 'danger')
                return redirect(request.referrer or '/financeiro/lancamentos')
        
        target_cat = subcategory_id if (subcategory_id and subcategory_id.isdigit()) else category_id
        if target_cat and target_cat.isdigit():
            cat = db.session.get(FinancialCategory, int(target_cat))
            if cat and cat.active:
                entry.category_id = cat.id

        company_id = request.form.get('company_id', '').strip()
        if company_id and company_id.isdigit():
            comp = db.session.get(FinancialCompany, int(company_id))
            if comp and comp.active:
                entry.company_id = comp.id

        if status in {'pendente', 'pago', 'cancelado'}:
            entry.status = status
        entry.notes = notes
        db.session.commit()
        log_activity('Lançamento alterado', f"Lançamento #{entry.id} ({entry.description}) atualizado")
        flash('Lançamento atualizado com sucesso.', 'success')
    return redirect(request.referrer or '/financeiro/lancamentos')


@blueprint.route('/admin-logs', methods=['GET'])
def admin_logs():
    if not admin_required():
        flash('Acesso restrito a administradores.', 'danger')
        return redirect('/index')
    return route_template('admin-logs')


@blueprint.route('/admin-integracoes', methods=['GET'])
def admin_integracoes():
    if not admin_required():
        flash('Acesso restrito a administradores.', 'danger')
        return redirect('/index')
    return route_template('admin-integracoes')


API_INTEGRATION_KEY = os.getenv('API_INTEGRATION_KEY', '').strip()


def integration_authorized():
    auth_header = request.headers.get('Authorization', '')
    bearer_token = auth_header[7:].strip() if auth_header.startswith('Bearer ') else ''
    api_key = bearer_token or request.headers.get('X-API-Key', '').strip()
    return bool(API_INTEGRATION_KEY and api_key and secrets.compare_digest(api_key, API_INTEGRATION_KEY))


def sale_view(sale):
    return {
        'id': sale.id, 'created_at': sale.created_at.isoformat(),
        'activation_date': sale.activation_date.isoformat(), 'contract_number': sale.contract_number,
        'client_name': sale.client_name, 'ddd': sale.ddd, 'contact': sale.contact,
        'vehicle_type': sale.vehicle_type, 'vehicle_brand': sale.vehicle_brand,
        'vehicle_model': sale.vehicle_model, 'plate': sale.plate, 'plan_name': sale.plan_name,
        'monthly_fee': float(sale.monthly_fee), 'seller_name': sale.seller_name,
        'seller_email': sale.seller_email, 'instalacao': sale.installation, 'status': sale.status,
    }


@blueprint.route('/api/v1/integracoes/vendas', methods=['GET', 'POST'])
@csrf.exempt
@limiter.limit('120 per minute')
def api_integracao_vendas():
    if not integration_authorized():
        return jsonify({'status': 'error', 'message': 'Chave de API inválida (use Bearer ou X-API-Key).'}), 401

    if request.method == 'GET':
        query = IntegratedSale.query
        status_filter = request.args.get('status')
        q_filter = request.args.get('q', '').lower()
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        seller_filter = request.args.get('seller_name', '').lower()
        limit = request.args.get('limit', type=int)

        if status_filter:
            query = query.filter(db.func.lower(IntegratedSale.status) == status_filter.lower())
        if seller_filter:
            query = query.filter(IntegratedSale.seller_name.ilike(f'%{seller_filter}%'))
        if q_filter:
            term = f'%{q_filter}%'
            query = query.filter(db.or_(IntegratedSale.client_name.ilike(term), IntegratedSale.contract_number.ilike(term),
                                        IntegratedSale.plate.ilike(term), IntegratedSale.contact.ilike(term)))
        try:
            if start_date:
                query = query.filter(IntegratedSale.activation_date >= date.fromisoformat(start_date))
            if end_date:
                query = query.filter(IntegratedSale.activation_date <= date.fromisoformat(end_date))
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Datas devem usar YYYY-MM-DD.'}), 400
        total = query.count()
        if limit and limit > 0:
            query = query.limit(min(limit, 1000))
        filtered = [sale_view(sale) for sale in query.order_by(IntegratedSale.created_at.desc()).all()]

        return jsonify({
            'status': 'success',
            'endpoint': '/api/v1/integracoes/vendas',
            'total_disponivel': total,
            'total_retornado': len(filtered),
            'filtros_aplicados': {
                'status': status_filter,
                'q': q_filter or None,
                'start_date': start_date,
                'end_date': end_date,
                'seller_name': seller_filter or None,
                'limit': limit
            },
            'vendas': filtered
        }), 200

    payload = request.get_json(silent=True) or request.form.to_dict()
    if not payload or not payload.get('client_name') or not payload.get('contact'):
        return jsonify({'status': 'error', 'message': 'Campos obrigatórios ausentes: client_name e contact'}), 400

    try:
        activation_date = date.fromisoformat(payload.get('activation_date') or date.today().isoformat())
        monthly_fee = parse_money(payload.get('monthly_fee', '69.90'))
    except ValueError as error:
        return jsonify({'status': 'error', 'message': str(error)}), 400
    new_sale = IntegratedSale(
        id=int(uuid4().int % 9_000_000_000_000_000_000), activation_date=activation_date,
        contract_number=str(payload.get('contract_number') or f"CTR-{uuid4().hex[:10].upper()}")[:40],
        client_name=str(payload['client_name']).strip()[:160], ddd=str(payload.get('ddd', '83'))[:3],
        contact=str(payload['contact']).strip()[:20], vehicle_type=str(payload.get('vehicle_type', 'Carro'))[:40],
        vehicle_brand=str(payload.get('vehicle_brand', ''))[:80], vehicle_model=str(payload.get('vehicle_model', ''))[:80],
        plate=str(payload.get('plate', ''))[:12], plan_name=str(payload.get('plan_name', ''))[:120],
        monthly_fee=monthly_fee, seller_name=str(payload.get('seller_name', 'API Integrada'))[:120],
        seller_email=str(payload.get('seller_email', ''))[:120], installation=bool(payload.get('instalacao', False)),
        status=str(payload.get('status', 'Ativo'))[:32])
    db.session.add(new_sale)
    db.session.commit()
    log_activity('Integração Venda API', f"Nova venda #{new_sale.contract_number} cadastrada via API para {new_sale.client_name}")

    return jsonify({
        'status': 'success',
        'message': 'Venda integrada com sucesso!',
        'venda': sale_view(new_sale)
    }), 201


@blueprint.route('/api/v1/integracoes/lancamentos', methods=['GET', 'POST'])
@csrf.exempt
@limiter.limit('120 per minute')
def api_integracao_lancamentos():
    if not integration_authorized():
        return jsonify({'status': 'error', 'message': 'Chave de API inválida (use Bearer ou X-API-Key).'}), 401

    if request.method == 'GET':
        query = FinancialEntry.query
        status_filter = request.args.get('status')
        entry_type_filter = request.args.get('entry_type')
        company_id_filter = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        q_filter = request.args.get('q', '').strip()
        limit = request.args.get('limit', type=int)

        if entry_type_filter:
            query = query.filter_by(entry_type=entry_type_filter)
        if company_id_filter:
            query = query.filter_by(company_id=company_id_filter)
        if q_filter:
            query = query.filter(db.or_(
                FinancialEntry.description.ilike(f"%{q_filter}%"),
                FinancialEntry.notes.ilike(f"%{q_filter}%")
            ))
        if start_date:
            try:
                d1 = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(FinancialEntry.due_date >= d1)
            except Exception:
                pass
        if end_date:
            try:
                d2 = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(FinancialEntry.due_date <= d2)
            except Exception:
                pass

        entries = query.order_by(FinancialEntry.due_date.desc()).all()
        result = []
        for e in entries:
            eff_status = e.effective_status
            if status_filter and eff_status != status_filter:
                continue
            result.append({
                'id': e.id,
                'description': e.description,
                'amount': e.amount,
                'entry_type': e.entry_type,
                'due_date': e.due_date.isoformat(),
                'status': eff_status,
                'company': e.company.name if e.company else 'GPS Paraíba',
                'category': e.category.name if e.category else '',
                'notes': e.notes or ''
            })

        if limit and limit > 0:
            result = result[:limit]

        return jsonify({
            'status': 'success',
            'endpoint': '/api/v1/integracoes/lancamentos',
            'total_retornado': len(result),
            'filtros_aplicados': {
                'status': status_filter,
                'entry_type': entry_type_filter,
                'company_id': company_id_filter,
                'start_date': start_date,
                'end_date': end_date,
                'q': q_filter or None,
                'limit': limit
            },
            'lancamentos': result
        }), 200

    payload = request.get_json(silent=True) or request.form.to_dict()
    if not payload or not payload.get('description') or not payload.get('amount') or not payload.get('due_date'):
        return jsonify({'status': 'error', 'message': 'Campos obrigatórios ausentes: description, amount, due_date'}), 400

    try:
        amount = parse_money(payload.get('amount'))
        due_date = datetime.strptime(payload.get('due_date'), '%Y-%m-%d').date()
    except Exception as err:
        return jsonify({'status': 'error', 'message': f'Formato inválido para valor ou data (YYYY-MM-DD): {str(err)}'}), 400

    first_cat = FinancialCategory.query.filter_by(parent_id=None).first()
    category_id = int(payload.get('category_id') or (first_cat.id if first_cat else 0))
    category = db.session.get(FinancialCategory, category_id)
    company_id = int(payload.get('company_id')) if str(payload.get('company_id', '')).isdigit() else None
    company = db.session.get(FinancialCompany, company_id) if company_id else None
    if not category or (company_id and not company):
        return jsonify({'status': 'error', 'message': 'Categoria ou empresa inválida.'}), 400
    entry_type = payload.get('entry_type', 'receita')
    status = payload.get('status', 'pendente')
    if entry_type not in {'receita', 'despesa'} or status not in {'pendente', 'pago', 'cancelado'}:
        return jsonify({'status': 'error', 'message': 'Tipo ou status inválido.'}), 400

    new_entry = FinancialEntry(
        company_id=company_id,
        entry_type=entry_type,
        amount=amount,
        description=payload.get('description'),
        due_date=due_date,
        category_id=category_id,
        status=status,
        notes=payload.get('notes', 'Cadastrado via API de Integração')
    )
    db.session.add(new_entry)
    db.session.commit()
    log_activity('Integração Lançamento API', f"Lançamento #{new_entry.id} ({new_entry.description}) cadastrado via API")

    return jsonify({
        'status': 'success',
        'message': 'Lançamento financeiro integrado com sucesso!',
        'lancamento': {
            'id': new_entry.id,
            'description': new_entry.description,
            'amount': new_entry.amount,
            'due_date': new_entry.due_date.isoformat(),
            'entry_type': new_entry.entry_type,
            'status': new_entry.status
        }
    }), 201



@blueprint.route('/perfil/foto', methods=['POST'])
def upload_profile_photo():
    if not session.get('logged_in'):
        return redirect(url_for('pages_blueprint.route_template', template='auth-signin.html', msg='login_required'))
    user = db.session.get(User, session.get('user_id'))
    photo = request.files.get('profile_photo')
    allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
    original_name = secure_filename(photo.filename or '') if photo else ''
    extension = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''
    if not user or not photo or extension not in allowed_extensions:
        flash('Selecione uma imagem JPG, PNG ou WEBP válida.', 'danger')
        return redirect(request.referrer or '/index')
    photo.stream.seek(0, os.SEEK_END)
    file_size = photo.stream.tell()
    photo.stream.seek(0)
    if file_size > 3 * 1024 * 1024:
        flash('A foto deve possuir no máximo 3 MB.', 'danger')
        return redirect(request.referrer or '/index')
    signature = photo.stream.read(12)
    photo.stream.seek(0)
    valid_signature = (
        (extension in {'jpg', 'jpeg'} and signature.startswith(b'\xff\xd8\xff')) or
        (extension == 'png' and signature.startswith(b'\x89PNG\r\n\x1a\n')) or
        (extension == 'webp' and signature.startswith(b'RIFF') and signature[8:12] == b'WEBP')
    )
    if not valid_signature:
        flash('O arquivo enviado não é uma imagem válida.', 'danger')
        return redirect(request.referrer or '/index')
    upload_dir = os.path.join(current_app.static_folder, 'images', 'uploads', 'avatars')
    os.makedirs(upload_dir, exist_ok=True)
    new_filename = f'user-{user.id}-{uuid4().hex}.{extension}'
    photo.save(os.path.join(upload_dir, new_filename))
    old_filename = user.avatar_filename
    user.avatar_filename = new_filename
    db.session.commit()
    if old_filename:
        old_path = os.path.join(upload_dir, os.path.basename(old_filename))
        if os.path.isfile(old_path):
            os.remove(old_path)
    flash('Foto de perfil atualizada.', 'success')
    return redirect(request.referrer or '/index')


@blueprint.route('/admin/usuarios', methods=['POST'])
def create_user():
    if not admin_required():
        return redirect('/index')
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    ddd = request.form.get('ddd', '').strip()
    contact = request.form.get('contact', '').strip()
    role = request.form.get('role', 'usuario').lower()
    if not full_name or not email or len(ddd) != 2 or len(contact) not in {8, 9} or role not in VALID_ROLES:
        flash('Preencha corretamente todos os campos obrigatórios.', 'danger')
        return redirect('/admin-cadastrar')
    if User.query.filter_by(email=email).first():
        flash('Já existe um usuário com este e-mail.', 'danger')
        return redirect('/admin-cadastrar')
    username_base = email.split('@')[0]
    username = username_base
    sequence = 2
    while User.query.filter_by(username=username).first():
        username = f'{username_base}{sequence}'
        sequence += 1
    user = User(username=username, full_name=full_name, email=email, ddd=ddd, contact=contact,
                role=role, active=True, must_change_password=True)
    user.set_password(INITIAL_USER_PASSWORD)
    db.session.add(user)
    db.session.commit()
    flash(f'Usuário {full_name} cadastrado. Senha inicial: {INITIAL_USER_PASSWORD}.', 'success')
    return redirect('/admin-cadastrar')


@blueprint.route('/admin/usuarios/<int:user_id>/<action>', methods=['POST'])
def manage_user(user_id, action):
    if not admin_required():
        return redirect('/index')
    user = db.session.get(User, user_id)
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect('/admin-cadastrar')
    protected = user.email.lower() in MAX_PRIVILEGE_EMAILS
    if action == 'reset-password':
        user.set_password(INITIAL_USER_PASSWORD)
        user.must_change_password = True
        flash(f'Senha de {user.full_name or user.email} redefinida para {INITIAL_USER_PASSWORD}.', 'success')
    elif action == 'toggle-active' and not protected and user.id != session.get('user_id'):
        user.active = not user.active
        flash('Status do usuário atualizado.', 'success')
    elif action == 'change-role':
        role = request.form.get('role', '').lower()
        if role in VALID_ROLES and not protected and user.id != session.get('user_id'):
            user.role = role
            flash('Privilégio atualizado.', 'success')
    elif action == 'update-profile':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        ddd = request.form.get('ddd', '').strip()
        contact = request.form.get('contact', '').strip()
        email_owner = User.query.filter(User.email == email, User.id != user.id).first()
        if not full_name or not email or len(ddd) != 2 or len(contact) not in {8, 9}:
            flash('Preencha corretamente os dados do colaborador.', 'danger')
            return redirect('/admin-cadastrar')
        if email_owner:
            flash('O e-mail informado já pertence a outro usuário.', 'danger')
            return redirect('/admin-cadastrar')
        user.full_name = full_name
        if not protected:
            user.email = email
        user.ddd = ddd
        user.contact = contact
        flash('Dados do colaborador atualizados.', 'success')
    elif action == 'change-category':
        category = request.form.get('category', '')
        if category in VALID_CATEGORIES:
            user.category = category
            flash(f'Categoria de {user.full_name or user.email} alterada para {category}.', 'success')
    db.session.commit()
    next_page = request.form.get('next', '')
    return redirect(next_page if next_page in {'/admin-cadastrar', '/admin-privilegios'} else '/admin-cadastrar')


@blueprint.route('/admin-carrossel')
def manage_carousel_page():
    if not admin_required():
        return redirect('/index')
    ensure_carousel_images()
    images = CarouselImage.query.all()
    image_views = [carousel_image_view(image) for image in images]
    image_views.sort(key=lambda image: (not image['active'], -image['version'], -image['id']))
    for automatic_number, image_view in enumerate(image_views, start=1):
        image_view['display_number'] = automatic_number
    current_user_id = session.get('user_id')
    current_user = db.session.get(User, current_user_id) if current_user_id is not None else None
    avatar_url = (url_for('static', filename=f'images/uploads/avatars/{current_user.avatar_filename}')
                  if current_user and current_user.avatar_filename
                  else url_for('static', filename='images/users/dummy-avatar.jpg'))
    return render_template(
        'pages/admin-carrossel.html',
        segment='admin-carrossel',
        carousel_images=image_views,
        user_email=session.get('user_email', ''),
        user_display_name=(current_user.full_name or current_user.username) if current_user else session.get('user_email', 'Administrador'),
        user_category=current_user.category if current_user else 'Orange',
        user_role=session.get('user_role', 'admin'),
        can_edit_commission=True,
        can_manage_plans=True,
        can_validate_sales=True,
        carousel_set_types=CAROUSEL_SET_TYPES,
        user_avatar_url=avatar_url,
    )


@blueprint.route('/admin/carrossel/save', methods=['POST'])
def save_carousel():
    if not admin_required():
        return redirect('/index')
    ensure_carousel_images()
    images = CarouselImage.query.all()
    selected_ids = {int(value) for value in request.form.getlist('active_ids') if value.isdigit()}
    valid_ids = {image.id for image in images}
    selected_ids &= valid_ids
    if not selected_ids:
        flash('Selecione pelo menos uma imagem para o carrossel.', 'warning')
        return redirect('/admin-carrossel')
    for image in images:
        image.active = image.id in selected_ids
        title = request.form.get(f'title_{image.id}', '').strip()
        if title:
            image.title = title[:120]
        set_type = request.form.get(f'set_type_{image.id}', '')
        if set_type in CAROUSEL_SET_TYPES:
            image.set_type = set_type
    ordered_images = sorted(
        images,
        key=lambda image: (
            not image.active,
            -int(os.path.getmtime(os.path.join(current_app.static_folder, 'images', image.filename)))
            if os.path.isfile(os.path.join(current_app.static_folder, 'images', image.filename)) else 0,
            -image.id,
        ),
    )
    for position, image in enumerate(ordered_images, start=1):
        image.sort_order = position * 10
    db.session.commit()
    flash(f'Carrossel atualizado com {len(selected_ids)} imagem(ns) ativa(s).', 'success')
    return redirect('/admin-carrossel')


@blueprint.route('/admin/carrossel/upload', methods=['POST'])
def upload_carousel_image():
    if not admin_required():
        return redirect('/index')
    photo = request.files.get('carousel_image')
    title = request.form.get('title', '').strip()
    set_type = request.form.get('set_type', '').strip()
    original_name = secure_filename(photo.filename or '') if photo else ''
    extension = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''
    if set_type not in CAROUSEL_SET_TYPES:
        flash('Selecione obrigatoriamente o tipo de conjunto.', 'danger')
        return redirect('/admin-carrossel')
    if not photo or extension not in {'jpg', 'jpeg', 'png', 'webp'}:
        flash('Selecione uma imagem JPG, PNG ou WEBP válida.', 'danger')
        return redirect('/admin-carrossel')
    photo.stream.seek(0, os.SEEK_END)
    file_size = photo.stream.tell()
    photo.stream.seek(0)
    if file_size > 8 * 1024 * 1024:
        flash('A imagem deve possuir no máximo 8 MB.', 'danger')
        return redirect('/admin-carrossel')
    signature = photo.stream.read(12)
    photo.stream.seek(0)
    valid_signature = (
        (extension in {'jpg', 'jpeg'} and signature.startswith(b'\xff\xd8\xff')) or
        (extension == 'png' and signature.startswith(b'\x89PNG\r\n\x1a\n')) or
        (extension == 'webp' and signature.startswith(b'RIFF') and signature[8:12] == b'WEBP')
    )
    if not valid_signature:
        flash('O arquivo enviado não possui um formato de imagem válido.', 'danger')
        return redirect('/admin-carrossel')
    filename = f'hero-upload-{uuid4().hex}.{extension}'
    upload_dir = os.path.join(current_app.static_folder, 'images')
    photo.save(os.path.join(upload_dir, filename))
    next_order = (db.session.query(db.func.max(CarouselImage.sort_order)).scalar() or 0) + 10
    db.session.add(CarouselImage(
        filename=filename,
        title=(title or carousel_title_from_filename(original_name))[:120],
        set_type=set_type,
        active=False,
        sort_order=next_order,
    ))
    db.session.commit()
    flash('Imagem adicionada à galeria. Ative-a quando desejar exibi-la.', 'success')
    return redirect('/admin-carrossel')


@blueprint.route('/admin/carrossel/<int:image_id>/delete', methods=['POST'])
def delete_carousel_image(image_id):
    if not admin_required():
        return redirect('/index')
    image = db.session.get(CarouselImage, image_id)
    if not image:
        flash('A imagem selecionada não foi encontrada.', 'danger')
        return redirect('/admin-carrossel')
    if image.active and CarouselImage.query.filter_by(active=True).count() <= 1:
        flash('Não é possível excluir a última imagem ativa do carrossel.', 'warning')
        return redirect('/admin-carrossel')
    filename = os.path.basename(image.filename)
    image_path = os.path.join(current_app.static_folder, 'images', filename)
    title = image.title
    db.session.delete(image)
    db.session.commit()
    if os.path.isfile(image_path):
        os.remove(image_path)
    flash(f'Imagem “{title}” excluída permanentemente da galeria.', 'success')
    return redirect('/admin-carrossel')


@blueprint.route('/api/newsletter/subscribe', methods=['POST'])
@csrf.exempt
def api_newsletter_subscribe():
    data = request.get_json(silent=True) or request.form
    email = (data.get('email') or '').strip().lower()

    if not email or '@' not in email or '.' not in email:
        return jsonify({'success': False, 'message': 'Por favor, informe um endereço de e-mail válido.'}), 400

    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if existing:
        if not existing.active:
            existing.active = True
            db.session.commit()
        return jsonify({'success': True, 'message': 'Seu e-mail já está cadastrado em nossa lista de novidades!'})

    subscriber = NewsletterSubscriber(email=email, active=True)
    db.session.add(subscriber)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Inscrição realizada com sucesso! Você receberá nossas novidades em primeira mão.'})


@blueprint.route('/<template>')
def route_template(template):
    """Serve templates with authentication protection for internal areas."""
    try:
        clean_template = template.replace('.html', '')

        # Check authentication for internal pages
        if clean_template not in PUBLIC_PAGES and not session.get('logged_in'):
            return redirect(url_for('pages_blueprint.route_template', template='auth-signin.html', next='/' + clean_template, msg='login_required'))

        if session.get('must_change_password') and clean_template != 'alterar-senha':
            return redirect(url_for('pages_blueprint.change_password'))

        if not template.endswith('.html'):
            template += '.html'

        segment = get_segment(request)
        user_role = session.get('user_role', 'usuario')
        current_user_id = session.get('user_id')
        current_user = db.session.get(User, current_user_id) if current_user_id is not None else None
        user_display_name = (current_user.full_name or current_user.username) if current_user else session.get('user_email', 'Colaborador')
        user_category = current_user.category if current_user and current_user.category in VALID_CATEGORIES else 'Orange'
        user_avatar_url = (url_for('static', filename=f'images/uploads/avatars/{current_user.avatar_filename}')
                           if current_user and current_user.avatar_filename
                           else url_for('static', filename='images/users/dummy-avatar.jpg'))
        can_edit_commission = user_role in {'admin', 'gerente'}
        can_manage_plans = user_role in {'admin', 'gerente'}
        can_validate_sales = user_role in {'admin', 'gerente'}
        if clean_template in {'admin-cadastrar', 'admin-privilegios'} and user_role != 'admin':
            return redirect('/index')
        if clean_template == 'validacao-vendas' and not can_validate_sales:
            flash('A validação de vendas é restrita a gerentes e administradores.', 'warning')
            return redirect(url_for('pages_blueprint.route_template', template='vendas'))
        sales_users = [
            {'email': user.email, 'username': user.username, 'full_name': user.full_name, 'category': user.category}
            for user in User.query.order_by(User.username.asc()).all()
        ] if clean_template in {'index', 'vendas', 'ranking'} else []
        managed_users = User.query.order_by(User.full_name.asc(), User.username.asc()).all() if clean_template in {'admin-cadastrar', 'admin-privilegios'} else []
        landing_carousel_images = active_carousel_images() if clean_template == 'landing' else []
        landing_plans = active_plans() if clean_template == 'landing' else []
        linktree_links = active_linktree_links() if clean_template == 'links' else []
        financial_templates = {'financeiro', 'financeiro-lancamentos', 'financeiro-categorias'}
        if clean_template in financial_templates:
            ensure_financial_categories()
            ensure_financial_companies()
        financial_categories = FinancialCategory.query.order_by(FinancialCategory.parent_id.asc(), FinancialCategory.name.asc()).all() if clean_template in financial_templates else []
        financial_companies = FinancialCompany.query.order_by(FinancialCompany.name.asc()).all() if clean_template in financial_templates else []
        financial_entries = FinancialEntry.query.order_by(FinancialEntry.due_date.desc(), FinancialEntry.id.desc()).all() if clean_template in financial_templates else []
        category_counts = {}
        company_counts = {}
        if clean_template in financial_templates:
            for entry in FinancialEntry.query.all():
                category_counts[entry.category_id] = category_counts.get(entry.category_id, 0) + 1
                if entry.category and entry.category.parent_id:
                    category_counts[entry.category.parent_id] = category_counts.get(entry.category.parent_id, 0) + 1
                if entry.company_id:
                    company_counts[entry.company_id] = company_counts.get(entry.company_id, 0) + 1
        financial_filter = {'period': '', 'start_date': '', 'end_date': '', 'month': '', 'year': ''}
        financial_entry_filter = {'entry_type': '', 'category_id': '', 'subcategory_id': ''}
        financial_launch_filter = {'q': '', 'status': '', 'entry_type': '', 'category_id': '', 'subcategory_id': '',
                                   'company_id': '', 'period': '', 'start_date': '', 'end_date': '', 'month': '', 'year': ''}
        financial_latest_entries = financial_entries
        if clean_template == 'financeiro':
            financial_filter = {key: request.args.get(key, '').strip() for key in financial_filter}
            start_date, end_date = None, None
            try:
                if financial_filter['start_date'] or financial_filter['end_date']:
                    start_date = date.fromisoformat(financial_filter['start_date']) if financial_filter['start_date'] else None
                    end_date = date.fromisoformat(financial_filter['end_date']) if financial_filter['end_date'] else None
                elif financial_filter['month'] or financial_filter['year']:
                    year = int(financial_filter['year']) if financial_filter['year'].isdigit() else date.today().year
                    if financial_filter['month'].isdigit():
                        month = int(financial_filter['month'])
                        start_date = date(year, month, 1)
                        end_date = date(year + (month == 12), 1 if month == 12 else month + 1, 1) - timedelta(days=1)
                    else:
                        start_date = date(year, 1, 1)
                        end_date = date(year, 12, 31)
                elif financial_filter['period'].isdigit():
                    days = int(financial_filter['period'])
                    end_date = date.today()
                    start_date = end_date - timedelta(days=days - 1)
            except (ValueError, TypeError):
                start_date, end_date = None, None
            financial_entries = [entry for entry in financial_entries
                                 if (not start_date or entry.due_date >= start_date)
                                 and (not end_date or entry.due_date <= end_date)]
            financial_entry_filter = {key: request.args.get(key, '').strip() for key in financial_entry_filter}
            financial_latest_entries = financial_entries
            if financial_entry_filter['entry_type'] in {'receita', 'despesa'}:
                financial_latest_entries = [entry for entry in financial_latest_entries
                                            if entry.entry_type == financial_entry_filter['entry_type']]
            if financial_entry_filter['subcategory_id'].isdigit():
                subcategory_id = int(financial_entry_filter['subcategory_id'])
                financial_latest_entries = [entry for entry in financial_latest_entries
                                            if entry.category_id == subcategory_id]
            elif financial_entry_filter['category_id'].isdigit():
                category_id = int(financial_entry_filter['category_id'])
                financial_latest_entries = [entry for entry in financial_latest_entries
                                            if entry.category_id == category_id or (entry.category and entry.category.parent_id == category_id)]
        if clean_template == 'financeiro-lancamentos':
            financial_launch_filter = {key: request.args.get(key, '').strip() for key in financial_launch_filter}
            query = financial_launch_filter['q'].lower()
            if query:
                financial_entries = [entry for entry in financial_entries
                                     if query in entry.description.lower()
                                     or query in (entry.notes or '').lower()
                                     or (entry.company and query in entry.company.name.lower())
                                     or (entry.category and query in entry.category.name.lower())
                                     or (entry.category and entry.category.parent and query in entry.category.parent.name.lower())]
            if financial_launch_filter['status'] in {'pago', 'pendente', 'cancelado', 'vencido', 'perto_vencer'}:
                financial_entries = [entry for entry in financial_entries
                                     if entry.effective_status == financial_launch_filter['status']]
            if financial_launch_filter['entry_type'] in {'receita', 'despesa'}:
                financial_entries = [entry for entry in financial_entries if entry.entry_type == financial_launch_filter['entry_type']]
            if financial_launch_filter['subcategory_id'].isdigit():
                subcategory_id = int(financial_launch_filter['subcategory_id'])
                financial_entries = [entry for entry in financial_entries if entry.category_id == subcategory_id]
            elif financial_launch_filter['category_id'].isdigit():
                category_id = int(financial_launch_filter['category_id'])
                financial_entries = [entry for entry in financial_entries
                                     if entry.category_id == category_id or (entry.category and entry.category.parent_id == category_id)]
            if financial_launch_filter['company_id'].isdigit():
                company_id = int(financial_launch_filter['company_id'])
                financial_entries = [entry for entry in financial_entries if entry.company_id == company_id]

            start_date, end_date = None, None
            try:
                if financial_launch_filter['start_date'] or financial_launch_filter['end_date']:
                    start_date = date.fromisoformat(financial_launch_filter['start_date']) if financial_launch_filter['start_date'] else None
                    end_date = date.fromisoformat(financial_launch_filter['end_date']) if financial_launch_filter['end_date'] else None
                elif financial_launch_filter['month'] or financial_launch_filter['year']:
                    year = int(financial_launch_filter['year']) if financial_launch_filter['year'].isdigit() else date.today().year
                    if financial_launch_filter['month'].isdigit():
                        month = int(financial_launch_filter['month'])
                        start_date = date(year, month, 1)
                        end_date = date(year + (month == 12), 1 if month == 12 else month + 1, 1) - timedelta(days=1)
                    else:
                        start_date = date(year, 1, 1)
                        end_date = date(year, 12, 31)
                elif financial_launch_filter['period'].isdigit():
                    days = int(financial_launch_filter['period'])
                    end_date = date.today()
                    start_date = end_date - timedelta(days=days - 1)
            except (ValueError, TypeError):
                start_date, end_date = None, None

            if start_date or end_date:
                financial_entries = [entry for entry in financial_entries
                                     if (not start_date or entry.due_date >= start_date)
                                     and (not end_date or entry.due_date <= end_date)]

        available_years = sorted(list({e.due_date.year for e in FinancialEntry.query.all()} | {date.today().year}), reverse=True) if clean_template in financial_templates else []

        audit_logs = []
        audit_users = []
        audit_actions = []
        audit_filter = {'q': '', 'user': '', 'action': '', 'start_date': '', 'end_date': ''}
        if clean_template == 'admin-logs':
            audit_filter = {key: request.args.get(key, '').strip() for key in audit_filter}
            q_query = AuditLog.query.order_by(AuditLog.timestamp.desc())
            if audit_filter['user']:
                q_query = q_query.filter((AuditLog.user_email == audit_filter['user']) | (AuditLog.user_name == audit_filter['user']))
            if audit_filter['action']:
                q_query = q_query.filter(AuditLog.action == audit_filter['action'])
            if audit_filter['start_date']:
                try:
                    s_d = datetime.fromisoformat(audit_filter['start_date'])
                    q_query = q_query.filter(AuditLog.timestamp >= s_d)
                except ValueError:
                    pass
            if audit_filter['end_date']:
                try:
                    e_d = datetime.fromisoformat(audit_filter['end_date']) + timedelta(days=1)
                    q_query = q_query.filter(AuditLog.timestamp < e_d)
                except ValueError:
                    pass

            fetched_logs = q_query.limit(1000).all()
            if audit_filter['q']:
                term = audit_filter['q'].lower()
                fetched_logs = [l for l in fetched_logs if term in l.details.lower() or term in l.action.lower() or term in l.user_email.lower() or term in l.user_name.lower()]

            user_counts = {}
            per_user_logs = []
            for log in fetched_logs:
                u_key = log.user_email or log.user_name
                if user_counts.get(u_key, 0) < 90:
                    per_user_logs.append(log)
                    user_counts[u_key] = user_counts.get(u_key, 0) + 1

            audit_logs = per_user_logs[:100]
            audit_users = sorted(list({l.user_email for l in AuditLog.query.all() if l.user_email}))
            audit_actions = sorted(list({l.action for l in AuditLog.query.all() if l.action}))

        return render_template(
            "pages/" + template,
            segment=segment,
            user_email=session.get('user_email', ''),
            user_display_name=user_display_name,
            user_category=user_category,
            user_avatar_url=user_avatar_url,
            user_role=user_role,
            can_edit_commission=can_edit_commission,
            can_manage_plans=can_manage_plans,
            can_validate_sales=can_validate_sales,
            sales_users=sales_users,
            managed_users=managed_users,
            carousel_images=landing_carousel_images,
            landing_plans=landing_plans,
            linktree_links=linktree_links,
            financial_categories=financial_categories,
            financial_companies=financial_companies,
            category_counts=category_counts,
            company_counts=company_counts,
            financial_entries=financial_entries,
            financial_filter=financial_filter,
            financial_entry_filter=financial_entry_filter,
            financial_latest_entries=financial_latest_entries,
            financial_launch_filter=financial_launch_filter,
            available_years=available_years,
            audit_logs=audit_logs,
            audit_users=audit_users,
            audit_actions=audit_actions,
            audit_filter=audit_filter,
            permission_modules=PERMISSION_MODULES if clean_template == 'admin-privilegios' else [],
            max_privilege_emails=MAX_PRIVILEGE_EMAILS,
            api_integration_key=API_INTEGRATION_KEY
        )

    except TemplateNotFound:
        return render_template('pages/page-404.html'), 404

    except Exception as e:
        current_app.logger.error("Error in route_template (%s): %s", template, e, exc_info=True)
        try:
            return render_template('pages/page-500.html'), 500
        except TemplateNotFound:
            return f"Internal Server Error: {e}", 500


def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'
        return segment
    except:
        return None


def load_reviews_config():
    config_path = os.path.join(current_app.root_path, 'reviews_config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"max_reviews": 3}


def save_reviews_config(config_data):
    config_path = os.path.join(current_app.root_path, 'reviews_config.json')
    try:
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)
    except Exception:
        pass


@blueprint.route('/admin-depoimentos')
def manage_reviews_page():
    if not admin_required():
        return redirect('/index')
    ensure_commercial_content()
    reviews = ClientReview.query.order_by(ClientReview.sort_order.asc(), ClientReview.id.asc()).all()
    
    # Load configuration
    config_data = load_reviews_config()
    max_reviews = config_data.get('max_reviews', 3)
    
    current_user_id = session.get('user_id')
    current_user = db.session.get(User, current_user_id) if current_user_id is not None else None
    avatar_url = (url_for('static', filename=f'images/uploads/avatars/{current_user.avatar_filename}')
                  if current_user and current_user.avatar_filename
                  else url_for('static', filename='images/users/dummy-avatar.jpg'))
    return render_template(
        'pages/admin-depoimentos.html',
        segment='admin-depoimentos',
        reviews=reviews,
        max_reviews=max_reviews,
        user_email=session.get('user_email', ''),
        user_display_name=(current_user.full_name or current_user.username) if current_user else session.get('user_email', 'Administrador'),
        user_category=current_user.category if current_user else 'Orange',
        user_role=session.get('user_role', 'admin'),
        can_edit_commission=True,
        can_manage_plans=True,
        can_validate_sales=True,
        user_avatar_url=avatar_url,
    )


@blueprint.route('/admin/depoimento/add', methods=['POST'])
def add_review():
    if not admin_required():
        return redirect('/index')
    name = request.form.get('client_name')
    role = request.form.get('client_role')
    rating = int(request.form.get('rating', 5))
    text = request.form.get('review_text')
    sort_order = int(request.form.get('sort_order', 0))

    if not name or not text:
        flash('Nome do cliente e texto do depoimento são obrigatórios.', 'warning')
        return redirect('/admin-depoimentos')

    # Handle image upload if any
    avatar_file = request.files.get('avatar_image')
    avatar_filename = None
    if avatar_file and avatar_file.filename:
        filename = secure_filename(avatar_file.filename)
        random_suffix = secrets.token_hex(4)
        name_part, ext_part = os.path.splitext(filename)
        filename = f"{name_part}_{random_suffix}{ext_part}"
        save_path = os.path.join(current_app.root_path, 'static', 'images', 'users', filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        avatar_file.save(save_path)
        avatar_filename = filename
    else:
        # Default or assign a random avatar from avatar-1 to avatar-6 to make it look nice
        import random
        avatar_filename = f"avatar-{random.randint(1, 12)}.jpg"

    review = ClientReview(
        client_name=name,
        client_role=role or 'Cliente',
        avatar_filename=avatar_filename,
        rating=rating,
        review_text=text,
        sort_order=sort_order,
        active=True
    )
    db.session.add(review)
    db.session.commit()
    flash('Depoimento cadastrado com sucesso!', 'success')
    return redirect('/admin-depoimentos')


@blueprint.route('/admin/depoimento/save', methods=['POST'])
def save_reviews():
    if not admin_required():
        return redirect('/index')
    
    # Save carousel config limit
    max_reviews_input = request.form.get('max_reviews')
    if max_reviews_input:
        save_reviews_config({"max_reviews": int(max_reviews_input)})
        
    active_ids = request.form.getlist('active_ids')
    active_ids = [int(x) for x in active_ids]

    reviews = ClientReview.query.all()
    for review in reviews:
        review.active = (review.id in active_ids)
        
        name = request.form.get(f'name_{review.id}')
        role = request.form.get(f'role_{review.id}')
        rating = request.form.get(f'rating_{review.id}')
        text = request.form.get(f'text_{review.id}')
        sort_order = request.form.get(f'sort_order_{review.id}')
        
        if name:
            review.client_name = name
        if role:
            review.client_role = role
        if rating:
            review.rating = int(rating)
        if text:
            review.review_text = text
        if sort_order:
            review.sort_order = int(sort_order)
            
        # Handle file upload for this specific card
        avatar_file = request.files.get(f'avatar_{review.id}')
        if avatar_file and avatar_file.filename:
            filename = secure_filename(avatar_file.filename)
            random_suffix = secrets.token_hex(4)
            name_part, ext_part = os.path.splitext(filename)
            filename = f"{name_part}_{random_suffix}{ext_part}"
            save_path = os.path.join(current_app.root_path, 'static', 'images', 'users', filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            avatar_file.save(save_path)
            review.avatar_filename = filename

    db.session.commit()
    flash('Alterações nos depoimentos salvas com sucesso!', 'success')
    return redirect('/admin-depoimentos')


@blueprint.route('/admin/depoimento/<int:review_id>/delete', methods=['POST'])
def delete_review(review_id):
    if not admin_required():
        return redirect('/index')
    review = db.session.get(ClientReview, review_id)
    if review:
        db.session.delete(review)
        db.session.commit()
        flash(f'Depoimento de {review.client_name} excluído com sucesso.', 'success')
    else:
        flash('Depoimento não encontrado.', 'warning')
    return redirect('/admin-depoimentos')
