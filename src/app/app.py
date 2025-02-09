"""FastAPI application for control of treadmill and reading of telemetry."""

import asyncio
from contextlib import asynccontextmanager

from bleak import BleakClient, BleakError
from fastapi import Body, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src import workouts
from src.treadmill.controller import TreadmillController
from src.treadmill.secret import TREADMILL_ADDR

treadmill_controller = ...


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Objects available throughout app lifespan."""
    global treadmill_controller

    treadmill_address = TREADMILL_ADDR
    data_point_uuid = "00002acd-0000-1000-8000-00805f9b34fb"
    control_point_uuid = "00002ad9-0000-1000-8000-00805f9b34fb"

    app.state.telemetry_queue = asyncio.Queue()
    app.state.height = None

    client = BleakClient(treadmill_address)
    try:
        await client.connect()
        treadmill_controller = TreadmillController(
            client, control_point_uuid, data_point_uuid, app.state.telemetry_queue
        )
    except BleakError as e:
        print(f"\rCould not connect: {e}")

    print("HERE")
    task = asyncio.create_task(treadmill_controller.subscribe())
    print("THERE")
    try:
        yield
    finally:
        task.cancel()
        await task
        treadmill_controller.stop_event.is_set()
        await client.stop_notify(data_point_uuid)
        await client.disconnect()


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
    await treadmill_controller.start()
    return {"start": True}


@app.post("/resume")
async def resume():
    """Pause the treadmill."""
    treadmill_controller.stop_event.clear()
    return {"pause": True}


class BioMetrics(BaseModel):
    height_cm: int

@app.post("/bio-metrics")
async def set_bio_metrics(bio_metrics: BioMetrics):
    """Pause the treadmill."""
    app.state.height = bio_metrics.height_cm


@app.post("/stop")
async def stop():
    """Stop the treadmill."""
    await treadmill_controller.stop()
    return {"stop": True}


@app.get("/workouts")
async def get_workouts():
    return [
        {
            "name": workouts.easy_30min_slow.name,
            "plan": workouts.easy_30min_slow.to_json(),
        },
        {
            "name": workouts.easy_40min_slow.name,
            "plan": workouts.easy_40min_slow.to_json(),
        },
    ]


class WorkoutBody(BaseModel):
    name: str


@app.post("/start-workout")
async def start_workout(workout: WorkoutBody):
    print(workout)
    print(f"Commanded to start workout: '{workout.name}'")
    intervals = workouts.register[workout.name].intervals
    asyncio.create_task(treadmill_controller.start_workout(intervals))


@app.post("/speed")
async def set_speed(value: float):
    """Increase/Decrease speed of treadmill by 1m/s increments."""
    await treadmill_controller.set_speed(value)
    return {"speed": value}


@app.websocket("/ws")
async def telemetry(*, websocket: WebSocket):
    """Websocket for passing on treadmill telemetry to clients."""
    await websocket.accept()
    queue = app.state.telemetry_queue  # Get shared queue

    try:
        while True:
            data = await queue.get()
            if app.state.height is not None:
                steps = int(int(data["distance_m"]) / (int(app.state.height) / 100 * 0.415) )
                data["steps"] = steps
            else:
                data["steps"] = 0
            await websocket.send_json(data)
    except WebSocketDisconnect:
        print("Clinet disconnected")
    except Exception as e:
        print("EX: ", e)
