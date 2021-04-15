import base64
import logging
import os
import signal
import subprocess
import time

# from rq import get_current_job

# from sirendb.core.redis import redis

from .conf import NGINX_CFG

log = logging.getLogger('sirendb.imaging.nginx')


def _get_port_for_geo_job() -> int:
    # job = get_current_job()
    # if job:
    #     job_id = job.id
    # else:
    #     job_id = '0'

    for portno in range(22000, 32000):
        # FIXME: this is only needed if an instance of this app
        #        is running more than once on a machine.
        #
        #        RQ in itself does not thread jobs, but more than
        #        once instance of a worker may run at the same time
        #        on any given machine.
        #
        #        I don't want to commit to redis right now since the
        #        project is intended to be run in a cluster.
        #
        # key = f'sirendb-dev:geoserverport:{portno}'
        # if not redis.set(key, job_id, nx=True, ex=30):
        #     continue
        return portno


class Nginx:
    def __init__(self, bin_dir: str, geo_dir: str):
        self._port = None
        self._proc = None
        self._nginx_conf = None
        self._geo_build_dir = geo_dir
        self._nginx_prefix = bin_dir + '/nginx'
        self._bind_host = os.environ.get('NGINX_HOST', '127.0.0.1')

    def _write_config(self) -> None:
        log.debug(f'writing temporary nginx configration file {self.filename}...')
        with open(self._nginx_conf, 'w') as fp:
            fp.write(NGINX_CFG.format(
                portno=self._port,
                geo_build_dir=self._geo_build_dir,
                netloc=self.netloc,
            ))

    def _remove_config(self) -> None:
        log.debug(f'removing temporary nginx configration file {self.filename}...')
        os.remove(self._nginx_conf)

    @property
    def netloc(self) -> str:
        return f'{self._bind_host}:{self._port}'

    @property
    def filename(self) -> str:
        parts = self._nginx_conf.split('/conf/nginx-')
        return 'nginx-' + parts[-1]

    def __enter__(self) -> str:
        self._port = _get_port_for_geo_job()

        self._nginx_conf = '{prefix}/conf/nginx-{netloc}.conf'.format(
            prefix=self._nginx_prefix,
            netloc=base64.b64encode(self.netloc.encode('utf-8')).decode('utf-8'),
        )
        self._write_config()

        log.debug(f'starting nginx on {self.netloc}...')
        nginx_bin = f'{self._nginx_prefix}/sbin/nginx'

        self._proc = subprocess.Popen([
            nginx_bin,
            '-g', 'daemon off;',
            '-c', self._nginx_conf
        ], shell=False)

        return self.netloc

    def __exit__(self, *args, **kwargs) -> None:
        if self._proc is None:
            return

        os.kill(self._proc.pid, signal.SIGTERM)

        # FIXME this can get stuck when SIGINT is sent cuz its not propaged
        if self._proc.poll():
            log.debug('waiting for process to exit...')
            time.sleep(3)

            try:
                os.kill(self._proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

        self._remove_config()
