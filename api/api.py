from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
@app.route('/api/meetings/all', methods=['GET'])
def index():
    data = {"message":"Hello, Cloud!"}
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
