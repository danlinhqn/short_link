docker network create my-network

docker run -d --name nginx --network my-network -p 80:80 nginx

docker run -d --name short-link-create-link --network my-network linhtran2023/short-link-create-link:v08

docker run -d --name trum-riviu-shop --network my-network linhtran2023/trum-riviu-shop:v02

```
docker build -t linhtran2023/short-link-create-link:v01 .
```

nano /etc/nginx/conf.d/default.conf

## Sửa lỗi khi nginx không đọc được file css
```yaml
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

# Thêm 1 domain nữa 
server {
    listen 80;
    server_name trum-riviu.realdealvn.click;

    location /create-link {
        proxy_pass http://short-link-create-link:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
