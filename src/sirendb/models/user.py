from sirendb.core.db import db


class User(db.Model):
    '''
    Describes an authenticated user account.
    '''
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
