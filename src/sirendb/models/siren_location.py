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
    satellite_latitude = db.Column(
        DOUBLE_PRECISION,
        default=None,
        doc="The location's satellite view latitude."
    )
    satellite_longitude = db.Column(
        DOUBLE_PRECISION,
        default=None,
        doc="The location's satellite view longitude."
    )
    satellite_zoom = db.Column(
        DOUBLE_PRECISION,
        default=None,
        doc="The location's satellite view zoom."
    )
    street_latitude = db.Column(
        DOUBLE_PRECISION,
        default=None,
        doc="The location's street view latitude."
    )
    street_longitude = db.Column(
        DOUBLE_PRECISION,
        default=None,
        doc="The location's street view longitude."
    )
    street_heading = db.Column(
        DOUBLE_PRECISION,
        default=None,
        doc="The location's street view heading."
    )
    street_pitch = db.Column(
        db.Float(precision=4),
        default=None,
        doc="The location's street view pitch."
    )
    street_zoom = db.Column(
        db.Float(precision=4),
        default=None,
        doc="The location's street view zoom."
    )
    siren_id = db.Column(
        db.ForeignKey('sirens.id'),
        nullable=False,
        doc="Identifies the siren's primary key from the database."
    )
    system_id = db.Column(
        db.ForeignKey('siren_systems.id'),
        default=None,
        doc="Identifies the system's primary key from the database."
    )
    installation_timestamp = db.Column(
        db.DateTime,
        default=None,
        doc='Timestamp indicating when the siren was installed at this location.'
    )
    removal_timestamp = db.Column(
        db.DateTime,
        default=None,
        doc='Timestamp indicating when the siren was removed from this location.'
    )
    # TODO: Testing Schedule, bind to the system or to the location.

    siren = db.relationship(
        'Siren',
        foreign_keys=[siren_id],
        uselist=False,
        back_populates='locations',
        doc='The siren at this location.',
    )
    system = db.relationship(
        'SirenSystem',
        foreign_keys=[system_id],
        uselist=False,
        back_populates='locations',
        doc='The system that this location is a part of.'
    )
