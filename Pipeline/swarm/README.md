## Docker Swarm
Ojo, service en Docker Swarm es diferente a service en Kubernetes

# In instance-1:
docker swarm init

# In the other instances:
docker swarm join --token {{TOKEN}} 10.128.0.20:2377

# Listar los nodos:
docker node ls

# Deploy del stack:
docker stack deploy --compose-file docker-compose.yml stackdemo

# In Every Node
docker service create \
  --mode global \
  --publish mode=host,target=5000,published=5000 \
  --name=resources \
  agustinnormand/resources:8

docker service create \
  --mode global \
  --name=whey_protein \
  agustinnormand/whey_protein:2

docker service create \
  --replicas 1 \
  --publish published=5000,target=5000 \
  --name=personal_trainer \
  agustinnormand/personal_trainer:2

docker service create \
  --replicas 1 \
  --name=dealer \
  agustinnormand/dealer:3

# Update to new image
Va actualizando de uno en uno
docker service update --image agustinnormand/resources:6 resources

# Remove a service
docker service rm resources

## Network
docker network create \
  --driver overlay \
  --attachable \
  my-network

## Resources
Single Node
docker service create --name resources \
                        --replicas 1 \
                        --publish published=5000,target=5000 \
                        --network my-network \
                        agustinnormand/resources:9

# Para arrancar el pipeline
Conectarse a cualquier instancia y ejecutar
curl localhost:5000/start-brand-new

## Querys
docker service create --name querys \
                        --mode global \
                        --network my-network \
                        agustinnormand/querys:25

## HtmlScrapper
docker service create --name html_scrapper \
                        --mode global \
                        --network my-network \
                        agustinnormand/html_scrapper:56

## RabbitMQ
docker service create --name html_scrapper \
                        --mode global \
                        --network my-network \
                        agustinnormand/html_scrapper:48
3.9.24-management-alpine


## Analisis de logs se podría mejorar.











## Terminal Flows
#1
curl localhost:5000/start-brand-new
#2
docker service logs resources -f
#3
docker build -t agustinnormand/querys:25 .
docker push agustinnormand/querys:25
#4
docker service rm querys
docker service create --name querys \
                        --mode global \
                        --network my-network \
                        agustinnormand/querys:24
#5
docker service logs querys -f

# DELETE
## Redis

docker service create --name redis \
                        --replicas 1 \
                        --publish published=6379,target=6379 \
                        --network my-network \
                        redis


