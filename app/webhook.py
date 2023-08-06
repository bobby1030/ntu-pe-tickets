from flask import Flask, request
from dotenv import load_dotenv
import io
import os
import time
import logging

from .NTUSSO import NTUSSO
from .RentPE import RentPE
from .Telegram import Telegram

load_dotenv()

TELEGRAM = Telegram(os.environ["TGBOTKEY"])
WHITELIST = [int(id) for id in os.environ["TGID"].split(",")]

# Set webhook URL
HOST = os.environ["WEBHOOK_HOST"]
TELEGRAM.setWebhook(f"{HOST}/webhook")

# create login session
NTUID = os.environ["NTUID"]
NTUPASSWORD = os.environ["NTUPASSWORD"]
SSO = NTUSSO(NTUID, NTUPASSWORD)
RENT = RentPE(SSO)

app = Flask(__name__)
starttime = time.time()


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"]
    logging.info(f"[RECEIVED] {chat_id}: {text}")

    # check if message is outdated (> 1 min before server start time)
    if update["message"]["date"] - starttime < -60:
        logging.warning("Outdated message received. Ignored.")
        return "OK"
    else:
        pass

    # check if sender is in whitelist
    if chat_id in WHITELIST:
        # check if sender is asking for tickets
        if text == "/ticket":
            try:
                TELEGRAM.sendMessage(chat_id, "Fetching tickets...")

                fetch_start = time.time()
                # login to rent.pe.ntu.edu.tw
                if RENT.login() == True:
                    TELEGRAM.sendMessage(
                        chat_id, "Suceessfully login to rent.pe.ntu.edu.tw!"
                    )

                    tickets = RENT.get_tickets()

                    # send all ticket types to user
                    for ticket in tickets:
                        infos = "\n".join(ticket.infos)
                        descriptions = f"[{ticket.facility}] {ticket.type} \n {infos}"

                        TELEGRAM.sendMessage(chat_id, descriptions)

                        # write QR code to buffer and send to user
                        with io.BytesIO() as img_buffer:
                            qr_segno = ticket.get_qr_img()
                            qr_segno.save(img_buffer, kind="png", scale=10)
                            TELEGRAM.sendPhoto(
                                chat_id, img_buffer.getvalue(), ticket.sn
                            )

                    fetch_end = time.time()
                    logging.info(f"Fetched tickets in {fetch_end - fetch_start} seconds.")
            except Exception as e:
                logging.error(e)
                TELEGRAM.sendMessage(chat_id, "Sorry, something went wrong.")
    else:
        TELEGRAM.sendMessage(chat_id, "Sorry, you are not allowed to use this bot.")

    return "OK"


if __name__ == "__main__":
    port = os.environ["WEBHOOK_PORT"]
    app.run(port=port, debug=True)
elif "gunicorn" in os.environ.get("SERVER_SOFTWARE"):
    # run by gunicorn
    gunicorn_logger = logging.getLogger("gunicorn.error")

    # assign gunicorn logger to Flask and root logger
    app.logger.handlers = gunicorn_logger.handlers  # Flask logger
    app.logger.setLevel(gunicorn_logger.level)
    logging.root.handlers = gunicorn_logger.handlers  # root logger
    logging.root.setLevel(gunicorn_logger.level)
