from flask import Flask, request
from decouple import config
import io
import time
import logging

from .NTUSSO import NTUSSO
from .RentPE import RentPE
from .Telegram import Telegram

telegram = Telegram(config("TGBOTKEY"))
whitelist = config(
    "TGID", cast=lambda ids: [int(id) for id in ids.split(",")]
)  # cast to list of int

# Set webhook URL
host = config("WEBHOOK_HOST")
telegram.setWebhook(f"{host}/webhook")

# create login session
NTUID = config("NTUID")
NTUPASSWORD = config("NTUPASSWORD")
SSO = NTUSSO(NTUID, NTUPASSWORD)
rent = RentPE(SSO)

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
    if chat_id in whitelist:
        # check if sender is asking for tickets
        if text == "/ticket":
            try:
                telegram.sendMessage(chat_id, "Fetching tickets...")

                fetch_start = time.time()
                # login to rent.pe.ntu.edu.tw
                if rent.login() == True:
                    telegram.sendMessage(
                        chat_id, "Suceessfully login to rent.pe.ntu.edu.tw!"
                    )

                    tickets = rent.get_tickets()

                    # send all ticket types to user
                    for ticket in tickets:
                        infos = "\n".join(ticket.infos)
                        descriptions = f"[{ticket.facility}] {ticket.type} \n {infos}"

                        telegram.sendMessage(chat_id, descriptions)

                        # write QR code to buffer and send to user
                        with io.BytesIO() as img_buffer:
                            qr_segno = ticket.get_qr_img()
                            qr_segno.save(img_buffer, kind="png", scale=10)
                            telegram.sendPhoto(
                                chat_id, img_buffer.getvalue(), ticket.sn
                            )

                    fetch_end = time.time()
                    logging.info(f"Fetched tickets in {fetch_end - fetch_start} seconds.")
            except Exception as e:
                logging.error(e)
                telegram.sendMessage(chat_id, "Sorry, something went wrong.")
    else:
        telegram.sendMessage(chat_id, "Sorry, you are not allowed to use this bot.")

    return "OK"


# run dev server if directly run this file
if __name__ == "__main__":
    port = config("WEBHOOK_PORT")
    app.run(port=port, debug=True)
