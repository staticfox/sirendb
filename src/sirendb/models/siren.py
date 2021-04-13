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
    # location_id = db.Column(
    #     db.Integer,
    #     db.ForeignKey('siren_locations.id'),
    #     default=None,
    # )
    active = db.Column(
        db.Boolean,
        default=None,
        doc='Whether or not the siren is active'
    )
    model = db.relationship(
        'SirenModel',
        foreign_keys=[model_id],
        uselist=False,
        doc="The model of the siren."
    )
    locations = db.relationship(
        'SirenLocation',
        # foreign_keys=[location_id],
        # uselist=False,
        doc='The geographic position of the siren.'
    )
    # address = db.relationship(
    #     'SirenAddress',
    #     foreign_keys=[address_id],
    #     uselist=False,
    #     doc='The physical address of the siren.'
    # )
