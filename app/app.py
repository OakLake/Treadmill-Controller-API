"""FastAPI application for control of treadmill and reading of telemetry."""

import asyncio
import random
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

store = {
    "speed": 0,
    "distance": 0,
    "time": 0,
    "calories": 0,
}


async def fetch_telemetry():
    """Get the telemetry from the treadmill."""
    global store
    while True:
        print("Fetching data...")
        store["speed"] = random.randint(100, 500)
        store["distance"] = random.randint(100, 500)
        store["time"] = random.randint(100, 500)
        store["calories"] = random.randint(100, 500)
        await asyncio.sleep(3)


# TODO: convert to lifespan event "startup" and write async polling of treadmill.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Objects available throughout app lifespan."""
    global store
    task = asyncio.create_task(fetch_telemetry())
    try:
        yield
    finally:
        task.cancel()
        await task


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/start")
async def start():
    """Start the treadmill."""
    return {"start": True}


@app.post("/puase")
async def pause():
    """Pause the treadmill."""
    return {"pause": True}


@app.post("/stop")
async def stop():
    """Stop the treadmill."""
    return {"stop": True}


@app.post("/speed")
async def set_speed(option: Literal["increase"] | Literal["decrease"]):
    """Increase/Decrease speed of treadmill by 1m/s increments."""
    value = 1 if option == "increase" else -1
    store["speed"] += value
    return {"speed": store["speed"]}


@app.websocket("/ws")
async def telemetry(*, websocket: WebSocket):
    """Websocket for passing on treadmill telemetry to clients."""
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(
                {
                    "distance": random.randint(1, 100),
                    "time": random.randint(1, 100),
                    "calories": random.randint(1, 100),
                    "speed": random.randint(1, 100),
                }
            )
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        print("Clinet disconnected")
    except Exception as e:
        print("EX: ", e)
