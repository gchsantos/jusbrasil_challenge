FROM python:3.9-alpine

COPY .  /app 

WORKDIR /app

RUN pip install -r requirements.txt

WORKDIR /app/jusbrasil_challenge