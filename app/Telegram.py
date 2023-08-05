import requests as req
import logging


class Telegram:
    def __init__(self, token) -> None:
        self.token = token
        self.endpoint = f"https://api.telegram.org/bot{token}"

    def setWebhook(self, url):
        endpoint = f"{self.endpoint}/setWebhook"
        data = {"url": url}
        res = req.post(endpoint, data=data)

        if res.status_code == 200:
            logging.info(res.json)
        else:
            raise Exception("Failed to set webhook. Check credentials.", res.json)

    def sendMessage(self, chat_id: int, text):
        endpoint = f"{self.endpoint}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        res = req.post(endpoint, data=data)

        if res.status_code == 200:
            logging.info(res.json)
        else:
            logging.error(res.json)

    def sendPhoto(self, chat_id: int, photo, caption: str = ""):
        endpoint = f"{self.endpoint}/sendPhoto"
        data = {"chat_id": chat_id, "caption": caption}
        files = {"photo": photo}
        res = req.post(endpoint, files=files, data=data)

        if res.status_code == 200:
            logging.info(res.json)
        else:
            logging.error(res.json)
