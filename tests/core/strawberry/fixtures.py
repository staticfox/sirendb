from typing import Any, Optional

import pytest
import strawberry

from sirendb.core.db import db
from sirendb.core.strawberry import (
    GraphQLField,
    GraphQLType,
)
from sirendb.core.strawberry.field import SortingEnum
from sirendb.core.strawberry.paginate import Paginate, paginated_field


class Book(db.Model):
    '''
    This describes a book.
    '''
    __tablename__ = 'test_book_1'

    id = db.Column(
        db.Integer,
        primary_key=True,
        doc='Identifies the primary key from the database.',
    )
    name = db.Column(
        db.String,
        nullable=False,
        doc='This is a book name.',
    )
    table_id = db.Column(
        db.Integer,
        db.ForeignKey('test_table_1.id'),
        nullable=False,
    )


class ExampleTable(db.Model):
    '''
    This is from ExampleTable's field
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
    books = db.relationship(
        'Book',
        uselist=True,
        doc='List of books that belong to this table.',
    )


class ExampleTableNode(GraphQLType):
    class Meta:
        name = 'ExampleTable'
        sqlalchemy_model = ExampleTable
        sqlalchemy_only_fields = (
            'id',
            'email',
            # 'books',
        )

    direct_field: str = strawberry.field(
        description='This was mounted directly'
    )

    @staticmethod
    def resolve_direct_field(row, *args, **kwargs):
        return 'this is from the resolver'


class Query(GraphQLField):
    __endpoints__ = ('/api/v1/test-graphql',)

    @strawberry.field(description='OwO Whats this?')
    def get_table_one(self) -> ExampleTableNode:
        return ExampleTableNode(
            id=1,
            email='test email',
            direct_field='test 123',
        )

    @paginated_field(node=ExampleTableNode)
    def all_tables(
        self,
        # Custom search
        # geolocation: Optional[Tuple[float, float]],

        # Provided by paginated_field
        paginate: Optional[Paginate] = None,
        sort: Optional[SortingEnum] = None,
        filter: Optional[Any] = None,
    ):
        '''
        Return all tables.
        '''
        return ExampleTable.query


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
