"""media table

Revision ID: 84d1e1dbc86d
Revises: 208ae3f1f93a
Create Date: 2021-04-17 23:05:32.638247

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '84d1e1dbc86d'
down_revision = '208ae3f1f93a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('siren_media',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('media_type', sa.Enum('SATELLITE_IMAGE', 'STREET_IMAGE', name='sirenmediatype'), nullable=False),
    sa.Column('filename', sa.String(), nullable=True),
    sa.Column('mimetype', sa.String(), nullable=False),
    sa.Column('kilobytes', postgresql.DOUBLE_PRECISION(), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=False),
    sa.Column('filesystem_uri', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['location_id'], ['siren_locations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('siren_locations', sa.Column('created_timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('siren_locations', sa.Column('modified_timestamp', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('siren_locations', 'modified_timestamp')
    op.drop_column('siren_locations', 'created_timestamp')
    op.drop_table('siren_media')
    # ### end Alembic commands ###