from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import requests
import logging
from pydantic import BaseModel
import httpx
import re
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()

app = FastAPI()

# Telex Bot API URL (replace with actual API URL)
TELEX_WEBHOOK_URL = os.getenv("TELEX_WEBHOOK_URL")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com/user/following/"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

@app.post("/webhook")
async def toggle_follow_github_user(request: Request):
    payload = await request.json()

    message = payload['message']

    pattern = r"Starred by:\s([a-zA-Z0-9_-]+)"

    # Use regex to extract the username after "Starred by: "
    match = re.search(pattern, message)

    if match:
        username = match.group(1)

        url = f"{GITHUB_API_URL}{username}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 204:
                    unfollow_response = await client.delete(url, headers=headers)
                    
                    if unfollow_response.status_code == 204:
                        return {"message": f"Successfully unfollowed {username}!"}
                    else:
                        raise HTTPException(status_code=unfollow_response.status_code, detail="Failed to unfollow user.")
                elif response.status_code == 404:
                    follow_response = await client.put(url, headers=headers)
                    
                    if follow_response.status_code == 204:
                        return {"message": f"{message}\n\nSuccessfully followed {username}!"}
                    else:
                        raise HTTPException(status_code=follow_response.status_code, detail="Failed to follow user.")
                else:
                    raise HTTPException(status_code=response.status_code, detail="Error checking follow status.")
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))


@app.get('/integration-config')
async def get_integration_config():
    data = {
  "data": {
    "date": {
      "created_at": "2025-02-20",
      "updated_at": "2025-02-20"
    },
    "descriptions": {
      "app_name": "github-star-notifier",
      "app_description": "This integration notifies my channel of a starred event on my repository",
      "app_logo": "https://www.pinterest.com/pin/883690758133210277/",
      "app_url": "https://github-star-notifier.onrender.com",
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
    "target_url": "https://github-star-notifier.onrender.com/webhook",
  }
}
    return JSONResponse(content=data)

@app.post("/github-webhook")
async def github_webhook(request: Request):
    data = await request.json()
    message = ""
    starrer_url = ""

    if data.get('action') == 'started':
        print("I am here")
        repo_name = data['repository']['name']
        starrer_name = data['sender']['login']
        starrer_url = data['sender']['html_url']

        message = f"🚀 A new star on repository: {repo_name}\n\nStarred by: {starrer_name}\nProfile: {starrer_url}"

        payload = {
            "event_name": "github-star-notification",
            "message": message,
            "status": "success",
            "username": starrer_url,
        }

        response = requests.post(
            TELEX_WEBHOOK_URL,
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if the PORT environment variable is not set
    uvicorn.run(app, host="0.0.0.0", port=port)
  