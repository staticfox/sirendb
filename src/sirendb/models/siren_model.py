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
        doc=(
            'Identifies the primary key from the database.'
        )
    )
    created_timestamp = db.Column(
        db.DateTime,
        nullable=False,
        doc=(
            'Timestamp when this entry was created.'
        )
    )
    modified_timestamp = db.Column(
        db.DateTime,
        default=None,
        doc=(
            'Timestamp when this entry was last modified.'
        )
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
