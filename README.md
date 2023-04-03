

# 运行 gunicorn
同时会自动启动 uvicorn, deploy/gunicorn.py配置的监听端口是 8000

我们的python代码是用 `from . import XXX` 相对路径的方式导入当前文件夹下的其它文件, 在这种情况下, 必须将当前目录切换到 fastapi_db 的**上一级目录**来运行。

所以下面这个命令要在 `chat_smallapp_chatgpt` 这个目录下执行
```bash
gunicorn fastapi_db.main:app -c ./fastapi_db/deploy/gunicorn.py
```
如果是开放调测阶段，用下面这个更合适
```bash
uvicorn fastapi_db.main:app --reload 
```
gunicorn没有对应的停止命令， 只能通过 `ps aux | grep gun` 找到进程ID再手动 `kill`掉


# 停止nginx
```bash
nginx -s stop
```

# 运行 nginx

### 1、 把deplay/nginx.conf链接到nginx配置文件所在的默认地址
**提醒：**  nginx.conf 一定要放在nginx的配置文件所在的默认地址

`sudo nginx -t` 可以查看 **nginx.conf** 默认所在的地址

```bash
rm /etc/nginx/nginx.conf -rf  
sudo ln -s $(pwd)/fastapi_db/deploy/nginx.conf  /etc/nginx/nginx.conf
```

### 2、把https的ssl证书拷贝到 nginx的默认配置文件地址下
[nginx的ssl证书配置教程](https://blog.csdn.net/finally_vince/article/details/127884546)

```bash
cp -r ./aliyun_free_cert_chat.ouj.com_nginx /etc/nginx/
nginx -t      #测试配置文件是否正确
```

### 3、运行
```bash
nginx   
```