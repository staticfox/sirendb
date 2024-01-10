from fakeredis import FakeRedis
from redis import Redis as Redis_

from sirendb.utils.lang import DelayedInstance


class Redis(DelayedInstance):
    def init_app(self, app):
        redis_url = app.config.get('APP_REDIS_URL')
        if app.testing or not redis_url:
            self.set_instance(FakeRedis())
        else:
            self.set_instance(Redis_.from_url(app.config['APP_REDIS_URL']))


redis = Redis()
