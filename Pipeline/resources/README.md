pip install git+https://github.com/mercadolibre/python-sdk.git
pip install python-dotenv
pip install --upgrade google-cloud-pubsub

3.3 minutos sin workers
En ampliar los resources y verificar los paging

40 segundos con workers
En ampliar los resources y verificar los paging

Comando para armar la imagen y pushearla a DockerHub.

docker build -t agustinnormand/resources:1 . && docker push agustinnormand/resources:1
