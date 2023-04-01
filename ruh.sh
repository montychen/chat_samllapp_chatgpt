#!/bin/bash

# 同时会自动启动 uvicorn
# gunicorn.py配置的监听端口是 8000
gunicorn fastapi_db.main:app -c ./fastapi_db/deploy/gunicorn.py

# 先停止nginx
nginx -s stop

# 把deplay/nginx.conf配置文件，链接到nginx默认的地址
rm /etc/nginx/nginx.conf -rf  
sudo ln -s $(pwd)/fastapi_db/deploy/nginx.conf  /etc/nginx/nginx.conf
nginx -t      #测试配置文件是否正确
nginx   