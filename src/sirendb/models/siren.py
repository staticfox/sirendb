from sqlalchemy.sql import func

from sirendb.core.db import db

from .siren_location import SirenLocation  # noqa
from .siren_model import SirenModel  # noqa


class Siren(db.Model):
    '''
    Describes a siren installation site.
    '''
    __tablename__ = 'sirens'

    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False,
        doc=(
            'Identifies the primary key from the database.'
        )
    )
    model_id = db.Column(
        db.Integer,
        db.ForeignKey('siren_models.id'),
        nullable=False,
        doc=(
            "Identifies the model's primary key from the database."
        )
    )
    active = db.Column(
        db.Boolean,
        default=None,
        doc='Whether or not the siren is active'
    )
    created_timestamp = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        doc='Timestamp when this entry was first created.',
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
        doc='Timestamp when this entry was last updated.',
    )
    updated_by_id = db.Column(
        db.ForeignKey('users.id'),
        default=None,
        doc='id of the last user who updated this entry.'
    )
    model = db.relationship(
        'SirenModel',
        foreign_keys=[model_id],
        uselist=False,
        doc='The model of the siren.'
    )
    locations = db.relationship(
        'SirenLocation',
        lazy='dynamic',
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
