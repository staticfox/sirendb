from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION

from sirendb.core.db import db


class SirenLocation(db.Model):
    '''
    Describes a specific siren location.
    '''
    __tablename__ = 'siren_locations'

    id = db.Column(
        db.Integer,
        primary_key=True,
        doc=(
            'Identifies the primary key from the database.'
        )
    )
    topographic_latitude = db.Column(
        DOUBLE_PRECISION,
        default=None,
        doc=''
    )
    topographic_longitude = db.Column(
        DOUBLE_PRECISION,
        default=None,
        doc=''
    )
    topographic_zoom = db.Column(
        db.Float(precision=14),
        default=None,
        doc=''
    )
    street_latitude = db.Column(
        DOUBLE_PRECISION,
        default=None,
        doc=''
    )
    street_longitude = db.Column(
        DOUBLE_PRECISION,
        default=None,
        doc=''
    )
    street_heading = db.Column(
        DOUBLE_PRECISION,
        default=None,
        doc=''
    )
    street_pitch = db.Column(
        db.Float(precision=4),
        default=None,
        doc=''
    )
    street_zoom = db.Column(
        db.Float(precision=4),
        default=None,
        doc=''
    )
    siren_id = db.Column(
        db.ForeignKey('sirens.id'),
        nullable=False,
        doc=''
    )
    system_id = db.Column(
        db.ForeignKey('siren_systems.id'),
        default=None,
        doc=''
    )
    installation_timestamp = db.Column(
        db.DateTime,
        default=None,
        doc=''
    )
    removal_timestamp = db.Column(
        db.DateTime,
        default=None,
        doc=''
    )
    # TODO: Testing Schedule, bind to the system or to the location.

    # system = db.relationship('SirenSystem')
