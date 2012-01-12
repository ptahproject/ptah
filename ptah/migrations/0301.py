"""Ptah 0.3.x changes

Revision ID: 0301
Revises: None
Create Date: 2012-01-10 10:53:51.715491

"""

# downgrade revision identifier, used by Alembic.
down_revision = None

import ptah
from alembic import op
from alembic import context
import sqlalchemy as sa
from sqlalchemy.engine import reflection


def upgrade():
    # it possible that this script is being called on new database
    # in this case we should not do anything
    insp = reflection.Inspector.from_engine(ptah.get_base().metadata.bind)

    if 'annotations' in [r['name'] for r in insp.get_columns('ptah_nodes')]:
        return

    # ptah_nodes
    op.add_column(
        'ptah_nodes',
        sa.Column('annotations', ptah.JsonDictType(), default={}))

    # ptah_content
    op.add_column(
        'ptah_content', sa.Column('lang', sa.String(12), default='en'))

    op.create_index(
        'ix_ptah_content_path', 'ptah_content', ('path',))

    # sqlite doesnt support column drop
    impl = context.get_impl()

    if impl.__dialect__ != 'sqlite':
        op.drop_column('ptah_content', 'view')
        op.drop_column('ptah_content', 'creators')
        op.drop_column('ptah_content', 'subjects')
        op.drop_column('ptah_content', 'publisher')
        op.drop_column('ptah_content', 'contributors')

    op.drop_table('test_sqla_table')


def downgrade():
    pass
