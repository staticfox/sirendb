pytest_plugins = (
    'tests.fixtures',
    'tests.core.strawberry.fixtures',
)


def test_pull_books_as_property(client, db):
    from .fixtures import (
        Book,
        ExampleTable,
    )

    row1 = ExampleTable(
        name='test 123',
        email='test email',
    )
    db.session.add(row1)
    db.session.commit()

    book1 = Book(name='Book1', table_id=row1.id)
    db.session.add(book1)
    db.session.commit()

    response = client.post(
        '/api/v1/test-graphql',
        json={
            'query': '''
query getAllTables($paginate: Paginate, $sort: ExampleTableSortEnum, $filter: ExampleTableFilter) {
  allTables(paginate: $paginate, sort: $sort, filter: $filter) {
    count
    pageInfo {
      hasNext
      lastCursor
    }
    items {
      directField
      id
      email
      books {
        name
      }
    }
  }
}
'''
        }
    )
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'allTables': {
                'count': 1,
                'pageInfo': {
                    'hasNext': False,
                    'lastCursor': '',
                },
                'items': [{
                    'books': [{
                        'name': 'Book1',
                    }],
                    'directField': 'this is from the resolver',
                    'email': 'test email',
                    'id': row1.id,  # TODO: global IDs
                }]
            }
        }
    }
