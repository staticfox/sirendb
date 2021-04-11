from sirendb.core.db import db


class SirenModel(db.Model):
    '''
    Describes a model for a given siren.
    '''
    __tablename__ = 'siren_models'

    id = db.Column(
        db.Integer,
        primary_key=True,
        doc=(
            'Identifies the primary key from the database.'
        )
    )
    name = db.Column(
        db.String(80),
        nullable=False,
        doc='The name of the manufacturer.',
    )
    start_of_production = db.Column(
        db.DateTime,
        default=None,
        doc='Timestamp when the model started production.'
    )
    end_of_production = db.Column(
        db.DateTime,
        default=None,
        doc='Timestamp when the model went out of production.'
    )
    info = db.Column(
        db.Text,
        default=None,
        doc='Additional information about the model.'
    )
    revision = db.Column(
        db.Text,
        default=None,
        doc="The models's specific revision."
    )
