import enum

from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.sql import func

from sirendb.core.db import db

from .siren_location import SirenLocation  # noqa


class SirenMediaType(enum.Enum):
    '''
    The type of media.
    '''
    SATELLITE_IMAGE = enum.auto()
    STREET_IMAGE = enum.auto()


class SirenMedia(db.Model):
    '''
    Describes downloadable content related to the siren location.
    '''
    __tablename__ = 'siren_media'

    id = db.Column(
        db.Integer,
        primary_key=True,
        nullable=False,
        doc=(
            'Identifies the primary key from the database.'
        )
    )
    media_type = db.Column(
        db.Enum(SirenMediaType),
        nullable=False,
        doc=(
            'The type of media.'
        )
    )
    filename = db.Column(
        db.String,
        default=None,
        doc='The name of the file.'
    )
    mimetype = db.Column(
        db.String,
        nullable=False,
        doc='Mimetype of this file.'
    )
    kilobytes = db.Column(
        DOUBLE_PRECISION,
        nullable=False,
        doc='Size in kilobytes of this media.'
    )
    location_id = db.Column(
        db.ForeignKey('siren_locations.id'),
        nullable=False,
        doc="Identifies the siren location's primary key from the database."
    )
    filesystem_uri = db.Column(
        db.String,
        nullable=False,
        doc='Identifies the location within the internal filesystem.'
    )
    created_timestamp = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        doc='Timestamp when this entry was created.',
    )
    created_by_id = db.Column(
        db.ForeignKey('users.id'),
        default=None,
        doc=(
            'id of the user who created this entry. '
            'This is null if this was generated by the server.'
        )
    )
    location = db.relationship(
        'SirenLocation',
        foreign_keys=[location_id],
        uselist=False,
        back_populates='media',
        doc='The location associated with this media.',
    )
    created_by = db.relationship(
        'User',
        foreign_keys=[created_by_id],
        uselist=False,
        doc='The user who created this entry.',
    )
