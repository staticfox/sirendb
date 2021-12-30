import base64
import logging
import os
import socket
import subprocess
import time
from typing import Optional

from flask import current_app

from .conf import NGINX_CFG

log = logging.getLogger('sirendb.imaging.nginx')


class Socket(socket.socket):
    pass


class Popen(subprocess.Popen):
    pass


class Nginx:
    def __init__(self, bin_dir: str, geo_dir: str):
        self._port = -1
        self._proc: Optional[Popen] = None
        self._nginx_conf = ''
        self._geo_build_dir = geo_dir
        self._nginx_install_dir = bin_dir + '/nginx'
        self._bind_host = os.environ.get('NGINX_HOST', '127.0.0.1')

    @property
    def netloc(self) -> str:
        return f'{self._bind_host}:{self._port}'

    def _wait_until_booted(self) -> bool:
        started_at = time.time()

        # Give nginx 3 seconds to start
        last_msg = 0.0
        result = -1
        while True:
            now = time.time()

            if now - started_at > 3:
                log.error('unable to connect to nginx: %s' % os.strerror(result))
                self._stop_nginx()
                return False

            with Socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex((self._bind_host, self._port))
                if now - last_msg > 1 and result != 0:
                    log.debug('_wait_until_booted waiting... %d' % result)
                    last_msg = now

                if result == 0:
                    log.debug('_wait_until_booted started in %ld seconds' % (now - started_at))
                    return True

    def _stop_nginx(self):
        self._proc.terminate()

        # FIXME this can get stuck when SIGINT is sent cuz its not propagated
        started_at = time.time()
        while time.time() - started_at < 3:
            if not self._proc.poll():
                return

            if current_app.testing:
                break

        log.debug('nginx failed to stop in time, killing')

        try:
            self._proc.kill()
        except ProcessLookupError:
            pass

        self._remove_config()

    def _start_nginx(self, port: int) -> str:
        '''
        Binds nginx to the given port then starts the httpd

        :return: network location of the nginx endpoint
        :rtype: str
        '''
        upper_port_limit = 32000
        lower_port_limit = 22000

        # self._port = _get_available_port()
        assert port >= lower_port_limit and port <= upper_port_limit
        self._port = port

        self._nginx_conf = '{prefix}/conf/nginx-{netloc}.conf'.format(
            prefix=self._nginx_install_dir,
            netloc=base64.b64encode(self.netloc.encode('utf-8')).decode('utf-8'),
        )
        self._write_config()

        log.debug(f'starting nginx on {self.netloc}...')
        nginx_exe = f'{self._nginx_install_dir}/sbin/nginx'

        args = [nginx_exe, '-g', 'daemon off;', '-c', self._nginx_conf]
        self._proc = Popen(args, shell=False)

        if not self._wait_until_booted():
            if port + 1 > upper_port_limit:
                port = lower_port_limit
            return self._start_nginx(port + 1)

        return self.netloc

    def _write_config(self) -> None:  # pragma: nocover
        log.debug(f'writing temporary nginx configration file {self._config_filename}...')
        with open(self._nginx_conf, 'w') as fp:
            fp.write(NGINX_CFG.format(
                portno=self._port,
                geo_build_dir=self._geo_build_dir,
                netloc=self.netloc,
            ))

    def _remove_config(self) -> None:  # pragma: nocover
        log.debug(f'removing temporary nginx configration file {self._config_filename}...')
        os.remove(self._nginx_conf)

    @property
    def _config_filename(self) -> str:  # pragma: nocover
        parts = self._nginx_conf.split('/conf/nginx-')
        return 'nginx-' + parts[-1]

    def __enter__(self) -> Optional[str]:
        return self._start_nginx(port=22000)

    def __exit__(self, *args, **kwargs) -> None:
        if self._proc is None:
            return

        self._stop_nginx()
