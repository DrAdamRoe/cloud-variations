from fastapi import FastAPI

from api.hello_cloud import hello_cloud

app = FastAPI()

@app.get('/')
def index():
    return hello_cloud()