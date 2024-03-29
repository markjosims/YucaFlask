"""entries table

Revision ID: d0ec19ffe792
Revises: 
Create Date: 2020-02-04 14:46:02.153774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0ec19ffe792'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('entry',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('headword', sa.String(length=24), nullable=True),
    sa.Column('gloss', sa.String(length=24), nullable=True),
    sa.Column('pos', sa.String(length=12), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_entry_timestamp'), 'entry', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_entry_timestamp'), table_name='entry')
    op.drop_table('entry')
    # ### end Alembic commands ###
