# API Interceptor
Flask app to intercept API calls and do a little bit more 

## Nginx proxy

For the interception to be caught properly, an Nginx proxy server needs to be set up for redirecting the http requests. 
Here is an example config file, which listens on 443 port for https requests, directs the intercepted API calls to port 5000 and others to 9100.
The actual Nginx configuration file used on the instances is also included in this repo.

```
server {
    listen       443;
    server_name  localhost;

    client_body_buffer_size 10M;
    client_header_buffer_size 1K;
    client_max_body_size 0;

    ssl_certificate /etc/nginx/cert.crt;
    ssl_certificate_key /etc/nginx/cert.key;

    ssl on;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    ssl_ciphers EECDH+ECDSA+AESGCM:EECDH+aRSA+AESGCM:EECDH+ECDSA+SHA512:EECDH+ECDSA+SHA384:EECDH+ECDSA+SHA256:ECDH+AESGCM:ECDH+AES256:DH+AESGCM:DH+AES256:RSA+AESGCM:!aNULL:!eNULL:!LOW:!RC4:!3DES:!MD5:!EXP:!PSK:!SRP:!DSS;

    location / {
        proxy_set_header Host $host;
        proxy_pass http://localhost:9100;
        proxy_read_timeout 90;
    }

    location ~ /api/dedup/clusters/(.*) {

      proxy_set_header        Host $host;
      proxy_set_header        X-Real-IP $remote_addr;
      proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header        X-Forwarded-Proto $scheme;

      # Fix the “It appears that your reverse proxy set up is broken" error.
      proxy_pass          http://localhost:5000;
      proxy_redirect      http://localhost:5000 https://localhost:443;
      proxy_read_timeout  90;
    }

    #error_page  404              /404.html;

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
```

## System service for flask app
To set up a system service entry for the flask app to be run automatically on start up, add the following two files 
under /etc/systemd/system (assuming Ubuntu 16.04), after changing the relevant path accordingly.

interceptor.service: 
```
[Unit]
Description=Gunicorn instance to serve Interceptor
After=network.target

[Service]
Type=simple
User=ubuntu
Group=www-data
WorkingDirectory=/<path-to>/api-interceptor
Environment="PATH=/<path-to>/api-interceptor/venv/bin"
ExecStart=/bin/bash /etc/systemd/system/iterceptor.startup

[Install]
WantedBy=multi-user.target
```

interceptor.startup:
```sh
cd /<path-to>/api-interceptor/
source /<path-to>/api-interceptor/setup.sh
/<path-to>/api-interceptor/venv/bin/gunicorn --bind 127.0.0.1:5000 wsgi
```

To start the service, run the following from command line:
```sh
sudo systemctl daemon-reload 
sudo service interceptor restart
```
To enable the service for automatic startup: 
```sh
sudo systemctl enable interceptor
```
