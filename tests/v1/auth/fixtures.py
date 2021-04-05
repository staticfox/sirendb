from datetime import datetime
from secrets import token_hex
from typing import NamedTuple

import pytest

from sirendb.models.user import User

pytest_plugins = (
    'tests.fixtures',
)


@pytest.fixture
def LOGIN_QUERY():
    return '''
mutation login($username: String!, $password: String!) {
  login(form: {username: $username, password: $password}) {
    ok
    message
  }
}
'''


class UserFixture(NamedTuple):
    id_: int
    username: str
    email: str
    password: str


@pytest.fixture
def user_client(app, client, db, LOGIN_QUERY):
    '''
    Creates an authenticated test user and their test client.
    '''
    client = app.test_client()

    user = User(
        username='testuser',
        email='test@sirendb.com',
        register_timestamp=datetime.utcnow(),
    )
    password = token_hex(16)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    response = client.post(
        '/api/v1/auth-graphql',
        json={
            'query': LOGIN_QUERY,
            'operationName': 'login',
            'variables': {
                'username': 'testuser',
                'password': password,
            }
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'login': {
                'ok': True,
                'message': '',
            }
        }
    }
    user_fixture = UserFixture(
        id_=user.id,
        username=user.username,
        email=user.email,
        password=password,
    )
    yield (user_fixture, client)
