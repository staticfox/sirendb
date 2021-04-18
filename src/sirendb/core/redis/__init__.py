from fakeredis import FakeRedis
from redis import Redis as Redis_

from sirendb.utils.lang import DelayedInstance


class Redis(DelayedInstance):
    def init_app(self, app):
        if app.testing:
            self.set_instance(FakeRedis())
        else:
            self.set_instance(Redis_(app.config['APP_REDIS_URL']))


redis = Redis()
