import time
import os
import logging
import json
import requests
import sseclient
import uuid

logger = logging.getLogger(__name__)

def login_check(endp, tok):
    logger.info("Trying to login...")
    username = None
    try:
      response = requests.get(
          f"{endp}/auth/check",
          json={},
          headers={"Authorization": f"Bearer {tok}"},
      )
      response.raise_for_status()
      username = response.json()
    except:
      pass

    return username

def refresh_token(endp, atok, rtok):
    logger.info("Refreshing login token...")
    new_tok = None
    try:
      response = requests.get(
          f"{endp}/auth/refresh",
          json={},
          headers={
              "Refresh": f"{rtok}"
              },
      )
      response.raise_for_status()
      new_tok = response.json()
    except:
      raise
    logger.info("New token is %s"%str(new_tok))

    return new_tok

class APIClient:
    def __init__(self, backend_url, http_client=requests):
        self.backend_url = backend_url
        self.http_client = http_client
        self.auth_headers = None
        self.message_id = None

    def login(self, tokens):
        print(tokens)
        atok = tokens["access_token"]["access_token"] + "e"
        rtok = tokens["refresh_token"]["access_token"]
        self.auth_headers = {"Authorization": f"Bearer {atok}"}
        username = login_check(self.backend_url, atok)
        if username is None:
          atok = refresh_token(self.backend_url, atok, rtok)
          if atok:
            username = login_check(self.backend_url, atok)

        logger.info(f"Logged in as {username}")


    def continue_chat(self, chat_id):
        self.chat_id = chat_id
        return self.chat_id

    def create_chat(self):
        response = self.http_client.post(
            f"{self.backend_url}/chats",
            json={},
            headers=self.auth_headers,
        )
        response.raise_for_status()
        self.chat_id = response.json()["id"]
        self.message_id = None
        return self.chat_id

    def get_available_models(self):
        response = self.http_client.get(
            f"{self.backend_url}/configs/model_configs",
            headers=self.auth_headers,
        )
        response.raise_for_status()
        return [model["name"] for model in response.json()]
    
    def get_available_workflows(self):
        response = self.http_client.get(
            f"{self.backend_url}/configs/workflow_configs",
            headers=self.auth_headers,
        )
        response.raise_for_status()
        return [model["name"] for model in response.json()]

    def send_message(self, message, model_config_name, collection=None):
        response = self.http_client.post(
            f"{self.backend_url}/chats/{self.chat_id}/prompter_message",
            json={
                "parent_id": self.message_id,
                "content": message,
                "collection": collection
            },
            headers=self.auth_headers,
        )
        response.raise_for_status()
        prompter_message_id = response.json()["id"]

        response = self.http_client.post(
            f"{self.backend_url}/chats/{self.chat_id}/assistant_message",
            json={
                "parent_id": prompter_message_id,
                "model_config_name": model_config_name,
                "sampling_parameters": {
                    "top_p": 0.95,
                    "top_k": 50,
                    "repetition_penalty": 1.2,
                    "temperature": 1.0,
                },
            },
            headers=self.auth_headers,
        )
        response.raise_for_status()
        self.message_id = response.json()["id"]

        response = self.http_client.get(
            f"{self.backend_url}/chats/{self.chat_id}/messages/{self.message_id}/events",
            stream=True,
            headers={
                "Accept": "text/event-stream",
                **self.auth_headers,
            },
        )
        response.raise_for_status()
        if response.status_code == 204:
            response = self.http_client.get(
                f"{self.backend_url}/chats/{self.chat_id}/messages/{self.message_id}",
                headers=self.auth_headers,
            )
            response.raise_for_status()
            data = response.json()
            yield data["content"]
        else:
            client = sseclient.SSEClient(response)
            events = iter(client.events())
            for event in events:
                if event.event == "error":
                    raise RuntimeError(event.data)
                if event.event == "ping":
                    continue
                try:
                    data = json.loads(event.data)
                except json.JSONDecodeError:
                    raise RuntimeError(f"Failed to decode {event.data=}")
                event_type = data["event_type"]
                if event_type == "token":
                    yield data["text"]
                elif event_type == "message":
                    # full message content, can be ignored here
                    break
                elif event_type == "error":
                    raise RuntimeError(data["error"])
                elif event_type == "pending":
                    logger.debug(f"Message pending. {data=}")


