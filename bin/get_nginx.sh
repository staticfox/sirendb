#!/bin/bash

set -eu -o pipefail

cd $(dirname $0)

NGINX_VERSION="1.18.0"

if [ ! -d "nginx-${NGINX_VERSION}" ]; then
    wget "http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz";
    tar -zxvf "nginx-${NGINX_VERSION}.tar.gz";
    rm "nginx-${NGINX_VERSION}.tar.gz";
fi

cd "nginx-${NGINX_VERSION}"
PREFIX="$(cd .. && pwd)/nginx"
./configure --builddir=build --prefix=$PREFIX --with-poll_module --with-threads --with-file-aio
make install
