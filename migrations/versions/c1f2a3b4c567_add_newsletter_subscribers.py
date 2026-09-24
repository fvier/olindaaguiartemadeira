"""add newsletter subscribers table

Revision ID: c1f2a3b4c567
Revises: b0e1f2a3c456
"""
from alembic import op
import sqlalchemy as sa


revision = 'c1f2a3b4c567'
down_revision = 'b0e1f2a3c456'
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    if 'newsletter_subscribers' not in inspector.get_table_names():
        op.create_table(
            'newsletter_subscribers',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(length=150), nullable=False),
            sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_newsletter_subscribers_email', 'newsletter_subscribers', ['email'], unique=True)


def downgrade():
    inspector = sa.inspect(op.get_bind())
    if 'newsletter_subscribers' in inspector.get_table_names():
        op.drop_index('ix_newsletter_subscribers_email', table_name='newsletter_subscribers')
        op.drop_table('newsletter_subscribers')
