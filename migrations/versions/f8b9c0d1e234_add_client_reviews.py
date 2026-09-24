"""add client_reviews table

Revision ID: f8b9c0d1e234
Revises: e7a8b9c0d123
"""
from alembic import op
import sqlalchemy as sa


revision = 'f8b9c0d1e234'
down_revision = 'e7a8b9c0d123'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if 'client_reviews' not in tables:
        op.create_table(
            'client_reviews',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('client_name', sa.String(length=100), nullable=False),
            sa.Column('client_role', sa.String(length=100), nullable=False),
            sa.Column('avatar_filename', sa.String(length=200), nullable=True),
            sa.Column('rating', sa.Integer(), nullable=False),
            sa.Column('review_text', sa.Text(), nullable=False),
            sa.Column('active', sa.Boolean(), nullable=False),
            sa.Column('sort_order', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade():
    op.drop_table('client_reviews')
