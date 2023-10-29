import httpx
import os
from dotenv_vault import load_dotenv

load_dotenv()


class Request:
    client = httpx.Client(base_url=os.getenv("API_URL"))

    def get(self, url, params=None):
        response = self.client.get(url, params=params)
        return response.json().get("data")

    def post(self, url, data):
        response = self.client.post(url, json=data)
        return response.json().get("data")

    def put(self, url, data=None):
        response = self.client.put(url, json=data)
        return response.json().get("data")

    def delete(self, url):
        response = self.client.delete(url)
        return response.json().get("data")


request = Request()


class Error:
    message: str


class BaseResponse:
    status: str
    error: Error


class PresidentInitRequest:
    telegramUserId: int

    def __init(self, telegram_user_id: int):
        self.telegramUserId = telegram_user_id


class PresidentInitResponse:
    url: str
    qrCode: str
