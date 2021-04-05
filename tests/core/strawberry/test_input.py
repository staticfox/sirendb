import pytest
import strawberry

from sirendb.core.strawberry import (
    GraphQLField,
    GraphQLType,
)


pytest_plugins = (
    'tests.fixtures',
    'tests.core.strawberry.fixtures',
)

# @strawberry.input(description="This is the input's description.")
class Input(GraphQLType):
    '''
    This is the input's description.
    '''
    __typename__ = 'ExampleInput'
    __isinput__ = True

    username: str = strawberry.field(
        description='This is a required username.'
    )


class Output(GraphQLType):
    '''
    This is an example payload.
    '''
    __typename__ = 'ExamplePayload'

    ok: bool = strawberry.field(
        description='Test argument.'
    )
    message: str = strawberry.field(
        description='The input value.'
    )


class Mutation(GraphQLField):
    __endpoints__ = ('/api/v1/test-graphql',)

    @strawberry.field(description='This is example mutation.')
    def run_example_mutation(self, form: Input) -> Output:
        return Output(ok=True, message=form.username)


def test_input_object_has_correct_attributes(client, introspection_graphql_query):
    response = client.post(
        '/api/v1/test-graphql',
        json={
            'query': introspection_graphql_query
        }
    )
    assert response.status_code == 200

    types = response.json.get('data', {}).get('__schema', {}).get('types', [])
    example_input = None

    missing_objects = {
        'ExampleInput',
        'ExamplePayload',
    }
    object_attributes = {
        'INPUT_OBJECT': {
            'ExampleInput': {
                'description': "This is the input's description.",
                'fields': None,
                # 'fields': [{
                #     'name': 'username',
                #     'description': 'This is a required username.',
                #     'isDeprecated': False,
                #     'deprecationReason': None,
                #     'type': {
                #         'kind': 'NON_NULL'
                #     }
                # }],
            }
        },
        'OBJECT': {
            'ExamplePayload': {
                'description': 'This is an example payload.',
                'fields': [{
                    'name': 'message',
                    'description': 'The input value.',
                    'isDeprecated': False,
                    'deprecationReason': None,
                    'type': {
                        'kind': 'NON_NULL'
                    }
                }, {
                    'name': 'ok',
                    'description': 'Test argument.',
                    'isDeprecated': False,
                    'deprecationReason': None,
                    'type': {
                        'kind': 'NON_NULL'
                    }
                }],
            }
        }
    }

    for type_ in types:
        if type_['kind'] not in object_attributes:
            continue
        gql_object = object_attributes[type_['kind']].get(type_['name'])
        if not gql_object:
            continue
        # print(type_)
        assert type_['description'] == gql_object['description']
        assert type_['fields'] ==  gql_object['fields']
        missing_objects.remove(type_['name'])
    assert not missing_objects


def test_example_mutation_works(client):
    response = client.post(
        '/api/v1/test-graphql',
        json={
            'query': '''
mutation {
  runExampleMutation(form: {username: "testuser"}) {
    ok
    message
  }
}
'''
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'runExampleMutation': {
                'message': 'testuser',
                'ok': True,
            }
        }
    }
