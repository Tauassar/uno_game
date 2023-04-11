"""empty message

Revision ID: 8d0d1a816560
Revises: 7d3b0a925109
Create Date: 2022-08-15 07:18:17.356020+00:00
"""

import alembic.op as op
import sqlalchemy as sa


revision = '8d0d1a816560'
down_revision = '7d3b0a925109'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('accesstokens',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.Text(), nullable=False),
        sa.Column('token_type', sa.Text(), server_default='bearer', nullable=False),
        sa.Column('is_revoked', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_in', sa.Integer(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('token'),
        sa.UniqueConstraint('token', name='uq_accesstokens_token'),
    )
    op.create_table('refreshtokens',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.Text(), nullable=False),
        sa.Column('token_type', sa.Text(), server_default='bearer', nullable=False),
        sa.Column('is_revoked', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('token'),
        sa.UniqueConstraint('token', name='uq_refreshtokens_token'),
    )
    op.create_index(
        op.f('ix_refreshtokens_user_id'),
        'refreshtokens',
        ['user_id'],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f('ix_refreshtokens_user_id'),
        table_name='refreshtokens',
    )
    op.drop_table('refreshtokens')
    op.drop_table('accesstokens')
