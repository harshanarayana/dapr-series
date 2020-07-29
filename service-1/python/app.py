from asyncio import sleep as async_sleep
from os import getenv

import grpc
import requests
from dapr.proto import api_service_v1, api_v1, common_v1
from google.protobuf.any_pb2 import Any
from sanic import Sanic
from sanic.log import logger
from sanic.request import Request
from sanic.response import json

app = Sanic(__name__)

DAPR_GRPC_PORT = getenv("DAPR_GRPC_PORT", "50001")
DAPR_HTTP_PORT = getenv("DAPR_HTTP_PORT", "3500")
STATE_KEY = getenv("STATE_KEY", "dapr-series")
STORE_NAME = getenv("STORE_NAME", "statestore")

DAPR_CLIENT = api_service_v1.DaprStub(
    grpc.insecure_channel(f"localhost:{DAPR_GRPC_PORT}")
)
DAPR_FORWARDER = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/invoke"
DAPR_PUBLISHER = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish"


def _store_state(state_value):
    logger.info(
        f"CLIENT: {DAPR_CLIENT}, STORE_NAME: {STORE_NAME}, STATE_KEY: {STATE_KEY}"
    )
    request = common_v1.StateItem(key=STATE_KEY, value=state_value.encode("utf-8"))
    state = api_v1.SaveStateRequest(store_name=STORE_NAME, states=[request])
    return DAPR_CLIENT.SaveState(state)


def _get_state():
    logger.info(
        f"CLIENT: {DAPR_CLIENT}, STORE_NAME: {STORE_NAME}, STATE_KEY: {STATE_KEY}"
    )
    request = api_v1.GetStateRequest(store_name=STORE_NAME, key=STATE_KEY)
    state = DAPR_CLIENT.GetState(request=request)
    return state.data.decode("utf-8")


def _delete_state():
    logger.info(
        f"CLIENT: {DAPR_CLIENT}, STORE_NAME: {STORE_NAME}, STATE_KEY: {STATE_KEY}"
    )
    request = api_v1.DeleteStateRequest(store_name=STORE_NAME, key=STATE_KEY)
    return DAPR_CLIENT.DeleteState(request=request)


@app.listener("after_server_start")
async def log_info(app: Sanic, loop):
    logger.info("=================================================")
    logger.info(f"DAPR_GRPC_PORT -> {DAPR_GRPC_PORT}")
    logger.info(f"DAPR_HTTP_PORT -> {DAPR_HTTP_PORT}")
    logger.info("=================================================")


@app.get("/s2/ping")
async def s2_ping(request: Request):
    d = requests.get(f"{DAPR_FORWARDER}/service-2/method/ping")
    return json({"message": d.json()})


@app.get("/ping")
async def ping(request: Request):
    return json({"message": "ping"})


@app.delete("/state")
async def delete(request: Request):
    _delete_state()
    return json({"message": "state deleted"})


@app.get("/state")
async def state(request: Request):
    return json({"state": _get_state()})


@app.post("/state")
async def save(request: Request):
    body = request.json
    _store_state(body.get("value", "TEST"))
    return json({"message": "State Stored"})


@app.post("/publish/<topic:string>")
async def publish_message(request: Request, topic: str):
    data = request.json
    requests.post(f"{DAPR_PUBLISHER}/{topic}", json={"messageType": topic, "message": data})
    return json({"message": "published"})


@app.post("/t1")
async def handle_t1(request: Request):
    d = requests.post(f"{DAPR_FORWARDER}/service-2/method/t1", json=request.json)
    _store_state(d.text)
    return json({"message": d.json()})


@app.post("/t2")
async def handle_t2(request: Request):
    await async_sleep(10)
    logger.info(request.json)
    return json({"success": True})


@app.get("/dapr/subscribe")
async def subscribe(request: Request):
    return json([{"topic": "t1", "route": "t1"}, {"topic": "t2", "route": "t2"}])


if __name__ == "__main__":
    app.run(port=6060, debug=True)
