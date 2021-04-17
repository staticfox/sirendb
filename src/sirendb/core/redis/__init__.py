from fakeredis import FakeRedis
from redis import Redis as Redis_


class Redis:
    def __init__(self):
        self.__local = None

    def init_app(self, app):
        if app.testing:
            self.__local = FakeRedis()
        else:
            self.__local = Redis_(app.config['APP_REDIS_URL'])

    def __getattr__(self, name):
        if name in ('__init__', 'init_app'):
            return self.__dict__[name]
        elif name == '__local':
            return self.__local
        else:
            return getattr(self.__local, name)


redis = Redis()
