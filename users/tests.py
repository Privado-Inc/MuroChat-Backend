import json
from django.test import TestCase
from rest_framework.test import APIClient

class SimpleTest(TestCase):
    def setUp(self):
        self.client = APIClient()


    def test_hello_world(self):
        response = self.client.post(
            "/u/login",
            json.dumps(
                { "username": "Hello, World!" }
            ),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"username": "Hello, World!"})
