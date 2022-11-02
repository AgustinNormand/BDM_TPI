gcloud auth login

export GOOGLE_APPLICATION_CREDENTIALS='/home/agustin/Downloads/cryptic-opus-335323-22f0fa15a4a0.json'

Comando para armar la imagen y pushearla a DockerHub.

docker build -t agustinnormand/htmlscrapper:25 . && docker push agustinnormand/htmlscrapper:25
