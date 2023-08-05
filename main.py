from decouple import config
import logging
import os

from app.webhook import app

if __name__ == "__main__":
    # check debug mode
    DEBUG = os.environ.get("DEBUG", "0")
    if DEBUG == "1":
        DEBUG = True
        logging.basicConfig(
            filename="debug.log",
            filemode="a",
            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
            level=logging.DEBUG,
            force=True,
        )
    else:
        DEBUG = False
        logging.basicConfig(
            filename="main.log",
            filemode="a",
            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
            level=logging.INFO,
            force=True,
        )

    port = config("WEBHOOK_PORT")
    app.run(port=port, debug=DEBUG, use_reloader=False)
