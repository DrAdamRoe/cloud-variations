import json
import unittest

from api.api import app
from api.hello_cloud import hello_cloud


class Test(unittest.TestCase):
    def test_api(self):
        with app.test_client() as test_client:

            response = test_client.get('/')

            assert response.status_code == 200

            json_data = json.loads(response.data)

            assert "message" in json_data

if __name__ == "__main__":
    unittest.main()
