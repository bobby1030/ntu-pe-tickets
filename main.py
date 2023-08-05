from decouple import config

from app.webhook import app

if __name__ == "__main__":
    port = config("WEBHOOK_PORT")
    app.run(port=port)
