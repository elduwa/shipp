"""empty message

Revision ID: cdd8611f8f30
Revises: 46c741e2a968
Create Date: 2023-08-02 20:13:24.510385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdd8611f8f30'
down_revision = '46c741e2a968'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('policy_device_map')


def downgrade():
    op.create_table('policy_device_map',
                    sa.Column('policy_id', sa.INTEGER(), nullable=False),
                    sa.Column('device_id', sa.INTEGER(), nullable=False),
                    sa.ForeignKeyConstraint(['device_id'], ['device.id'], ),
                    sa.ForeignKeyConstraint(['policy_id'], ['policy.id'], ),
                    sa.PrimaryKeyConstraint('policy_id', 'device_id')
                    )
