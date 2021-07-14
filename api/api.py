from flask import Flask, request

from api.hello_cloud import hello_cloud


app = Flask(__name__)

@app.route('/')
@app.route('/api/meetings/all', methods=['GET'])
def index():
    return hello_cloud(request)


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
