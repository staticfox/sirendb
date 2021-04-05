from flask_login import login_required
from strawberry import Schema
from strawberry.flask.views import GraphQLView

from .field import SchemaFieldRegistry


class GraphQLSchema(Schema):
    @classmethod
    def init_app(cls, app):
        auth_required_endpoints = app.config.get('AUTH_REQUIRED_ENDPOINTS', (
            '/api/v1/graphql'
        ))
        for endpoint, schema_kwargs in SchemaFieldRegistry.schema_for_endpoint():
            schema = cls(**schema_kwargs)
            view_name = endpoint.replace('/', '_') + '_view'

            view_func = GraphQLView.as_view(view_name, schema=schema)
            if endpoint in auth_required_endpoints:
                view_func = login_required(view_func)

            app.add_url_rule(endpoint, view_func=view_func)
