"""resources table

Revision ID: 09fd72b6648e
Revises: 7b3ac689f83a
Create Date: 2020-03-26 01:15:25.739792

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09fd72b6648e'
down_revision = '7b3ac689f83a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_categories_name', table_name='categories')
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.create_index('ix_categories_name', 'categories', ['name'], unique=False)
    # ### end Alembic commands ###
