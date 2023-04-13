"""empty message

Revision ID: f0aa41eded25
Revises: c46610caca3d
Create Date: 2023-04-13 12:36:06.728313+00:00
"""

import alembic.op as op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = 'f0aa41eded25'
down_revision = 'c46610caca3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('refreshtokens', 'revoked_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('refreshtokens', 'revoked_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False)
    # ### end Alembic commands ###