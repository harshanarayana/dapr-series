FROM python:3.8.3-alpine3.12 as base

# This is required to install grpc.io. Without this, the cc command won't work.
RUN apk update && apk add build-base linux-headers
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
