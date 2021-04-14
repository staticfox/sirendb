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
        uselist=True,
        order_by='desc(SirenLocation.installation_timestamp)',
        doc=(
            'All known geographic locations of the siren. '
            'This allows you to define previous installation sites for '
            'a specific siren in order to document it moving locations. '
            'This list is sorted by SirenLocation.installationTimestamp, '
            'meaning the most recent installation location will appear first.'
        )
    )
    # address = db.relationship(
    #     'SirenAddress',
    #     foreign_keys=[address_id],
    #     uselist=False,
    #     doc='The physical address of the siren.'
    # )
