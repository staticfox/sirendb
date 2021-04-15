"""initial schema

Revision ID: 208ae3f1f93a
Revises: 
Create Date: 2021-04-13 23:30:13.293439

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '208ae3f1f93a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('siren_manufacturers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_timestamp', sa.DateTime(), nullable=False),
    sa.Column('modified_timestamp', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('founded_timestamp', sa.DateTime(), nullable=True),
    sa.Column('defunct_timestamp', sa.DateTime(), nullable=True),
    sa.Column('info', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('siren_systems',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_timestamp', sa.DateTime(), nullable=False),
    sa.Column('modified_timestamp', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('start_of_service_timestamp', sa.DateTime(), nullable=True),
    sa.Column('end_of_service_timestamp', sa.DateTime(), nullable=True),
    sa.Column('in_service', sa.Boolean(), nullable=True),
    sa.Column('city', sa.String(length=50), nullable=True),
    sa.Column('county', sa.String(length=50), nullable=True),
    sa.Column('state', sa.String(length=50), nullable=True),
    sa.Column('country', sa.String(length=50), nullable=True),
    sa.Column('postal_code', sa.String(length=20), nullable=True),
    sa.Column('siren_wiki_url', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=512), nullable=False),
    sa.Column('register_timestamp', sa.DateTime(), nullable=False),
    sa.Column('email_verified_timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('siren_models',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_timestamp', sa.DateTime(), nullable=False),
    sa.Column('modified_timestamp', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('manufacturer_id', sa.Integer(), nullable=True),
    sa.Column('start_of_production', sa.DateTime(), nullable=True),
    sa.Column('end_of_production', sa.DateTime(), nullable=True),
    sa.Column('info', sa.Text(), nullable=True),
    sa.Column('revision', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['manufacturer_id'], ['siren_manufacturers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sirens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('model_id', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['model_id'], ['siren_models.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('siren_locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('satellite_latitude', postgresql.DOUBLE_PRECISION(), nullable=True),
    sa.Column('satellite_longitude', postgresql.DOUBLE_PRECISION(), nullable=True),
    sa.Column('satellite_zoom', postgresql.DOUBLE_PRECISION(), nullable=True),
    sa.Column('street_latitude', postgresql.DOUBLE_PRECISION(), nullable=True),
    sa.Column('street_longitude', postgresql.DOUBLE_PRECISION(), nullable=True),
    sa.Column('street_heading', postgresql.DOUBLE_PRECISION(), nullable=True),
    sa.Column('street_pitch', sa.Float(precision=4), nullable=True),
    sa.Column('street_zoom', sa.Float(precision=4), nullable=True),
    sa.Column('siren_id', sa.Integer(), nullable=False),
    sa.Column('system_id', sa.Integer(), nullable=True),
    sa.Column('installation_timestamp', sa.DateTime(), nullable=True),
    sa.Column('removal_timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['siren_id'], ['sirens.id'], ),
    sa.ForeignKeyConstraint(['system_id'], ['siren_systems.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('siren_locations')
    op.drop_table('sirens')
    op.drop_table('siren_models')
    op.drop_table('users')
    op.drop_table('siren_systems')
    op.drop_table('siren_manufacturers')
