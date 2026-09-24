from apps import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, date, timedelta
import json

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    ddd = db.Column(db.String(2), nullable=True)
    contact = db.Column(db.String(9), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), nullable=False, default='usuario')
    category = db.Column(db.String(32), nullable=False, default='Orange')
    active = db.Column(db.Boolean, nullable=False, default=True)
    must_change_password = db.Column(db.Boolean, nullable=False, default=False)
    avatar_filename = db.Column(db.String(160), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin_or_manager(self):
        return self.role.lower() in {'admin', 'gerente'}

    def __repr__(self):
        return f'<User {self.email}>'


class CarouselImage(db.Model):
    __tablename__ = 'carousel_images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    set_type = db.Column(db.String(32), nullable=False, default='outros')
    active = db.Column(db.Boolean, nullable=False, default=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<CarouselImage {self.filename}>'


class CommercialPlan(db.Model):
    __tablename__ = 'commercial_plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    vehicle_type = db.Column(db.String(80), nullable=False)
    coverage = db.Column(db.String(160), nullable=False)
    monthly_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    installation_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    description = db.Column(db.String(240), nullable=False, default='')
    benefits = db.Column(db.Text, nullable=False, default='')
    badge = db.Column(db.String(60), nullable=False, default='')
    whatsapp_url = db.Column(db.Text, nullable=False, default='')
    active = db.Column(db.Boolean, nullable=False, default=True)
    featured = db.Column(db.Boolean, nullable=False, default=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    last_version_code = db.Column(db.String(32), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))


class PlanVersion(db.Model):
    __tablename__ = 'plan_versions'

    id = db.Column(db.Integer, primary_key=True)
    version_code = db.Column(db.String(32), unique=True, nullable=False)
    snapshot = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class LandingCard(db.Model):
    __tablename__ = 'landing_cards'

    id = db.Column(db.Integer, primary_key=True)
    slot = db.Column(db.Integer, unique=True, nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('commercial_plans.id'), nullable=False)
    benefits = db.Column(db.Text, nullable=False, default='')
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    plan = db.relationship('CommercialPlan')


class LinktreeLink(db.Model):
    __tablename__ = 'linktree_links'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(180), nullable=False, default='')
    url = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(60), nullable=False, default='ri-links-line')
    color = db.Column(db.String(7), nullable=False, default='#2563eb')
    active = db.Column(db.Boolean, nullable=False, default=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))


class FinancialCategory(db.Model):
    __tablename__ = 'financial_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    entry_type = db.Column(db.String(16), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('financial_categories.id'), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    parent = db.relationship('FinancialCategory', remote_side=[id], backref='subcategories')


class FinancialCompany(db.Model):
    __tablename__ = 'financial_companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class FinancialEntry(db.Model):
    __tablename__ = 'financial_entries'

    id = db.Column(db.Integer, primary_key=True)
    entry_type = db.Column(db.String(16), nullable=False)
    description = db.Column(db.String(180), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('financial_categories.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('financial_companies.id'), nullable=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(16), nullable=False, default='pendente')
    notes = db.Column(db.Text, nullable=False, default='')
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    category = db.relationship('FinancialCategory')
    company = db.relationship('FinancialCompany')

    @property
    def effective_status(self):
        if self.status != 'pendente':
            return self.status
        today = date.today()
        if self.due_date < today:
            return 'vencido'
        if self.due_date < today + timedelta(days=5):
            return 'perto_vencer'
        return 'pendente'


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False, default='Sistema')
    user_name = db.Column(db.String(100), nullable=False, default='Sistema')
    action = db.Column(db.String(120), nullable=False)
    details = db.Column(db.Text, nullable=False, default='')
    ip_address = db.Column(db.String(45), nullable=False, default='')
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class IntegratedSale(db.Model):
    __tablename__ = 'integrated_sales'

    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    activation_date = db.Column(db.Date, nullable=False)
    contract_number = db.Column(db.String(40), unique=True, nullable=False)
    client_name = db.Column(db.String(160), nullable=False)
    ddd = db.Column(db.String(3), nullable=False, default='83')
    contact = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.String(40), nullable=False, default='Carro')
    vehicle_brand = db.Column(db.String(80), nullable=False, default='')
    vehicle_model = db.Column(db.String(80), nullable=False, default='')
    plate = db.Column(db.String(12), nullable=False, default='')
    plan_name = db.Column(db.String(120), nullable=False, default='')
    monthly_fee = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    seller_name = db.Column(db.String(120), nullable=False, default='API Integrada')
    seller_email = db.Column(db.String(120), nullable=False, default='')
    installation = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(32), nullable=False, default='Ativo')


