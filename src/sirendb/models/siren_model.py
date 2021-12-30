from sqlalchemy.sql import func

from sirendb.core.db import db

from .siren_manufacturer import SirenManufacturer  # noqa


class SirenModel(db.Model):
    '''
    Describes a model for a given siren.
    '''
    __tablename__ = 'siren_models'

    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False,
        doc=(
            'Identifies the primary key from the database.'
        )
    )
    created_timestamp = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        doc=(
            'Timestamp when this entry was created.'
        )
    )
    created_by_id = db.Column(
        db.ForeignKey('users.id'),
        nullable=False,
        doc='id of the user who created this entry.',
    )
    updated_timestamp = db.Column(
        db.DateTime,
        default=None,
        onupdate=func.now(),
        doc=(
            'Timestamp when this entry was last updated.'
        )
    )
    updated_by_id = db.Column(
        db.ForeignKey('users.id'),
        default=None,
        doc='id of the last user who updated this entry.'
    )
    name = db.Column(
        db.String(80),
        nullable=False,
        doc='The name of the manufacturer.',
    )
    manufacturer_id = db.Column(
        db.ForeignKey('siren_manufacturers.id'),
        default=None,
        doc="Identifies the manufacturer's primary key from the database."
    )
    start_of_production = db.Column(
        db.DateTime,
        default=None,
        doc='Timestamp when the model started production.'
    )
    end_of_production = db.Column(
        db.DateTime,
        default=None,
        doc='Timestamp when the model went out of production.'
    )
    info = db.Column(
        db.Text,
        default=None,
        doc='Additional information about the model.'
    )
    revision = db.Column(
        db.Text,
        default=None,
        doc="The models's specific revision."
    )
    manufacturer = db.relationship(
        'SirenManufacturer',
        foreign_keys=[manufacturer_id],
        uselist=False,
        doc="The manufacturer of the model."
    )
    created_by = db.relationship(
        'User',
        foreign_keys=[created_by_id],
        uselist=False,
        doc='The user who created this siren entry.',
    )
    updated_by = db.relationship(
        'User',
        foreign_keys=[updated_by_id],
        uselist=False,
        doc='The user who last updated this siren entry.',
    )
