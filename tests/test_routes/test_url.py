import json
import re

from fastapi.testclient import TestClient
from main import app

# ToDo: Use another app and DB for testing.
# ToDo: Write more tests which include all the outcomes
client = TestClient(app)


def test_generate_url():
    data = {"original": "https://thecontentworks.uk/http-status-codes-cheat-sheet/"}
    response = client.post("/minilink/url/", json.dumps(data))

    assert response.json()["message"] == "Url generated successfully."
    assert response.json()["success"] is True
    assert re.match("^ml/+\w+", response.json()["data"]['short_url']) is not None


def test_get_url_info():
    response = client.get("/minilink/url/?hashed_url=ml/b31f77f6a4727afda4295d388d1a4568")
    url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    assert response.json()["success"] is True
    assert response.json()["message"] == "The URL info retrieved successfully."
    assert re.match(url_regex, response.json()["data"]['url_info']['original']) is not None
    assert re.match("^ml/+\w+", response.json()["data"]['url_info']['hashed']) is not None
    assert type(response.json()["data"]['url_info']['is_active']) is bool
    assert re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
                    response.json()["data"]['url_info']['created_at']) is not None
    assert type(response.json()["data"]['url_info']['statistics']) is list


def test_not_found_get_url_info():
    response = client.get("/minilink/url/?hashed_url=ml/b31f77f6a4727afda4295d388d1a2635")

    assert response.json()["success"] is False
    assert response.json()["message"] == "Requested URL does not found or has been deleted before."
    assert response.json()["error_code"] == -2
    assert type(response.json()["data"]) is dict