class ClientReview(db.Model):
    __tablename__ = 'client_reviews'

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_role = db.Column(db.String(100), nullable=False, default='Cliente')
    avatar_filename = db.Column(db.String(200), nullable=True)
    rating = db.Column(db.Integer, nullable=False, default=5)
    review_text = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<ClientReview {self.client_name}>'


class BlogArticle(db.Model):
    __tablename__ = 'blog_articles'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    author_role = db.Column(db.String(120), nullable=False)
    author_avatar = db.Column(db.String(200), nullable=False)
    read_time = db.Column(db.String(40), nullable=False)
    cover_image = db.Column(db.String(200), nullable=False)
    excerpt = db.Column(db.Text, nullable=False)
    quote = db.Column(db.Text, nullable=False, default='')
    content_json = db.Column(db.Text, nullable=False, default='[]')
    content_html = db.Column(db.Text, nullable=False, default='')
    gallery_json = db.Column(db.Text, nullable=False, default='[]')
    status = db.Column(db.String(20), nullable=False, default='published', index=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    published_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    edited_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    @staticmethod
    def _json_list(value):
        try:
            parsed = json.loads(value or '[]')
        except (TypeError, ValueError):
            return []
        return parsed if isinstance(parsed, list) else []

    def to_public_dict(self):
        months = ('Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro')
        published = self.published_at or self.created_at or datetime.now(timezone.utc)
        edited = self.edited_at
        format_date = lambda value: f'{value.day} de {months[value.month - 1]}, {value.year}'
        return {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'category': self.category,
            'author_name': self.author_name,
            'author_role': self.author_role,
            'author_avatar': self.author_avatar,
            'date': format_date(published),
            'published_date': published.strftime('%Y-%m-%d'),
            'edited_date': format_date(edited) if edited else '',
            'is_edited': bool(edited),
            'display_date': format_date(edited or published),
            'read_time': self.read_time,
            'cover_image': self.cover_image,
            'excerpt': self.excerpt,
            'quote': self.quote or self.excerpt,
            'content_paragraphs': self._json_list(self.content_json),
            'content_html': self.content_html or '',
            'gallery': self._json_list(self.gallery_json),
            'status': self.status or 'published',
        }


class WoodworkOrder(db.Model):
    __tablename__ = 'woodwork_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(32), unique=True, nullable=False, index=True)
    cpf = db.Column(db.String(18), nullable=False, index=True)
    client_name = db.Column(db.String(120), nullable=False)
    client_phone = db.Column(db.String(30), nullable=True)
    item_title = db.Column(db.String(160), nullable=False)
    wood_type = db.Column(db.String(120), nullable=False, default='Madeira de Demolição Nobre')
    dimensions = db.Column(db.String(100), nullable=True)
    current_step = db.Column(db.Integer, nullable=False, default=1)
    step_description = db.Column(db.String(240), nullable=True)
    estimated_delivery = db.Column(db.String(80), nullable=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=True, default=0)
    deposit_amount = db.Column(db.Numeric(10, 2), nullable=True, default=0)
    balance_amount = db.Column(db.Numeric(10, 2), nullable=True, default=0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    @property
    def clean_cpf(self):
        import re
        return re.sub(r'\D', '', self.cpf or '')

    @property
    def formatted_cpf(self):
        c = self.clean_cpf
        if len(c) == 11:
            return f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}"
        return self.cpf

    def to_dict(self):
        step_definitions = [
            {
                'number': 1,
                'name': 'Pedido',
                'label': 'Pedido',
                'sublabel': 'Pedido Realizado',
                'description': 'Briefing e especificações técnicas registrados no ateliê.',
                'icon': 'ri-file-list-3-line'
            },
            {
                'number': 2,
                'name': 'Sinal financeiro',
                'label': 'Sinal financeiro',
                'sublabel': 'Sinal Confirmado',
                'description': f"Entrada confirmada de R$ {float(self.deposit_amount or 0):,.2f} para reserva das toras.".replace('.', 'X').replace(',', '.').replace('X', ','),
                'icon': 'ri-hand-coin-line'
            },
            {
                'number': 3,
                'name': 'Elaboração da peça',
                'label': 'Elaboração da peça',
                'sublabel': 'Em Produção',
                'description': 'Corte, respigas, entalhe manual e polimento na marcenaria.',
                'icon': 'ri-hammer-line'
            },
            {
                'number': 4,
                'name': 'Pagamento',
                'label': 'Pagamento',
                'sublabel': 'Saldo Quitado',
                'description': 'Acabamento aprovado e quitação do saldo final.',
                'icon': 'ri-bank-card-line'
            },
            {
                'number': 5,
                'name': 'Entrega',
                'label': 'Entrega',
                'sublabel': 'Entrega & Envio',
                'description': 'Embalagem reforçada e transporte seguro até o destino.',
                'icon': 'ri-truck-line'
            }
        ]

        steps_output = []
        for s in step_definitions:
            if s['number'] < self.current_step:
                status = 'completed'
            elif s['number'] == self.current_step:
                status = 'active'
            else:
                status = 'pending'

            steps_output.append({
                'number': s['number'],
                'name': s['name'],
                'label': s['label'],
                'sublabel': s['sublabel'],
                'description': s['description'],
                'icon': s['icon'],
                'status': status
            })

        step_names = ['Pedido', 'Sinal financeiro', 'Elaboração da peça', 'Pagamento', 'Entrega']
        cur_name = step_names[min(max(self.current_step - 1, 0), 4)]

        img_map = {
            'mesa': 'mesa-jantar-peroba-rosa-demolicao-1.png',
            'escultura': 'carrinho-bar-colonial-madeira.png',
            'painel': 'armarios-cozinha-jatoba-lambri-demolicao-1.png',
            'bancada': 'bancada-madeira-demolicao-verniz-pu-1.png',
            'aparador': 'comoda-balcao-gaveteiro-demolicao.png'
        }
        item_img = 'mesa-jantar-peroba-rosa-demolicao-1.png'
        t_low = (self.item_title or '').lower()
        for k, v in img_map.items():
            if k in t_low:
                item_img = v
                break

        return {
            'id': self.id,
            'order_number': self.order_number,
            'client_name': self.client_name,
            'client_phone': self.client_phone,
            'cpf': self.formatted_cpf,
            'clean_cpf': self.clean_cpf,
            'item_title': self.item_title,
            'item_image': f"/static/images/{item_img}",
            'wood_type': self.wood_type,
            'dimensions': self.dimensions,
            'current_step': self.current_step,
            'current_step_name': cur_name,
            'step_description': self.step_description or step_definitions[min(max(self.current_step - 1, 0), 4)]['description'],
            'estimated_delivery': self.estimated_delivery or 'Consulte o ateliê',
            'total_amount': float(self.total_amount or 0),
            'deposit_amount': float(self.deposit_amount or 0),
            'balance_amount': float(self.balance_amount or 0),
            'notes': self.notes,
            'created_at': self.created_at.strftime('%d/%m/%Y'),
            'steps': steps_output
        }

    def __repr__(self):
        return f'<WoodworkOrder {self.order_number} - {self.client_name}>'
