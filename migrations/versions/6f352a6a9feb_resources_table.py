"""resources table

Revision ID: 6f352a6a9feb
Revises: 07aaca035d6f
Create Date: 2020-04-01 00:35:18.599459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f352a6a9feb'
down_revision = '07aaca035d6f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('resources', schema=None) as batch_op:
        batch_op.add_column(sa.Column('iped_ad', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('resource_type', sa.String(length=255), nullable=True))
        batch_op.create_index(batch_op.f('ix_resources_iped_ad'), ['iped_ad'], unique=False)
        batch_op.create_index(batch_op.f('ix_resources_resource_type'), ['resource_type'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('resources', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_resources_resource_type'))
        batch_op.drop_index(batch_op.f('ix_resources_iped_ad'))
        batch_op.drop_column('resource_type')
        batch_op.drop_column('iped_ad')

    # ### end Alembic commands ###
