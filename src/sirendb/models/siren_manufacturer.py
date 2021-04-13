from sirendb.core.db import db


class SirenManufacturer(db.Model):
    '''
    Describes a manufacturer for a given siren.
    '''
    __tablename__ = 'siren_manufacturers'

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
        db.String(80),
        nullable=False,
        doc='The name of the manufacturer.',
    )
    founded_timestamp = db.Column(
        db.DateTime,
        default=None,
        doc='Timestamp when the company was founded.'
    )
    defunct_timestamp = db.Column(
        db.DateTime,
        default=None,
        doc='Timestamp when the company went out of business.'
    )
    info = db.Column(
        db.Text,
        default=None,
        doc='Additional information about the manufacturer.'
    )
