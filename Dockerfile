# syntax=docker/dockerfile:1

## Dockerfile to build a basic flask app, based on 
## https://docs.docker.com/language/python/build-images/ 

FROM python:3.10-slim-bullseye

COPY . . 

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=5022"]
