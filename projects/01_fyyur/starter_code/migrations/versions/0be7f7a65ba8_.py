"""empty message

Revision ID: 0be7f7a65ba8
Revises: d212fba4de44
Create Date: 2021-08-29 23:42:25.961149

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0be7f7a65ba8'
down_revision = 'd212fba4de44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venues', sa.Boolean(), nullable=False))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('Venue', sa.Column('website_link', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website_link')
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'seeking_venues')
    op.drop_column('Artist', 'website_link')
    # ### end Alembic commands ###
