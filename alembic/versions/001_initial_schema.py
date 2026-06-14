"""Initial schema

Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('org_id', sa.Integer()),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_org_id', 'users', ['org_id'])

def downgrade():
    op.drop_index('idx_users_email')
    op.drop_index('idx_users_org_id')
    op.drop_table('users')
