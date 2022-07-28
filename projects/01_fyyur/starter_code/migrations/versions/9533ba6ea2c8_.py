"""empty message

Revision ID: 9533ba6ea2c8
Revises: 77e2a60982b6
Create Date: 2022-07-28 20:40:51.481001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9533ba6ea2c8'
down_revision = '77e2a60982b6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    # ### end Alembic commands ###