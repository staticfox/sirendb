from datetime import datetime

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


def test_basic_login(client, db):
    response = client.post(
        '/api/v1/graphql',
        json={ 'query': VIEWER_QUERY }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'viewer': None
        }
    }

    user = User(
        username='testuser',
        email='test@sirendb.com',
        register_timestamp=datetime.utcnow(),
    )
    user.set_password('v9fg4anu4VFDGa4a!')
    db.session.add(user)
    db.session.commit()

    response = client.post(
        '/api/v1/login',
        data={
            'username': 'testuser',
            'password': 'v9fg4anu4VFDGa4a!',
        }
    )
    assert response.status_code == 200
    assert response.json == { 'ok': True }

    response = client.post(
        '/api/v1/graphql',
        json={ 'query': VIEWER_QUERY }
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

    response = client.get('/api/v1/logout')
    assert response.status_code == 200
    assert response.json == { 'ok': True }

    response = client.post(
        '/api/v1/graphql',
        json={ 'query': VIEWER_QUERY }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'viewer': None
        }
    }
