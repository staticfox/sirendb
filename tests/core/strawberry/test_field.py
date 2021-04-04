import pytest

from sirendb.core.strawberry import GraphQLField


pytest_plugins = (
    'tests.fixtures',
    'tests.core.strawberry.fixtures',
)


def test_table_one_object_is_mapped_correctly(client, introspection_graphql_query):
    response = client.post(
        '/api/v1/graphql',
        json={
            'query': introspection_graphql_query
        }
    )
    assert response.status_code == 200

    types = response.json.get('data', {}).get('__schema', {}).get('types', [])
    table_one = None
    for type_ in types:
        if type_['kind'] == 'OBJECT' and type_['name'] == 'TableOne':
            table_one = type_
            break
    assert table_one is not None
    assert table_one['description'] == "This is from TableOne's field"

    fields = {
        'directField': {
            'description': 'This was mounted directly',
            'isDeprecated': False,
            'deprecationReason': None,
            'nullable': False,
        },
        'email': {
            'description': 'This can be null though.',
            'isDeprecated': False,
            'deprecationReason': None,
            'nullable': True,
        },
    }
    field_names = [k['name'] for k in table_one['fields']]

    assert field_names == ['directField', 'email']

    for field in table_one['fields']:
        field_def = fields[field['name']]
        assert field_def['description'] == field['description']
        assert field_def['isDeprecated'] == field['isDeprecated']
        assert field_def['deprecationReason'] == field['deprecationReason']
        assert field_def['nullable'] is (field['type']['kind'] != 'NON_NULL'), f"{field['name']} {field} {field_def}"


def test_query_from_table_one(client):
    response = client.post(
        '/api/v1/graphql',
        json={
            'query': '''
query {
  getTableOne {
    directField
    email
  }
}
'''
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'getTableOne': {
                'directField': 'test 123',
                'email': 'test email',
            }
        }
    }


def test_field_base_is_subclassed_with_invalid_name():
    with pytest.raises(RuntimeError):
        class WrongSubclass(GraphQLField):
            key: str
