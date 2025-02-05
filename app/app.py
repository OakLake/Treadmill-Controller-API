from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import random

import asyncio

store = {
    "speed": 0,
    "distance": 0,
    "time": 0,
    "calories": 0,
}


async def fetch_telemetry():
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


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/start")
async def start():
    return {"start": True}


@app.post("/stop")
async def stop():
    return {"stop": True}


@app.post("/speed/increase")
async def set_speed():
    store["speed"] += 1
    return {"speed": store["speed"]}


@app.post("/speed/decrease")
async def set_speed():
    store["speed"] -= 1
    return {"speed": store["speed"]}


@app.websocket("/ws")
async def telemetry(*, websocket: WebSocket):
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
    except WebSocketDiconnect:
        print("Clinet disconnected")
    except Exception as e:
        print("EX: ", e)
