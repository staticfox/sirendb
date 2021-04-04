from sirendb.core.db import db


class User(db.Model):
    '''
    Describes an authenticated user account.
    '''
    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        doc=(
            'Identifies the primary key from the database.'
        )
    )
    username = db.Column(
        db.String(100),
        nullable=False,
        doc=(
            "The user's username."
        )
    )
    email = db.Column(
        db.String(100),
        nullable=False,
        doc=(
            "The user's E-Mail address."
        )
    )
    password_hash = db.Column(
        db.String(512),
        nullable=False,
        doc=(
            'Password hash'
        )
    )
    register_timestamp = db.Column(
        db.DateTime,
        nullable=False,
        doc=(
            'Identifies when the user registered their account.'
        )
    )
    email_verified_timestamp = db.Column(
        db.DateTime,
        default=None,
        doc=(
            'Identifies when the user verified their email address.'
        )
    )
