"""empty message

Revision ID: b9642d8f9ee9
Revises: 41f65b7cad3e
Create Date: 2020-05-16 15:39:01.468289

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9642d8f9ee9'
down_revision = '41f65b7cad3e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artist', 'past_shows_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('artist', 'upcoming_shows_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('artist', 'seeking_description')
    op.drop_column('artist', 'seeking_venue')
    op.alter_column('venue', 'past_shows_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('venue', 'seeking_description',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)
    op.alter_column('venue', 'upcoming_shows_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venue', 'upcoming_shows_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('venue', 'seeking_description',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
    op.alter_column('venue', 'past_shows_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.add_column('artist', sa.Column('seeking_venue', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('artist', sa.Column('seeking_description', sa.VARCHAR(length=200), autoincrement=False, nullable=False))
    op.alter_column('artist', 'upcoming_shows_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('artist', 'past_shows_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
