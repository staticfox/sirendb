from redis import (
    ConnectionPool,
    Redis as _Redis,
)


class Redis(_Redis):
    def __init__(self, *args, **kwargs):
        if args or kwargs:
            super().__init__(*args, **kwargs)

    def init_app(self, app):
        super().__init__(
            connection_pool=ConnectionPool.from_url(
                url=app.config['APP_REDIS_URL']
            )
        )


# redis = Redis()
