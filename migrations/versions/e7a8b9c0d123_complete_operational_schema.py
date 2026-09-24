"""complete operational schema and persist integrated sales

Revision ID: e7a8b9c0d123
Revises: d6f704253647
"""
from alembic import op
import sqlalchemy as sa


revision = 'e7a8b9c0d123'
down_revision = 'd6f704253647'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if 'financial_companies' not in tables:
        op.create_table('financial_companies',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('active', sa.Boolean(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('name'))

    columns = [c['name'] for c in inspector.get_columns('financial_entries')]
    if 'company_id' not in columns:
        op.add_column('financial_entries', sa.Column('company_id', sa.Integer(), nullable=True))
        op.create_foreign_key('fk_financial_entry_company', 'financial_entries', 'financial_companies', ['company_id'], ['id'])

    if 'audit_logs' not in tables:
        op.create_table('audit_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_email', sa.String(length=120), nullable=False),
            sa.Column('user_name', sa.String(length=100), nullable=False),
            sa.Column('action', sa.String(length=120), nullable=False),
            sa.Column('details', sa.Text(), nullable=False),
            sa.Column('ip_address', sa.String(length=45), nullable=False),
            sa.Column('timestamp', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'))

    if 'integrated_sales' not in tables:
        op.create_table('integrated_sales',
            sa.Column('id', sa.BigInteger(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('activation_date', sa.Date(), nullable=False),
            sa.Column('contract_number', sa.String(length=40), nullable=False),
            sa.Column('client_name', sa.String(length=160), nullable=False),
            sa.Column('ddd', sa.String(length=3), nullable=False),
            sa.Column('contact', sa.String(length=20), nullable=False),
            sa.Column('vehicle_type', sa.String(length=40), nullable=False),
            sa.Column('vehicle_brand', sa.String(length=80), nullable=False),
            sa.Column('vehicle_model', sa.String(length=80), nullable=False),
            sa.Column('plate', sa.String(length=12), nullable=False),
            sa.Column('plan_name', sa.String(length=120), nullable=False),
            sa.Column('monthly_fee', sa.Numeric(precision=12, scale=2), nullable=False),
            sa.Column('seller_name', sa.String(length=120), nullable=False),
            sa.Column('seller_email', sa.String(length=120), nullable=False),
            sa.Column('installation', sa.Boolean(), nullable=False),
            sa.Column('status', sa.String(length=32), nullable=False),
            sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('contract_number'))


def downgrade():
    op.drop_table('integrated_sales')
    op.drop_table('audit_logs')
    op.drop_constraint('fk_financial_entry_company', 'financial_entries', type_='foreignkey')
    op.drop_column('financial_entries', 'company_id')
    op.drop_table('financial_companies')
