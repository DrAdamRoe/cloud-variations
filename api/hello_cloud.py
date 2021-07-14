from flask import jsonify

def hello_cloud(request):
    data = {"message": "Hello, Cloud!"}
    return jsonify(data)
