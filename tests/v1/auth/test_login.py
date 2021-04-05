from datetime import datetime
from secrets import token_hex

from sirendb.models.user import User

pytest_plugins = (
    'tests.fixtures',
)

VIEWER_QUERY = '''
query getMe {
  viewer {
    username
    email
  }
}
'''

LOGOUT_QUERY = '''
mutation logout {
  logout {
    ok
    message
  }
}
'''


def test_basic_login(client, db, LOGIN_QUERY):
    response = client.post(
        '/api/v1/graphql',
        json={'query': VIEWER_QUERY}
    )
    assert response.status_code == 401
    assert response.json is None

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

    response = client.post(
        '/api/v1/graphql',
        json={'query': VIEWER_QUERY}
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'viewer': {
                'username': 'testuser',
                'email': 'test@sirendb.com',
            }
        }
    }

    response = client.get(
        '/api/v1/auth-graphql',
        json={'query': LOGOUT_QUERY}
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'logout': {
                'ok': True,
                'message': '',
            }
        }
    }

    response = client.post(
        '/api/v1/graphql',
        json={'query': VIEWER_QUERY}
    )
    assert response.status_code == 401
    assert response.json is None
