# syntax=docker/dockerfile:1

## Dockerfile to build a basic flask app, based on 
## https://docs.docker.com/language/python/build-images/ 

FROM python:3.9-slim-buster

COPY . . 

RUN pip install -r requirements.txt

ENV FLASK_APP=main.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=5022"]
