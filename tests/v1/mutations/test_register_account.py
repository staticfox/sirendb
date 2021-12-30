pytest_plugins = (
    'tests.fixtures',
)


CREATE_QUERY = '''
mutation makeAccount($username: String!, $email: String!, $password: String!) {
  registerAccount(form: {
    username: $username,
    email: $email,
    password: $password,
  }) {
    ok
    message
    user {
      email
      emailVerifiedTimestamp
      username
    }
  }
}
'''


def test_example_mutation_works(client, db):
    response = client.post(
        '/api/v1/auth-graphql',
        json={
            'query': CREATE_QUERY,
            'operationName': 'makeAccount',
            'variables': {
                'username': 'testuser',
                'email': 'test@sirendb.com',
                'password': 'p@ssw04D',
            }
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'registerAccount': {
                'ok': True,
                'message': 'Please verify your email address to log in.',
                'user': {
                    'email': 'test@sirendb.com',
                    'emailVerifiedTimestamp': None,
                    'username': 'testuser',
                },
            }
        }
    }
