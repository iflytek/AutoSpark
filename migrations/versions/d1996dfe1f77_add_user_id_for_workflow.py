"""add user_id for workflow

Revision ID: d1996dfe1f77
Revises: 4e2578740233
Create Date: 2023-08-18 11:27:52.144904

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1996dfe1f77'
down_revision = '4e2578740233'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('agent_workflows', sa.Column('user_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('agent_workflows', sa.Column('user_id', sa.Integer(), nullable=True))


