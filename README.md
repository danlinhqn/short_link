docker network create my-network

docker run -d --name nginx --network my-network -p 80:80 nginx

docker run -d --name short-link-create-link --network my-network linhtran2023/short-link-create-link:v02

```
docker build -t linhtran2023/short-link-create-link:v01 .
```