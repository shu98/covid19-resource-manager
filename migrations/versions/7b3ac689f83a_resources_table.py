"""resources table

Revision ID: 7b3ac689f83a
Revises: 36fff97199a0
Create Date: 2020-03-25 21:49:53.929584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b3ac689f83a'
down_revision = '36fff97199a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=255), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    op.create_index(op.f('ix_categories_slug'), 'categories', ['slug'], unique=False)
    op.create_table('resources',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('institution', sa.String(length=255), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('link', sa.Text(), nullable=False),
    sa.Column('submitter', sa.String(length=255), nullable=True),
    sa.Column('date_added', sa.DateTime(), nullable=True),
    sa.Column('file_location', sa.Text(), nullable=True),
    sa.Column('upvotes', sa.Integer(), nullable=True),
    sa.Column('show', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resources_date_added'), 'resources', ['date_added'], unique=False)
    op.create_index(op.f('ix_resources_description'), 'resources', ['description'], unique=False)
    op.create_index(op.f('ix_resources_institution'), 'resources', ['institution'], unique=False)
    op.create_index(op.f('ix_resources_link'), 'resources', ['link'], unique=True)
    op.create_index(op.f('ix_resources_submitter'), 'resources', ['submitter'], unique=False)
    op.create_index(op.f('ix_resources_title'), 'resources', ['title'], unique=True)
    op.create_index(op.f('ix_resources_upvotes'), 'resources', ['upvotes'], unique=False)
    op.create_table('resource_categories',
    sa.Column('resource_id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], )
    )
    op.drop_index('ix_resource_date_added', table_name='resource')
    op.drop_index('ix_resource_link', table_name='resource')
    op.drop_index('ix_resource_source', table_name='resource')
    op.drop_index('ix_resource_tag', table_name='resource')
    op.drop_index('ix_resource_title', table_name='resource')
    op.drop_table('resource')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('resource',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.TEXT(), nullable=True),
    sa.Column('source', sa.VARCHAR(length=128), nullable=True),
    sa.Column('tag', sa.VARCHAR(length=128), nullable=True),
    sa.Column('link', sa.TEXT(), nullable=True),
    sa.Column('date_added', sa.DATETIME(), nullable=True),
    sa.Column('show', sa.BOOLEAN(), nullable=True),
    sa.CheckConstraint('show IN (0, 1)'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_resource_title', 'resource', ['title'], unique=1)
    op.create_index('ix_resource_tag', 'resource', ['tag'], unique=False)
    op.create_index('ix_resource_source', 'resource', ['source'], unique=False)
    op.create_index('ix_resource_link', 'resource', ['link'], unique=1)
    op.create_index('ix_resource_date_added', 'resource', ['date_added'], unique=False)
    op.drop_table('resource_categories')
    op.drop_index(op.f('ix_resources_upvotes'), table_name='resources')
    op.drop_index(op.f('ix_resources_title'), table_name='resources')
    op.drop_index(op.f('ix_resources_submitter'), table_name='resources')
    op.drop_index(op.f('ix_resources_link'), table_name='resources')
    op.drop_index(op.f('ix_resources_institution'), table_name='resources')
    op.drop_index(op.f('ix_resources_description'), table_name='resources')
    op.drop_index(op.f('ix_resources_date_added'), table_name='resources')
    op.drop_table('resources')
    op.drop_index(op.f('ix_categories_slug'), table_name='categories')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_table('categories')
    # ### end Alembic commands ###
