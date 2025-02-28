import asyncio

from bleak import BleakClient
from textual import on
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Digits, Footer, Header, Label

from src.treadmill.controller import TreadmillController
from src.treadmill.secret import TREADMILL_ADDR


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


class TreadMillApp(App):
    """A Textual App to manage FTMS enabled treadmill."""

    BINDINGS = []

    def __init__(
        self, treadmill_controller: TreadmillController, telemetry_queue: asyncio.Queue
    ):
        super().__init__()
        self.q = telemetry_queue
        self.controller = treadmill_controller

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield VerticalScroll(
            HorizontalGroup(
                Button("Stop", id="stop", variant="error"),
                Button("Start", id="start", variant="success"),
            ),
            HorizontalGroup(
                Button("-", id="dec_speed", variant="error"),
                Button("+", id="inc_speed", variant="success"),
            ),
            HorizontalGroup(Label("Duratinon"), DurationDisplay("00:00:00")),
            HorizontalGroup(Label("Speed"), SpeedDisplay("Speed")),
            HorizontalGroup(Label("Calories"), CaloriesDisplay("000")),
            HorizontalGroup(Label("Distance"), DistanceDisplay("0000")),
            HorizontalGroup(Label("Steps"), StepsDisplay("0000")),
        )

    @on(Button.Pressed, "#start")
    async def start_treadmill(self):
        await self.controller.start()

    @on(Button.Pressed, "#stop")
    async def stop_treadmill(self):
        await self.controller.stop()

    @on(Button.Pressed, "#inc_speed")
    async def increase_speed_treadmill(self):
        await self.controller.set_speed(2)

    @on(Button.Pressed, "#dec_speed")
    async def decrease_speed_treadmill(self):
        await self.controller.set_speed(1)


async def run():
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
