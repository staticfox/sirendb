import enum

from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION

from sirendb.core.db import db

from .siren_location import SirenLocation  # noqa


class SirenMediaType(enum.Enum):
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
    download_url = db.Column(
        db.String,
        nullable=False,
        doc='Network location of this media.'
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
    location = db.relationship(
        'SirenLocation',
        foreign_keys=[location_id],
        uselist=False,
        back_populates='media',
        doc='The location associated with this media.',
    )
