docker network create my-network

docker run -d --name nginx --network my-network -p 80:80 nginx

docker run -d --name short-link-create-link --network my-network linhtran2023/short-link-create-link:v06

docker run -d --name trum-riviu-shop --network my-network linhtran2023/trum-riviu-shop:v02

```
docker build -t linhtran2023/short-link-create-link:v01 .
```

docker exec -it nginx sh
nano /etc/nginx/conf.d/default.conf

## Sửa lỗi khi nginx không đọc được file css

```yaml
# Domain realdealvn.click
server {
    
    listen 80;
    server_name realdealvn.click;
    location /create-link {
        proxy_pass http://short-link-create-link:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Khai báo thư mục tĩnh ở đây
    location /static/ {
        proxy_pass http://short-link-create-link:5000/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Khai báo thư mục tĩnh ở đây
    location /uploads/ {
        proxy_pass http://short-link-create-link:5000/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Domain review-phim.realdealvn.click
server {
    listen 80;
    server_name review-phim.realdealvn.click;

    location / {
        proxy_pass http://short-link-create-link:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Domain review-phim.realdealvn.click
server {
    listen 80;
    server_name tin-hot.realdealvn.click;

    location / {
        proxy_pass http://short-link-create-link:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
}
```

-----

sudo nano /root/redis_data/redis.conf

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