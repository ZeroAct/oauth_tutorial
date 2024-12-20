# Oauth Tutorial
<img src="https://github.com/user-attachments/assets/2b83a4f0-8a40-4f87-8a5e-d23ceec709d1" width="50%"/>

 A simple boilerplate for setting up HTTPS, Nginx, and OAuth with FastAPI and HTMX. This implementation handles OAuth through plain HTTP requests instead of using an OAuth-specific module.

support
- [google login](https://console.cloud.google.com/)
- [kakao login](https://developers.kakao.com/)
- [naver login](https://developers.naver.com/)

## index
- [1. nginx setting](#1-nginx-setting)
  * [install nginx](#install-nginx)
  * [setting](#setting)
    + [example](#example)
  * [Run](#run)
- [2. enable https](#2-enable-https)
  * [install certbot](#install-certbot)
  * [configure nginx conf (auto)](#configure-nginx-conf--auto-)
- [3. web app](#3-web-app)
  * [copy static files to authorized folder](#copy-static-files-to-authorized-folder)
  * [Run](#run-1)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

## 0. Setting Environment
```
GOOGLE_CLIENT_ID=YOUR_VALUE
GOOGLE_CLIENT_SECRET=YOUR_VALUE
GOOGLE_REDIRECT_URI=YOUR_VALUE

KAKAO_API_KEY=YOUR_VALUE
KAKAO_REDIRECT_URI=YOUR_VALUE

NAVER_CLIENT_ID=YOUR_VALUE
NAVER_CLIENT_SECRET=YOUR_VALUE
NAVER_REDIRECT_URI=YOUR_VALUE
```

## 1. nginx setting

### install nginx
```shell
sudo apt update
sudo apt install nginx -y
# /etc/nginx
```

### setting

`/etc/nginx/sites-available/` stores configuration files for individual sites.

define server block here

and

`/etc/nginx/sites-enabled/` contains symbolic links to the files in `sites-availables` for activation

```shell
sudo ln -s /etc/nginx/sites-available/yourdomain.com /etc/nginx/sites-enabled/
```

#### example
`/etc/nginx/sites-enabled/zeroact.dev`

reverse proxy

1. http 80
```
server {
    listen 80;
    server_name world.zeroact.dev;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static/ {
        alias /var/www/world.zeroact.dev/;
        autoindex on;
        allow all;
    }
}
```

2. https 443
```
server {

    server_name world.zeroact.dev;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static/ {
        alias /var/www/world.zeroact.dev/;
        autoindex on;
        allow all;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/world.zeroact.dev/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/world.zeroact.dev/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {  # Redirect 80 port to 443
    if ($host = world.zeroact.dev) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen 80;

    server_name world.zeroact.dev;
    return 404; # managed by Certbot
}
```


### Run
validate nginx config
```shell
sudo nginx -t
```

run service
```shell
sudo systemctl start nginx
```

[zeroact.dev](http://zeroact.dev)


## 2. enable https

### install certbot
```shell
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

### configure nginx conf (auto)
```shell
sudo certbot --nginx -d zeroact.dev -d app.zeroact.dev
```
this query will automatically update `/etc/nginx/sites-enabled/zeroact.dev` file.


```shell
sudo systemctl reload nginx
```

## 3. web app

### copy static files to authorized folder
```shell
sudo cp -r static/* /var/www/world.zeroact.dev/
```

### Run
```
uvicorn app:app --host 0.0.0.0
```
