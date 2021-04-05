from werkzeug.security import generate_password_hash

from sirendb.core.auth import login_manager
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

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        # TODO: Check email verification status, suspended, banned, etc
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
