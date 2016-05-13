"""empty message

Revision ID: 0897a5267f59
Revises: 9a070d09f4be
Create Date: 2016-05-13 19:52:47.087970

"""

# revision identifiers, used by Alembic.
revision = '0897a5267f59'
down_revision = '9a070d09f4be'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('fb_id', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'fb_id')
    ### end Alembic commands ###
