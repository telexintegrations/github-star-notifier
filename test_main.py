import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch
import httpx
import re
import os

from main import app

client = TestClient(app)

GITHUB_API_URL = "https://api.github.com/user/following/"
headers = {
    "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
    "Accept": "application/vnd.github.v3+json"
}


def test_toggle_follow_github_user():
    test_payload = {
        "message": "Starred by: example_user"
    }
    
    with patch("httpx.AsyncClient.get") as mock_get, patch("httpx.AsyncClient.put") as mock_put, patch("httpx.AsyncClient.delete") as mock_delete:
        mock_get.return_value.status_code = 404
        mock_put.return_value.status_code = 204 
        
        response = client.post("/webhook", json=test_payload)
        
        assert response.status_code == 200
        assert response.json() == {"message": "Successfully followed example_user!"}

def test_integration_config():
    response = client.get('/integration.json')
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "date": {
                "created_at": "2025-02-20",
                "updated_at": "2025-02-20"
            },
            "descriptions": {
                "app_name": "github-star-notifier",
                "app_description": "This integration notifies my channel of a starred event on my repository",
                "app_logo": "https://www.pinterest.com/pin/883690758133210277/",
                "app_url": "https://p7hr5wrm-8000.uks1.devtunnels.ms",
                "background_color": "#fff"
            },
            "is_active": True,
            "integration_type": "modifier",
            "integration_category": "Task Automation",
            "key_features": [
                "real time notification"
            ],
            "author": "Graeyy",
            "settings": [
                {
                    "label": "event_type",
                    "type": "dropdown",
                    "required": True,
                    "default": "unstarred",
                    "options": [
                        "starred",
                        "unstarred"
                    ]
                }
            ],
            "target_url": "https://p7hr5wrm-8000.uks1.devtunnels.ms/webhook",
        }
    }