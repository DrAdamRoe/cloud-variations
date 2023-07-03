from fastapi.testclient import TestClient

from api.api import app

test_client = TestClient(app)

def test_api_response():
    response = test_client.get('/')
    assert response.status_code == 200
    assert "message" in response.json()