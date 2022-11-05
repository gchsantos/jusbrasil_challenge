FROM python:3.9

RUN apt-get upgrade -y
RUN apt-get install -y git

COPY .  /app 

WORKDIR /app

RUN pip install -r requirements.txt

WORKDIR /app/jusbrasil_challenge