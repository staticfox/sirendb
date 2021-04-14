from sirendb.core.db import db


class SirenSystem(db.Model):
    '''
    Describes a collection of sirens that are managed by a local government or agency.
    '''
    __tablename__ = 'siren_systems'

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
