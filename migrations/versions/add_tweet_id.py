"""add tweet id column

Revision ID: add_tweet_id
Revises: previous_revision_id
Create Date: 2024-03-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_tweet_id'
down_revision = None  # Replace with your last migration's ID if any
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('article', sa.Column('tweet_id', sa.String(50), nullable=True))

def downgrade():
    op.drop_column('article', 'tweet_id') 