#!/bin/sh

docker run -d --name=ntu-pe-tickets \
    -p $PORT:8000 \
    --env-file .env \
    --restart=always \
    ntu-pe-tickets
