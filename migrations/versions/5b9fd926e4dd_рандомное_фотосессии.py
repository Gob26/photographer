"""РАндомное фотосессии

Revision ID: 5b9fd926e4dd
Revises: c11c8851df65
Create Date: 2024-10-04 20:24:47.719056

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b9fd926e4dd'
down_revision = 'c11c8851df65'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('photosession', schema=None) as batch_op:
        batch_op.add_column(sa.Column('show_on_main', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('photosession', schema=None) as batch_op:
        batch_op.drop_column('show_on_main')

    # ### end Alembic commands ###
