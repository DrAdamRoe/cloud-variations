# syntax=docker/dockerfile:1

## Dockerfile to build a basic flask app, based on https://docs.docker.com/language/python/

FROM python:3.11.7-slim-bullseye

COPY . . 

RUN pip install -r requirements.txt

ENV FLASK_APP=main.py

CMD ["flask", "run", "--host=0.0.0.0", "--port=5022"]
