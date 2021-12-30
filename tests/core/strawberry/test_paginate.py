pytest_plugins = (
    'tests.fixtures',
    'tests.core.strawberry.fixtures',
)


def test_query_from_table_one(client, db):
    from .fixtures import ExampleTable

    row1 = ExampleTable(
        name='test 123',
        email='test email',
    )
    db.session.add(row1)
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
                    'lastCursor': '1',
                },
                'items': [{
                    'directField': 'this is from the resolver',
                    'id': 1,
                    'email': 'test email',
                }]
            }
        }
    }
