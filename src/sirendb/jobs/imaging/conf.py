NGINX_CFG = '''
# user   root;
worker_processes  1;

# daemon off;
# master_process off;

#error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

#pid        logs/nginx.pid;


events {{
    worker_connections  1024;
}}


http {{
    include       mime.types;
    default_type  application/octet-stream;

    access_log off;

    sendfile        on;

    keepalive_timeout  65;

    gzip  on;

    server {{
        listen       {netloc};
        server_name  127.0.0.1;

        root {geo_build_dir};
        location / {{
            try_files $uri /index.html;
        }}
    }}
}}
'''
