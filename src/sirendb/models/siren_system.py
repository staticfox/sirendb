from sqlalchemy.sql import func

from sirendb.core.db import db


class SirenSystem(db.Model):
    '''
    Describes a collection of sirens that are managed by a local government or agency.
    '''
    __tablename__ = 'siren_systems'

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
        db.String(100),
        nullable=False,
        doc=(
            'The name of the system.'
        )
    )
    start_of_service_timestamp = db.Column(
        db.DateTime,
        default=None,
        doc=(
            'Relative timestamp when the system was put in to service.'
        )
    )
    end_of_service_timestamp = db.Column(
        db.DateTime,
        default=None,
        doc=(
            'Relative timestamp when the system was decommissioned.'
        )
    )
    in_service = db.Column(
        db.Boolean,
        default=None,
        doc=(
            'Whether or not the system is currently in service. '
            'If endOfServiceTimestamp is set, then this field is '
            'automatically populated. Otherwise, this field may be '
            'set in the event that endOfServiceTimestamp is unknown.'
        )
    )
    city = db.Column(
        db.String(50),
        default=None,
        doc=(
            'Name of the city that the system is designated for.'
        )
    )
    county = db.Column(
        db.String(50),
        default=None,
        doc=(
            'Name of the county that the system is designated for.'
        )
    )
    state = db.Column(
        db.String(50),
        default=None,
        doc=(
            'Name of the state that the system is designated for.'
        )
    )
    country = db.Column(
        db.String(50),
        default=None,
        doc=(
            'Name of the country that the system is designated for.'
        )
    )
    postal_code = db.Column(
        db.String(20),
        default=None,
        doc=(
            'Postal code that the system is designated for.'
        )
    )
    siren_wiki_url = db.Column(
        db.String(100),
        default=None,
        doc=(
            "The URL to the system's wiki.airraidsirens.net entry."
        )
    )
    locations = db.relationship(
        'SirenLocation',
        uselist=True,
        order_by='desc(SirenLocation.installation_timestamp)',
        doc=(
            'Associated siren locations within this system.'
            'This list is sorted by SirenLocation.installationTimestamp, '
            'meaning the most recent installation locations will appear first.'
        )
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
