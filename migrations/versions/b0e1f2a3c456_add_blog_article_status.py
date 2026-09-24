"""add blog article publication status

Revision ID: b0e1f2a3c456
Revises: a9d0e1f2b345
"""
from alembic import op
import sqlalchemy as sa


revision = 'b0e1f2a3c456'
down_revision = 'a9d0e1f2b345'
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    columns = {column['name'] for column in inspector.get_columns('blog_articles')}
    if 'status' not in columns:
        op.add_column(
            'blog_articles',
            sa.Column('status', sa.String(length=20), nullable=False,
                      server_default='published'),
        )
    indexes = {index['name'] for index in inspector.get_indexes('blog_articles')}
    if 'ix_blog_articles_status' not in indexes:
        op.create_index('ix_blog_articles_status', 'blog_articles', ['status'], unique=False)


def downgrade():
    op.drop_index('ix_blog_articles_status', table_name='blog_articles')
    op.drop_column('blog_articles', 'status')
