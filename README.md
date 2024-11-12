# oauth_tutorial

- [oauth_tutorial](#oauth-tutorial)
  * [1. nginx setting](#1-nginx-setting)
    + [install nginx](#install-nginx)
    + [setting](#setting)
      - [example](#example)
    + [Run](#run)
  * [2. enable https](#2-enable-https)
    + [install certbot](#install-certbot)
    + [configure nginx conf (auto)](#configure-nginx-conf--auto-)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>


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

1. 80 port to `/var/www/something`
```
server {
    listen 80;
    server_name zeroact.dev;

    root /var/www/something;
    index index.html index.htm;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

2. 80 port to localhost service `http://localhost:8000` (reverse proxy)
```
server {
    listen 80;
    server_name app.zeroact.dev;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
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