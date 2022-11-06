FROM python:3.9

COPY .  /app 

WORKDIR /app

RUN pip install -r requirements.txt

WORKDIR /app/jusbrasil_challenge

RUN chmod +x start-server.sh