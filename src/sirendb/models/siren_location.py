from __future__ import annotations

from typing import (
    NamedTuple,
    Optional,
)

from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.sql import func

from sirendb.core.db import db


class SirenLocation(db.Model):
    '''
    Describes a specific siren location.
    '''
    __tablename__ = 'siren_locations'

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
        doc='Timestamp when this entry was created.'
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
        doc='Timestamp when this entry was last updated.'
    )
    updated_by_id = db.Column(
        db.ForeignKey('users.id'),
        default=None,
        doc='id of the last user who updated this entry.'
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
    media = db.relationship(
        'SirenMedia',
        uselist=True,
        back_populates='location',
        doc='media associated with this location.',
    )
    created_by = db.relationship(
        'User',
        foreign_keys=[created_by_id],
        uselist=False,
        doc='The user who created this entry.',
    )
    updated_by = db.relationship(
        'User',
        foreign_keys=[updated_by_id],
        uselist=False,
        doc='The user who last updated this entry.',
    )

    @property
    def satellite_coordinates(self) -> Optional[SatelliteCoordinates]:
        if self.satellite_latitude and self.satellite_longitude and self.satellite_zoom:
            return SatelliteCoordinates(
                latitude=self.satellite_latitude,
                longitude=self.satellite_longitude,
                zoom=self.satellite_zoom,
            )
        else:
            return None

    @property
    def street_coordinates(self) -> Optional[StreetCoordinates]:
        if (
            self.street_latitude and
            self.street_longitude and
            self.street_heading and
            self.street_pitch and
            self.street_zoom
        ):
            return StreetCoordinates(
                latitude=self.street_latitude,
                longitude=self.street_longitude,
                heading=self.street_heading,
                pitch=self.street_pitch,
                zoom=self.street_zoom,
            )
        else:
            return None


class SatelliteCoordinates(NamedTuple):
    latitude: float
    longitude: float
    zoom: float


class StreetCoordinates(NamedTuple):
    latitude: float
    longitude: float
    heading: float
    pitch: float
    zoom: float
