"""a

Revision ID: 198ca44535ae
Revises: a76bd14371c9
Create Date: 2023-02-03 21:21:17.231771

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '198ca44535ae'
down_revision = 'a76bd14371c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('chat_message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file', sa.String(), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('file')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file', sa.VARCHAR(), nullable=True))

    with op.batch_alter_table('chat_message', schema=None) as batch_op:
        batch_op.drop_column('file')

    # ### end Alembic commands ###