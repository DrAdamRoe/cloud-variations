from flask import Flask, request

from api.hello_cloud import hello_cloud


app = Flask(__name__)

@app.route('/')
def index():
    return hello_cloud(request)


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
