import pytest
import strawberry

from sirendb.core.db import db
from sirendb.core.strawberry import (
    GraphQLField,
    GraphQLType,
)


class TableOne(db.Model):
    '''
    This is from TableOne's field
    '''
    __tablename__ = 'test_table_1'

    id = db.Column(
        db.Integer,
        primary_key=True,
        doc='Identifies the primary key from the database.',
    )
    name = db.Column(
        db.String,
        nullable=False,
        default='asdf',
        doc='This cannot be null',
    )
    email = db.Column(
        db.String,
        nullable=True,
        default=None,
        doc='This can be null though.'
    )


class TableOneNode(GraphQLType):
    class Meta:
        name = 'TableOne'
        sqlalchemy_model = TableOne
        sqlalchemy_only_fields = (
            'email',
        )

    direct_field: str = strawberry.field(
        description='This was mounted directly'
    )


class Query(GraphQLField):
    __endpoints__ = ('/api/v1/test-graphql',)

    @strawberry.field(description='OwO Whats this?')
    def get_table_one(self) -> TableOneNode:
        return TableOneNode(
            email='test email',
            direct_field='test 123',
        )


@pytest.fixture
def introspection_graphql_query():
    # From GraphiQL
    yield '''
    query IntrospectionQuery {
      __schema {
        queryType {
          name
        }
        mutationType {
          name
        }
        subscriptionType {
          name
        }
        types {
          ...FullType
        }
        directives {
          name
          description
          locations
        }
      }
    }

    fragment FullType on __Type {
      kind
      name
      description
      fields(includeDeprecated: true) {
        name
        description
        isDeprecated
        deprecationReason
        type {
          kind
        }
      }
    }
    '''
