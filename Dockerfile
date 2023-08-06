FROM python:3.11-alpine3.18

WORKDIR /ntu-pe-ticket
COPY requirements.txt /ntu-pe-ticket
RUN pip install -r requirements.txt

COPY ./app /ntu-pe-ticket/app

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8000", "app.webhook:app"]