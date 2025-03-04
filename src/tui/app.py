"""Terminal UI App."""

import asyncio
from datetime import timedelta
from decimal import Decimal, getcontext

from bleak import BleakClient
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Grid, HorizontalGroup, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Digits, Footer, Header, Label, Static

from src.treadmill.controller import TreadmillController
from src.treadmill.secret import TREADMILL_ADDR, USER_HEIGHT

getcontext().prec = 2


class SpeedDisplay(Digits):
    """A widget to display the treadmill speed."""


class DurationDisplay(Digits):
    """A widget to display the treadmill duration."""


class CaloriesDisplay(Digits):
    """A widget to display the treadmill calories."""


class DistanceDisplay(Digits):
    """A widget to display the treadmill distance."""


class StepsDisplay(Digits):
    """A widget to display the treadmill steps."""


class TreadmillUpdate(Message):
    """Custom message to update UI with treadmill telemetry."""

    def __init__(self, data):
        """Init the message."""
        super().__init__()
        self.data = data


class TreadMillApp(App):
    """A Textual App to manage FTMS enabled treadmill."""

    CSS_PATH = "treadmill.tcss"
    BINDINGS = []

    def __init__(
        self, treadmill_controller: TreadmillController, telemetry_queue: asyncio.Queue
    ):
        """Init the TUI app."""
        super().__init__()
        self.queue = telemetry_queue
        self.controller = treadmill_controller
        self.speed = 0

    def compose(self) -> ComposeResult:
        """Compose the widgets."""
        yield Header()
        yield Footer()
        yield VerticalScroll(
            Grid(
                Static("TREADMILL CONTROL", classes="title"),
                HorizontalGroup(
                    Button("Stop", id="stop", variant="error"),
                    Button("Start", id="start", variant="success"),
                    classes="button-group",
                ),
                HorizontalGroup(
                    Button("-", id="dec_speed", variant="error"),
                    Button("+", id="inc_speed", variant="success"),
                    classes="button-group",
                ),
                Static("Telemetry", classes="section-title"),
                Grid(
                    HorizontalGroup(Label("⚡ Speed"), SpeedDisplay("00.0")),
                    HorizontalGroup(Label("⏳ Duration"), DurationDisplay("00:00:00")),
                    HorizontalGroup(Label("📏 Distance"), DistanceDisplay("0000")),
                    HorizontalGroup(Label("🔥 Calories"), CaloriesDisplay("000")),
                    HorizontalGroup(Label("👣 Steps"), StepsDisplay("0000")),
                    classes="telemetry",
                ),
                classes="main-grid",
            )
        )

    @on(Button.Pressed, "#start")
    async def start_treadmill(self):
        """Start treadmill button handler."""
        await self.controller.start()

    @on(Button.Pressed, "#stop")
    async def stop_treadmill(self):
        """Stop treadmill button handler."""
        await self.controller.stop()

    @on(Button.Pressed, "#inc_speed")
    async def increase_speed_treadmill(self):
        """Increase treadmill speed button handler."""
        await self.controller.set_speed(self.speed + Decimal(0.1))

    @on(Button.Pressed, "#dec_speed")
    async def decrease_speed_treadmill(self):
        """Dencrease treadmill speed button handler."""
        await self.controller.set_speed(self.speed - Decimal(0.1))

    async def stream_telemetry(self):
        """Stream telemetry from treadmill."""
        while True:
            data_raw = await self.queue.get()

            self.speed = Decimal(data_raw["speed"])

            data = {
                "speed": f"{data_raw["speed"]:05.2f}",
                "distance": f"{data_raw["distance"]:04d}",
                "calories": f"{data_raw["calories"]:04d}",
                "duration": str(timedelta(seconds=data_raw["time"])),
                "steps": str(
                    int(int(data_raw["distance"]) / (int(USER_HEIGHT) / 100 * 0.415))
                ),
            }

            self.post_message(TreadmillUpdate(data))

    async def on_mount(self):
        """Start the worker task."""
        self.run_worker(self.stream_telemetry(), exclusive=True)

    async def on_treadmill_update(self, event: TreadmillUpdate):
        """Handle treadmill UI update for updated telemetry."""
        data = event.data
        self.query_one(SpeedDisplay).update(data["speed"])
        self.query_one(DurationDisplay).update(data["duration"])
        self.query_one(DistanceDisplay).update(data["distance"])
        self.query_one(CaloriesDisplay).update(data["calories"])
        self.query_one(StepsDisplay).update(data["steps"])


async def run():
    """Run the TUI."""
    print("Started Run")
    data_point_uuid = "00002acd-0000-1000-8000-00805f9b34fb"
    control_point_uuid = "00002ad9-0000-1000-8000-00805f9b34fb"
    telemetry_queue = asyncio.Queue(maxsize=5)

    async with BleakClient(TREADMILL_ADDR) as client:
        print("Connected")

        treadmill_controller = TreadmillController(
            client, control_point_uuid, data_point_uuid, telemetry_queue
        )
        task = asyncio.create_task(treadmill_controller.subscribe())

        app = TreadMillApp(treadmill_controller, telemetry_queue)
        await app.run_async()

    task.cancel()
    await task
    # treadmill_controller.stop_event.is_set()
    # await client.stop_notify(data_point_uuid)


if __name__ == "__main__":
    asyncio.run(run())
