"""add persistent blog articles

Revision ID: a9d0e1f2b345
Revises: f8b9c0d1e234
"""
from alembic import op
import sqlalchemy as sa


revision = 'a9d0e1f2b345'
down_revision = 'f8b9c0d1e234'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'blog_articles' in inspector.get_table_names():
        return

    op.create_table(
        'blog_articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=180), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('category', sa.String(length=80), nullable=False),
        sa.Column('author_name', sa.String(length=100), nullable=False),
        sa.Column('author_role', sa.String(length=120), nullable=False),
        sa.Column('author_avatar', sa.String(length=200), nullable=False),
        sa.Column('read_time', sa.String(length=40), nullable=False),
        sa.Column('cover_image', sa.String(length=200), nullable=False),
        sa.Column('excerpt', sa.Text(), nullable=False),
        sa.Column('quote', sa.Text(), nullable=False),
        sa.Column('content_json', sa.Text(), nullable=False),
        sa.Column('gallery_json', sa.Text(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('edited_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_blog_articles_slug', 'blog_articles', ['slug'], unique=True)


def downgrade():
    op.drop_index('ix_blog_articles_slug', table_name='blog_articles')
    op.drop_table('blog_articles')
