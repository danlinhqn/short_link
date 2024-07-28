### Chương trình chính

```yaml
docker network create my-network

# Rebuild
docker rm -f short-link-create-link
docker run -d --name short-link-create-link --network my-network linhtran2023/short-link-create-link:v19
```

-----
### Cài đặt Nginx 

```
docker run -d --name nginx --network my-network -p 80:80 nginx
docker exec -it nginx sh
nano /etc/nginx/conf.d/default.conf
```


```yaml
# Domain riviu.online ( Chấp nhận tất cả subdomain )
server {
    listen 80;
    server_name .riviu.online;
    location /create-link {
        proxy_pass http://short-link-create-link:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    
    # Sửa lỗi khi nginx không đọc được file css
    location /static/ {
        proxy_pass http://short-link-create-link:5000/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Sửa lỗi khi nginx không liên kết được folder upload
    location /uploads/ {
        proxy_pass http://short-link-create-link:5000/uploads/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Domain realdealvn.click ( Chấp nhận tất cả subdomain )
server {
    listen 80;
    server_name .realdealvn.click;

    location / {
        proxy_pass http://short-link-create-link:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        proxy_pass http://short-link-create-link:5000/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads/ {
        proxy_pass http://short-link-create-link:5000/uploads/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

```

-----
### Cài đặt Redis

```sudo nano /root/redis_data/redis.conf```

```
bind 0.0.0.0
port 6379
requirepass shortlink123456!
dir /data
dbfilename dump.rdb
appendonly yes
appendfilename "appendonly.aof"

```
```
docker run -d --name redis \
  -p 8080:6379 \
  -v /root/redis_data:/data \
  -v /root/redis_data/redis.conf:/usr/local/etc/redis/redis.conf \
  redis:latest redis-server /usr/local/etc/redis/redis.conf

```

-----
## Các lưu ý về Redis database
#### D14: Lưu các shop phụ thử 1 shop chính ( Giới hạn 1 shop chính được 10 shop phụ )

#### D15: Lưu short_link và domain & dommain đã được xác thực